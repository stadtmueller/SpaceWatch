#! /usr/bin/python3

import os
import time
import smtplib
import RPi.GPIO as GPIO
from _thread import start_new_thread

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
GPIO.setup( pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN )

WEEK            = 336 # One week = 336 half hours
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

# END VARIABLES

#----------------------------------------------------------------------

# FUNCTIONS
def rebootOnButton():
    while True:
        if GPIO.input( pin ):
            log( "Button press. Rebooting." )
            log( "------------------------" )
            os.system( "sudo reboot" )
        else:
            time.sleep( 2 )

def sendEmail( message, subject ):
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

# In Bytes
def getSpcAvail():
    stfs = os.statvfs( "/" )
    free = stfs.f_bavail * stfs.f_frsize
    return free

# My camera creates a new directory every day containing 
# another directory containing the pictures
# You may have to rewrite this function for your use.
# In Bytes
def getAvgFileSize():
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
    
    start_new_thread( rebootOnButton, () )
    
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

# END MAIN
