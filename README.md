SpaceWatch

    This program is used to monitor disk space of a FTP file server
    and notify someone via email if it's running low.

    SpaceWatch was originaly designed for the use with a raspberry pi and
    an IP camera which can send images to a server.
    But theres not much to change if you want to use it somewhere else.
    See config file.

    If you install it with the install script, proftpd, a FTP-Server deamon, 
    will be installed too.
    The script writes some stats to a log file, that is located on the server.

    Units are configurable. You can either set K ( powers of 1024 ) or kB ( powers of 1000 ).
    See config file.

    The config file needs to be in the same directory as the sw.py file.
