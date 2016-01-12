#! /usr/bin/python3

import os
import apt
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
availableSpace = True
spcAvail = 0
avg = 0
messageTemp = "Raspberry Pi FTP-Server: Reached minimum value of free space!\n" \
              "Available space: %s kB.\n\n" \
              "Only %d pictures can be taken."

d = config.readConfig()

ftpDir = d[ "ftpDir" ]
mailingList = d[ "mailinglist" ]
minSpcAvail = int( d[ "min" ] ) # In Bytes ( 5.000.000B = 5MB )

logFile = open( ftpDir + "SpcWtch/mesg.txt", "a" )

# END VARIABLES

#----------------------------------------------------------------------

# FUNCTIONS
def sendEmail( mailingList, message ):
    login = "XXXX"
    password = "XXXX"
    smtpserver = "smtp.gmail.com:587"
    mailer = "Raspberry Pi"

    header  = "From: %s\n" % mailer
    mailingList = ",".join( mailingList )
    header += "To: %s\n" % mailingList
    header += "Subject: Raspberry Pi FTP-Server: No space available\n\n"
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
    totalSize = 0
    totalCount = 0

    for d in dirs:
        if d == "SpcWtch":
                continue
        else:
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
    log( "Total data size: %fkB." % toKilo( totalSize ) )
    log( "%d pictures have been taken." % totalCount )

    return totalSize / totalCount

def toKilo( byte ):
    return byte / 1000

def log( msg ):
    actTime = time.strftime( "%d.%m.%Y @ %H:%M:%S: " )
    logFile.write( actTime + msg + "\n" )
    logFile.flush()

# END FUNCTIONS

#----------------------------------------------------------------------

# MAIN
try:
    log( "Starting." )
    print( "Starting" )
    while availableSpace:
        log( "..............New cycle.............." )
        spcAvail = getSpcAvail()
        avg = getAvgFileSize()
        log( "Free disk space: %fkB" % toKilo( spcAvail ) )
        log( "New average picture size is: %f kB" % toKilo( avg ) )
        log( "%d pictures could be taken." % (spcAvail / avg) )

        if( spcAvail < minSpcAvail ):
            # Drive is going to have no available space / Send email
            log( "No space available anymore." )
            availableSpace = False
            message = messageTemp % ( toKilo( spcAvail ), (spcAvail / avg) )
            sendEmail( mailingList, message )
            log( "Email sent." )

            log( "Exiting normal." )
            log( "-------------------------------------" )
            exit( 0 )
        else:
      	    # Sleep half an hour
            time.sleep( 30 * 60 )
        time.sleep( 1 )
except KeyboardInterrupt:
    print( "\n" )
    log( "Received KeyboardInterrupt. Exiting." )
    log( "-------------------------------------" ) 
    logFile.close()
    exit( 0 )

# END MAIN
