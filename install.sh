#! /bin/bash

if [ $( id -u ) -gt 0 ]
   then
   echo "[ERR] Need root privileges!";
   echo "      Try sudo.";
   exit 1;
fi

    
echo "Enter FTP-Directorie: ";
read ftpDir;
logPath="$ftpDir/SpcWtch"
swHome="/usr/local/SpcWtch"


echo "Creating directories...";
mkdir $ftpDir;
mkdir $logPath;
mkdir $swHome;


echo "Copy Files...";
cp ./clearFiles.py $swHome;
cp ./sw.py $swHome;
touch $logPath/mesg.txt;
touch $swHome/sw.conf;


echo "Installing ProFTP...";
apt-get install proftp;


echo "Configuring ProFTP...";
file = /etc/proftpd/proftpd.conf
echo "DefaultRoot ~" >> $file;
echo "AuthOrder              mod_auth_file.c  mod_auth_unix.c" >> $file;
echo "AuthUserFile /etc/proftpd/ftpd.passwd" >> $file;
echo "AuthPAM off" >> $file;
echo "RequireValidShell off" >> $file;


echo "Creating user for FTP-Access...";
echo "Enter a user name:( Required for login ): ";
read $userName;
cd /etc/proftpd/;
uid=$( id www-data -u )
gid=$( id www-data -g )
ftpasswd -passwd -name $userName -uid $uid -gid $gid -home $ftpDir -shell /bin/false;
chmod g+s $ftpDir;
chmod 755 $ftpDir
chown -R www-data:www-data $ftpDir


echo "Restarting FTP-Server..."
/etc/init.d/proftpd restart;


echo "Configuring sw...";

echo "Enter minimum available size";
read min;

echo "Enter a list of mail addresses that have to be notified when running out of space.";
echo "Seperate with ','";
read mailinglist;

configFile="$swHome/sw.conf"

echo "ftpDir = $ftpDir" >> $configFile;
echo "mailinglist = $mailinglist" >> $configFile;
echo "min = $min" >> $configFile;

echo ""



echo "Setup finished. FTP-Server is ready to use."
ip=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
echo "Try to call ftp://$ip from your browser."

