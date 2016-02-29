SpaceWatch

    This program is used to monitor disk space of a FTP file server
    and notify someone via email if it's running low.

    It can give you the latest stats weekly or even daily.

    SpaceWatch was originaly designed for the use with a raspberry pi and
    an IP camera which can send images to a server.
    But theres not much to change if you want to use it somewhere else.
    See config file.

    Make sure to edit the config file and sw.py. Give it your username and password to
    mail address so SpaceWatch can send from it.

    If you install it with the install script, proftpd, a FTP-Server deamon, 
    will be installed too.

    Run "sudo ./install [ option ]" to install SpaceWatch.

    Add the option "-noserver" to installation command to suppress server installation.

    The script writes some stats to a log file, that should be together with sw.py
    located on the server.

    Units are configurable. You can either set unit to powers of 1024 or units to powers of 1000
    such as GiBiByte or Gigabyte.
    See config file.

    The config file needs to be in the same directory as the sw.py file.
