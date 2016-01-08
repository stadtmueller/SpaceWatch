#! /usr/bin/python3

import os
import apt
import time

#----------------------------------------------------------------------

# INIT
if os.getuid() != 0:
  print( "[ERR] Root-Rechte benoetigt!" )
  print( "      Versuch 'sudo python3 sw.py'")
  exit( 1 )

cache = apt.Cache()
if not cache[ 'mailutils' ].is_installed:
  print( "[ERR] sendmail is not installed!" )
  print( "      Install with 'sudo apt-get install sendmail'" )
  exit( 2 )

# END INIT

#----------------------------------------------------------------------

# VARIABLES
minSpcAvail = 15625 # In Bytes ( == 5MB )
logFile = open( "/home/pi/FTP/SpcWtch/mesg.txt", "a" )
ftpDir = "/home/pi/FTP/"   # !!!  Must end with '/'
availableSpace = True
spcAvail = 0
avg = 0
messageTemp = "Raspberry Pi FTP-Server: Mindestwert an freiem Speicher unterschritten!\n" \
              "Verfuegbarer Speicher: %s kB.\n\n" \
              "Es koennen nur noch ca. %d Bilder gemacht werden."
commandTemp = "echo '%s' | sendmail -s 'Raspberry Pi FTP-Server' timsta2000@googlemail.com"

# END VARIABLES

#----------------------------------------------------------------------

# FUNCTIONS
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
    while availableSpace:
        spcAvail = getSpcAvail()
        log( "Free disk space: %fB" % spcAvail )
        if( spcAvail < minSpcAvail ):
            # Drive is going to have no available space / Send email
            log( "No space available anymore." )
            availableSpace = False
            if avg == 0:
                avg = toKilo( getAvgFileSize() )
            log( "Average picture size: %fkB" % avg )
            message = messageTemp % ( toKilo( spcAvail ), (spcAvail / avg) )
            command = commandTemp % message
            #os.system( command ) 

            log( "Exiting normal." )
            log( "------------------------------------" )
            exit( 0 )
        else:
            # Recalculate average picture size
      	    # Sleep half an hour
            log( "Recalculate average picture size." )
            avg = toKilo( getAvgFileSize() )
            log( "New average picture size is: %f kB" % avg )
            log( "%d pictures could be taken." % (spcAvail / avg) )
            time.sleep( 30 * 60 * 60 )
        time.sleep( 1 )
except KeyboardInterrupt:
    print( "\n" )
    log( "Received KeyboardInterrupt. Exiting." )
    log( "------------------------------------" ) 
    logFile.close()
    exit( 0 )

# END MAIN
