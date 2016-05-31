#! /bin/bash

if [ $( id -u ) -gt 0 ]
then
   echo "[ERR] Need root privileges!";
   echo "      Try sudo.";
   exit 1;
fi


if [ "$1" = "-noserver" ]
then
    echo "No-server set...";
    noserv=1;
else
    noserv=0;
fi
    
    
echo "Enter FTP-Directory( If it doesn't exist it will be created, no '/' at the end ): ";
read ftpDir;

if [ ! -d $ftpDir ]
then
    mkdir $ftpDir;
fi

logPath="$ftpDir/SpcWtch";
swHome="/usr/local/SpcWtch";

echo "Creating directories...";
mkdir $logPath;
mkdir $swHome;

echo "Copy Files...";
cp src/truncateLog.sh $swHome;
cp src/config.py $swHome;
cp src/sw.py $swHome;
cp src/sw.conf $swHome;
touch "$logPath/mesg.txt";

echo "Configuring sw...";

echo "Enter minimum available size in Bytes:";
read min;

echo "Enter the unit used to display stats in logfile( kB, K, mB, M, gB, G, auto ): ";
read unit;

echo "Enter a list of mail addresses that have to be notified when running out of space:";
echo "Seperate with ','";
read mailinglist;

echo "Enter messaging frequency for statistics( d for daily; w for weekly; n for never ):";
read messagingFreq;

case $messagingFreq in
    "n") mailtime=0; 
	 mailday=0; ;;
    "d") echo "Enter the time the stat mail will be send at( number between 0 and 23 ): ";
         read mailtime; ;;
    "w") echo "Enter the day the stat mail will be send at( number between 0 and 7 ): ";
         read mailday;
	 echo "Enter the time the stat mail will be send at( number between 0 and 23 ): ";
         read mailtime; ;;
      *) echo "Not valid. Setting frequency to 'n'";
	 $messagingFreq="n"; ;;
esac

echo "Enter email login: ";
read login;

echo "Enter password: ";
read password;


configFile="$swHome/sw.conf";

echo "ftpDir = $ftpDir/"          >> $configFile;
echo "mailinglist = $mailinglist" >> $configFile;
echo "min = $min"                 >> $configFile;
echo "unit = $unit"               >> $configFile;
echo "messaging = $messagingFreq" >> $configFile;
echo "mailtime = $mailtime"       >> $configFile;
echo "mailday = $mailday"         >> $configFile;
echo "loginName = $login"         >> $configFile;
echo "loginPassword = $password"  >> $configFile;
echo "";


echo "SpaceWatch is now ready to use.";


#FTP-Installation:
if [ $noserv -eq 0 ]
then
    echo "Installing ProFTP...";
    apt-get -y install proftpd-basic;

    echo "";

    echo "Configuring ProFTP...";

    file=/etc/proftpd/proftpd.conf;
    echo "DefaultRoot ~"                                           >> $file;
    echo "AuthOrder              mod_auth_file.c  mod_auth_unix.c" >> $file;
    echo "AuthUserFile /etc/proftpd/ftpd.passwd"                   >> $file;
    echo "AuthPAM off"                                             >> $file;
    echo "RequireValidShell off"                                   >> $file;


    echo "Creating user for FTP-Access...";
    echo "Enter a user name( Required for login ): ";
    read userName;
    cd /etc/proftpd/;
    uid=$( id www-data -u );
    gid=$( id www-data -g );

    ftpasswd --passwd --name $userName --uid $uid --home $ftpDir --shell /bin/false;
    chmod g+s $ftpDir;
    chmod 755 $ftpDir;
    chown -R www-data:www-data $ftpDir;


    echo "Restarting FTP-Server...";
    /etc/init.d/proftpd restart;

    echo "FTP-Server ready to use.";
    ip=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/');
    echo "Try to call ftp://$ip from your browser and see the directory SpcWtch/.";
fi

echo "";
echo "Setup finished.";
echo "";
echo "If you want SpaceWatch to automatically start with";
echo "the server run 'sudo crontab -e' and add the line '@reboot /usr/local/SpcWtch/sw.py'";
echo "to the end of the file.";

