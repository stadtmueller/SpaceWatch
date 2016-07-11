#! /usr/bin/python3

import time

# ---- Base class ----------------------
class Scheduler( object ):
    def __init__( self, schedule, action ):
        self.schedule = schedule
        self.action = action

    def performAction( self, data ):
        if self.schedule == "n":
            return

# --------------------------------------


# ---- MailScheduler -------------------
class MailScheduler( Scheduler ):
    def setTimeContent( self, mailtime, mailday ):
        self.mailtime = mailtime
        self.mailday  = mailday

        self.oldTime   = None
        self.oldDay    = None

        self.sameTime  = False
        self.sameDay   = False

    def setMailContent( self, message, subject ):
        self.message = message
        self.subject = subject

    def performAction( self ):
        if self.schedule == "n":
            return

        actHour = time.strftime( "%H" )
        actDay  = time.strftime( "%w" )

        if( self.schedule == "d" ):
            if( actHour != self.oldTime ):
                sameTime = False

            if( actHour == self.mailtime and self.sameTime == False ):
                  self.sameTime = True
                  self.oldTime = actHour
                  self.action( self.message, self.subject )

        if( self.schedule == "w" ):
            if( actDay != self.oldDay ):
                self.sameDay = False
            if( actHour != self.oldTime ):
                self.sameTime = False

            if( actHour == self.mailtime and self.sameTime == False and self.sameDay == False ):
               self.sameTime = True
               self.sameDay  = True
               self.oldTime  = actHour
               self.oldDay   = actDay
               self.action( self.message, self.subject )

