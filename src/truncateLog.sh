#! /bin/bash

if [ $1 ]
then
    if [ "$1" == "?" ]
    then
        echo "Usage:"
        echo "           -q: Display help."
        echo "         file: Truncate the lines of (file)."
        echo "No parameters: Specifie file later."
	exit

    elif [ "$1" != "?" ]
    then
        fileToTruncate=$1

    fi
else
    echo "Use file: "
    read fileToTruncate
fi

echo "From line: "
read fromLine

echo "To line: "
read toLine

param=$fromLine,$toLine"d"

sed -i -e $param $fileToTruncate
