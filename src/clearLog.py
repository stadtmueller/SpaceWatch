#! /usr/bin/python3

import os

# INIT
if os.getuid() != 0:
  print( "Need root privileges. Exiting." )
  exit( 1 )

# END INIT

# ---------------------------------------------

with open( "/home/pi/FTP/SpcWtch/mesg.txt", "w" ) as logFile:
  logFile.write( "" )
