#! /bin/bash

if [ $( id -u ) -gt 0 ]
   then
   echo "[ERR] Need root privileges!";
   echo "      Try sudo.";
   exit 1;
fi

    
echo "Enter FTP-Directory ( No '/' at the end ): ";
read ftpDir;
logPath="$ftpDir/SpcWtch/"
swHome="$HOME/SpcWtch/"
echo "";


echo "Creating directories...";
mkdir $ftpDir;
mkdir $logPath;
mkdir $swHome;
echo "";


echo "Copy Files...";
cp src/clearFiles.py $swHome;
cp src/sw.py $swHome;
touch $logPath/mesg.txt;
echo "";


echo "Installing ProFTP...";
apt-get install proftpd;
echo "";


echo "Configuring ProFTP...";
file=/etc/proftpd/proftpd.conf
echo "DefaultRoot ~" >> $file;
echo "AuthOrder              mod_auth_file.c  mod_auth_unix.c" >> $file;
echo "AuthUserFile /etc/proftpd/ftpd.passwd" >> $file;
echo "AuthPAM off" >> $file;
echo "RequireValidShell off" >> $file;
echo "";


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
echo "";


echo "Restarting FTP-Server..."
/etc/init.d/proftpd restart;
echo "";


echo "Setup finished. FTP-Server is ready to use."
ip=$(ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/')
echo "Try to call ftp://$ip from your browser."
echo ""
