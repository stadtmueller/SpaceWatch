# !!!   !!!   !!!   !!!   !!! #
# This is a testing file! Do  #
# not use this unless you     #
# have to!                    #
# !!!   !!!   !!!   !!!   !!! #

#! /usr/bin/python3

import os
import time
import smtplib

import config

#----------------------------------------------------------------------


specialLogFile = open( "/usr/local/SpcWtch/specialLog.log", "a" )
def specialLog( msg ):
    print( msg, end = "", flush = True )
    specialLogFile.write( msg )
    specialLogFile.flush()

# INIT

specialLog( "Init..." )

if os.getuid() != 0:
    print( "[ERR] Root-Rechte benoetigt!" )
    print( "      Versuch 'sudo python3 sw.py'")
    exit( 1 )

specialLog( "Done. \n" )

# END INIT

#----------------------------------------------------------------------

# VARIABLES

specialLog( "Setting variables..." )

d = config.readConfig() # <- Dictionary with the config data as follows:

ftpDir      = d[ "ftpDir" ]
mailingList = d[ "mailinglist" ]
minSpcAvail = int( d[ "min" ] ) # In Bytes ( 5.000.000B = 5Mb )
unit        = d[ "unit" ]
messaging   = d[ "messaging" ]

logFile = open( ftpDir + "SpcWtch/mesg.txt", "a" )

WEEK            = 336 # One week = 336 half hours
DAY             = 46  # One day = 46 half hours
availableSpace  = True
spcAvail        = 0
avg             = 0
cycles          = 0
statData        = ""
messageTemp     = "Raspberry Pi FTP-Server: Reached minimum value of free space!\n" \
                  "Available space: %s" + unit + ".\n\n" \
                  "Only %d pictures can be taken."
statMessageTemp = "Raspberry Pi FTP-Server: %s stats\n" \
                  "Here are your stats:\n" \
                  "%s\n\n"
subjectNorm     = "Raspberry Pi FTP-Server: No space available"
subjectFreq     = "Raspberry Pi FTP-Server: Stats"

specialLog( "Done \n" )

# END VARIABLES

#----------------------------------------------------------------------

# FUNCTIONS
def sendEmail( message, subject ):
    specialLog( "Sending email..." )
    login = "XXXX"
    password = "XXXX"
    smtpserver = "smtp.gmail.com:587"
    mailer = "Raspberry Pi"
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
    specialLog( "Done \n" )

# In Bytes
def getSpcAvail():
    specialLog( "Getting acvailable space..." )
    stfs = os.statvfs( "/" )
    free = stfs.f_bavail * stfs.f_frsize
    specialLog( "Done [ Returning: %f ]\n" % free )
    return free

# My camera creates a new directory every day containing 
# another directory containing the pictures
# You may have to rewrite this function for your use.
# In Bytes
def getAvgFileSize():
    specialLog( "Getting average file size..." )
    dirs = os.listdir( ftpDir )
    dirCount = 0
    totalSize = 0
    totalCount = 0

    for d in dirs:
        if d == "SpcWtch":
            continue
        else:
            dirCount += 1
            d = ftpDir + d + "/"
            if os.path.isdir( d ):
                subDirs = os.listdir( d )
                for sd in subDirs:
                    sd = d + sd + "/"
                    files = os.listdir( sd )
                    for f in files:
                        f = sd + f
                        if os.path.isfile( f ):
                            totalSize += os.path.getsize( f )
                            totalCount += 1

    log( "Days uploading: %d." % dirCount )
    log( "Total data size: %f%s." % (toKi( totalSize ), unit) )
    log( "Pictures taken: %d." % totalCount )
    log( "Pictures per day: %d." % (totalCount / dirCount) )

    specialLog( "Done [ Returning: %f ]\n" % float( totalSize / totalCount ) )
    return totalSize / totalCount

def toKi( byte ):
    if unit == "K":
        return byte / 1024
    else:
        return byte / 1000

    specialLog( "Done\n" )

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
    specialLog( "Starting..." )
    log( "Starting." )
    print( "Starting." )
    while availableSpace:
        log( "..............New cycle.............." )
        cycles += 1
        spcAvail = getSpcAvail()
        avg = getAvgFileSize()
        log( "Free disk space: %f%s." % (toKi( spcAvail ), unit) )
        log( "New average picture size: %f%s." % (toKi( avg ), unit) )
        log( "Pictures could be taken: %d." % (spcAvail / avg) )

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

        if messaging == "d" and cycles == DAY:
            message = statMessageTemp % ("Daily", statData )
            sendEmail( message, subjectFreq )
            cycles = 0
        if messaging == "w" and cycles == WEEK:
            message = statMessageTemp % ("Weekly", statData)
            sendEmail( message, subjectFreq )
            cycles = 0

        time.sleep( 30 * 60 ) # Sleep half an hour
        statData = ""
except KeyboardInterrupt:
    print( "\n" )
    log( "Received KeyboardInterrupt. Exiting." )
    log( "-------------------------------------" ) 
    logFile.close()
    exit( 0 )
except Exception as e:
    specialLog( "Interrupted by %s... Exiting." % str( type( e ) ) )
    exit( 1 )

# END MAIN
