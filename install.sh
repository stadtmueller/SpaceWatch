#! /bin/bash

if [ $( id -u ) -gt 0 ]
   then
   echo "[ERR] Need root privileges!";
   echo "      Try sudo.";
   exit 1;
fi
    
echo "Enter FTP-Directorie: ";
read ftpDir;

echo "Creating directories..."
mkdir $ftpDir;
mkdir "$ftpDir/SpcWtch/";
mkdir "$HOME/SpcWtch/";

echo "Moving Files"
