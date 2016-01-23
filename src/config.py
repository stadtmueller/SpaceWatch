#! /usr/bin/python

def readConfig():
    d = {}
    with open( "sw.conf", "r" ) as configFile:
        for line in configFile:
            if not line.rstrip() or line.rstrip()[0] == '#': # Skip empty lines and lines
                continue                                     # lines starting with '#'

            seperatorPos = line.find( '=' )
            name = line[ :seperatorPos ].strip()
            content = line[ seperatorPos + 1: ].strip()
            d.update( { name : content } )
    return d
