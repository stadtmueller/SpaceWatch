#! /usr/bin/python3

import os
import re
import time
import smtplib

import config

#----------------------------------------------------------------------

# INIT
if os.getuid() != 0:
    print( "[ERR] Need root privileges!" )
    print( "      Try 'sudo python3 /usr/local/SpcWtch/sw.py'")
    exit( 1 )

# END INIT

#----------------------------------------------------------------------

# VARIABLES
d = config.readConfig() # <- Dictionary with the config data as follows:

ftpDir        = d[ "ftpDir" ]
mailingList   = d[ "mailinglist" ]
minSpcAvail   = int( d[ "min" ] ) # In Bytes ( 5.000.000B = 5Mb )
unit          = d[ "unit" ]
messaging     = d[ "messaging" ]
mailday       = d[ "mailday" ]
mailtime      = int( d[ "mailtime" ] )
loginName     = d[ "loginName" ]
loginPassword = d[ "loginPassword" ]

logFile = open( ftpDir + "SpcWtch/mesg.txt", "a" )

pid = str( os.getpid() )

availableSpace  = True
spcAvail        = 0
avg             = 0
cycles          = 0
statData        = ""
messageTemp     = "SpaceWatch: Reached minimum value of free space!\n" \
                  "Available space: %s.\n\n" \
                  "Only %d pictures can be taken."
statMessageTemp = "SpaceWatch: %s stats\n" \
                  "Here are your stats:\n" \
                  "%s\n\n"
subjectNorm     = "SpaceWatch: No space available"
subjectStat     = "SpaceWatch: Stats"

# END VARIABLES

#----------------------------------------------------------------------

# FUNCTIONS
def sendEmail( message, subject ):
    smtpserver = "smtp.gmail.com:587"
    mailer = "SpaceWatch"
    mailinList = ",".join( mailingList )

    header  = "From: %s\n" % mailer
    header += "To: %s\n" % mailingList
    header += "Subject: %s\n\n" % subject
    message = header + message

    try:
        server = smtplib.SMTP( smtpserver )
        server.starttls()
        server.login( loginName, loginPassword )
        server.sendmail( mailer, mailingList, message )
        server.quit()
    except smtplib.SMTPAuthenticationError:
        log( "Wrong login data. Can not send any mails." )

# In Bytes
def getSpcAvail():
    stfs = os.statvfs( "/" )
    free = stfs.f_bavail * stfs.f_frsize
    return free

# In Bytes
def getAvgFileSize():
    dirCount = 0
    totalSize = 0
    totalCount = 0

    for directory in os.listdir( ftpDir ):
        if directory != "SpcWtch":
            dirCount += 1

    for root, dirs, files in os.walk( ftpDir ):
        for filename in files:
            if filename != "mesg.txt":
                totalCount += 1
                totalSize += os.path.getsize( os.path.join( root, filename ) )

    log( "Days uploading: %d." % dirCount )
    log( "Total data size: %s." % convert( totalSize ) )
    log( "Daily throughput: %s." % convert( totalSize / dirCount ) )
    log( "Pictures taken: %d." % totalCount )
    log( "Pictures per day: %d." % (totalCount / dirCount) )

    return totalSize / totalCount

def convert( byte, digitsOnly=False ):
    byte = float( byte )

    if byte == 0:
        return 0

    conv = 0

    if unit == "K":
        conv = str( byte / 1024 ) + unit
    elif unit == "kB":
        conv = str( byte / 1000 ) + unit
    elif unit == "M":
        conv = str( byte / 1024 / 1024 ) + unit
    elif unit == "mB":
        conv = str( byte / 1000 / 1000 ) + unit
    elif unit == "G":
        conv = str( byte / 1024 / 1024 / 1024 ) + unit
    elif unit == "gB":
        conv = str( byte / 1000 / 1000 / 1000 ) + unit
    else:
        log( "Unknown unit. Going on with K." )
        conv = str( byte / 1024 ) + "K"

    if( digitsOnly ):
        return int( re.sub( "[^0-9]", "", conv ) )

    return conv

def log( msg ):
    global statData
    actTime = time.strftime( "%d.%m.%Y @ %H:%M:%S: " )
    msg = actTime + msg + "\n"
    logFile.write( msg )
    logFile.flush()

    statData += msg

# END FUNCTIONS

#----------------------------------------------------------------------

# MAIN
try:
    log( "Starting with PID: " + pid )
    print( "Starting with PID: " + pid )
    while availableSpace:
        log( "..............New cycle.............." )
        cycles += 1
        actHour = int( time.strftime( "%H" ) )
        actDay  = int( time.strftime( "%w" ) )

        spcAvail = getSpcAvail()
        avg = getAvgFileSize()
        log( "Cycle number: %d" % cycles )
        log( "Free disk space: %s." % convert( spcAvail ) )
        log( "New average picture size: %s." % convert( avg ) )
        log( "Pictures could be taken: %d." % (spcAvail / avg) )

        if( spcAvail < minSpcAvail ):
            # Drive is going to have no available space / Send email
            log( "No space available anymore." )
            availableSpace = False
            message = messageTemp % ( convert( spcAvail ), (spcAvail / avg) )
            sendEmail( message, subjectNorm )
            log( "Email sent." )

            log( "Exiting normal." )
            log( "-------------------------------------" )
            logFile.close()
            exit( 0 )

        if messaging == "d" and actHour >= mailtime and actHour < (mailtime + 1):
            message = statMessageTemp % ("Daily", statData )
            sendEmail( message, subjectStat )
        if messaging == "w" and actDay == mailday and actHour >= mailtime and acthour < (mailtime + 1):
            message = statMessageTemp % ("Weekly", statData)
            sendEmail( message, subjectStat )

        time.sleep( 1800 ) # Sleep half an hour
        statData = ""
except KeyboardInterrupt:
    print( "\n" )
    log( "Received KeyboardInterrupt. Exiting." )
    log( "-------------------------------------" )
    logFile.close()
    exit( 0 )

# END MAIN
