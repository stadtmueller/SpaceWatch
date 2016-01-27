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
    noserv=1
else
    noserv=0
fi
    
    
echo "Enter FTP-Directory( If it doesn't exist it will be created ): ";
read ftpDir;

if [ ! -d $ftpDir ]
then
    mkdir $ftpDir;
fi
logPath="$ftpDir/SpcWtch"
swHome="/usr/local/SpcWtch"

echo "Creating directories...";
mkdir $logPath;
mkdir $swHome;

echo "Copy Files...";
cp src/clearLog.py $swHome;
cp src/config.py $swHome;
cp src/sw.py $swHome;
cp src/sw.conf $swHome;
touch "$logPath/mesg.txt";

echo "Configuring sw...";

echo "Enter minimum available size:";
read min;

echo "Enter a list of mail addresses that have to be notified when running out of space:";
echo "Seperate with ','";
read mailinglist;

echo "Enter the unit used to display stats in logfile( kB( 1000 ) or K( 1024 ) ): ";
read unit;

echo "Enter messaging frequency( d for daily; w for weekly; n for never ): ";
read messagingFreq;


configFile="$swHome/sw.conf"

echo "ftpDir = $ftpDir" >> $configFile;
echo "mailinglist = $mailinglist" >> $configFile;
echo "min = $min" >> $configFile;
echo "unit = $unit" >> $configFile;
echo "messaging = $messagingFreq" >> $configFile;
echo ""


echo "SpaceWatch is now ready to use."


#FTP-Installation:
if [ $noserv -eq 0 ]
then
    echo "Installing ProFTP...";
    apt-get -y install proftpd-basic;

    echo ""

    echo "Configuring ProFTP...";

    file=/etc/proftpd/proftpd.conf
    echo "DefaultRoot ~" >> $file;
    echo "AuthOrder              mod_auth_file.c  mod_auth_unix.c" >> $file;
    echo "AuthUserFile /etc/proftpd/ftpd.passwd" >> $file;
    echo "AuthPAM off" >> $file;
    echo "RequireValidShell off" >> $file;


    echo "Creating user for FTP-Access...";
    echo "Enter a user name( Required for login ): ";
    read userName;
    cd /etc/proftpd/;
    uid=$( id www-data -u )
    gid=$( id www-data -g )

    ftpasswd --passwd --name $userName --uid $uid --home $ftpDir --shell /bin/false;
    chmod g+s $ftpDir;
    chmod 755 $ftpDir;
    chown -R www-data:www-data $ftpDir;


    echo "Restarting FTP-Server...";
    /etc/init.d/proftpd restart;

    echo "FTP-Server ready to use.";
    ip=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
    echo "Try to call ftp://$ip from your browser and see the directory SpcWtch/."
fi

