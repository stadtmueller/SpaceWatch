#! /usr/bin/python

def isInt( txt ):
    try: 
        int( txt )
        return True
    except ValueError:
        return False

def readConfig():
    d = {}
    with open( "/usr/local/SpcWtch/sw.conf", "r" ) as configFile:
        for line in configFile:
            if not line.rstrip() or line.rstrip()[0] == '#': # Skip empty lines and lines
                continue                                     # lines starting with '#'

            seperatorPos = line.find( '=' )
            name = line[ :seperatorPos ].strip()
            content = line[ seperatorPos + 1: ].strip()
            d.update( { name : content } )
            
    if not d[ "unit" ] in [ "K", "kB", "M", "mB", "G", "gB" ]:
        d[ "unit" ] = "K"
        print( "Error in config file detected. Setting unit to K." )
    if not d[ "messaging" ] in [ "n", "w", "d" ]:
        d[ "messaging" ] = "n"
        print( "Error in config file detected. Setting messaging to never." )
    
    if not isInt( d[ "min" ] ):
        d[ "min" ] = "5000000"
        print( "Error in config file detected. Setting min to 5.000.000." )

    if isInt( d[ "mailtime" ] ):
        timeInt = int( d[ "mailtime" ] )
        if timeInt < 0 or timeInt > 23:
            d[ "mailtime" ] = "18"
            print( "Error in config file detected. Setting mailtime to 18" )
    if not isInt( d[ "mailtime" ] ):
        d[ "mailtime" ] = "18"
        print( "Error in config file detected. Setting mailtime to 18" )


    return d
