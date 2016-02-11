#! /usr/bin/python3

import os
import time
import smtplib

import config

#----------------------------------------------------------------------

# INIT
if os.getuid() != 0:
    print( "[ERR] Root-Rechte benoetigt!" )
    print( "      Versuch 'sudo python3 sw.py'")
    exit( 1 )

# END INIT

#----------------------------------------------------------------------

# VARIABLES
d = config.readConfig() # <- Dictionary with the config data as follows:

ftpDir      = d[ "ftpDir" ]
mailingList = d[ "mailinglist" ]
minSpcAvail = int( d[ "min" ] ) # In Bytes ( 5.000.000B = 5Mb )
unit        = d[ "unit" ]
messaging   = d[ "messaging" ]
mailtime    = int( d[ "mailtime" ] )

logFile = open( ftpDir + "SpcWtch/mesg.txt", "a" )

WEEK            = 336 # One week = 336 half hours
availableSpace  = True
spcAvail        = 0
avg             = 0
cycles          = 0
statData        = ""
messageTemp     = "SpaceWatch: Reached minimum value of free space!\n" \
                  "Available space: %s" + unit + ".\n\n" \
                  "Only %d pictures can be taken."
statMessageTemp = "SpaceWatch: %s stats\n" \
                  "Here are your stats:\n" \
                  "%s\n\n"
subjectNorm     = "SpaceWatch: No space available"
subjectFreq     = "SpaceWatch: Stats"

# END VARIABLES

#----------------------------------------------------------------------

# FUNCTIONS
def sendEmail( message, subject ):
    login = "XXXX"
    password = "XXXX"
    smtpserver = "smtp.gmail.com:587"
    mailer = "SpaceWatch"
    mailinList = ",".join( mailingList )

    header  = "From: %s\n" % mailer
    header += "To: %s\n" % mailingList
    header += "Subject: %s\n\n" % subject
    message = header + message

    server = smtplib.SMTP( smtpserver )
    server.starttls()
    server.login( login, password )
    server.sendmail( mailer, mailingList, message )
    server.quit()

# In Bytes
def getSpcAvail():
    stfs = os.statvfs( "/" )
    free = stfs.f_bavail * stfs.f_frsize
    return free

# In Bytes
def getAvgFileSize():
    dirs = os.listdir( ftpDir )
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
    log( "Total data size: %f%s." % (toKi( totalSize ), unit) )
    log( "Pictures taken: %d." % totalCount )
    log( "Pictures per day: %d." % (totalCount / dirCount) )

    return totalSize / totalCount

def toKi( byte ):
    if unit == "K":
        return byte / 1024
    else:
        return byte / 1000

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
    log( "Starting." )
    print( "Starting." )
    while availableSpace:
        log( "..............New cycle.............." )
        cycles += 1
        actHour = int( time.strftime( "%H" ) )

        # Critical
        spcAvail = getSpcAvail()
        avg = getAvgFileSize()
        log( "Cycle number: %d" % cycles )
        log( "Free disk space: %f%s." % (toKi( spcAvail ), unit) )
        log( "New average picture size: %f%s." % (toKi( avg ), unit) )
        log( "Pictures could be taken: %d." % (spcAvail / avg) )
        # Critical

        if( spcAvail < minSpcAvail ):
            # Drive is going to have no available space / Send email
            log( "No space available anymore." )
            availableSpace = False
            message = messageTemp % ( toKi( spcAvail ), (spcAvail / avg) )
            sendEmail( message, subjectNorm )
            log( "Email sent." )

            log( "Exiting normal." )
            log( "-------------------------------------" )
            logFile.close()
            exit( 0 )

        if messaging == "d" and actHour >= mailtime and actHour < (mailtime + 1):
            message = statMessageTemp % ("Daily", statData )
            sendEmail( message, subjectFreq )
        if messaging == "w" and cycles == WEEK:
            message = statMessageTemp % ("Weekly", statData)
            sendEmail( message, subjectFreq )

        time.sleep( 30 * 60 ) # Sleep half an hour
        statData = ""
except KeyboardInterrupt:
    print( "\n" )
    log( "Received KeyboardInterrupt. Exiting." )
    log( "-------------------------------------" ) 
    logFile.close()
    exit( 0 )

# END MAIN
