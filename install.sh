#!/bin/bash

# Check if the user is root.
if [ "$(id -u)" != "0" ]; then
	echo "Only root may run the install script."; exit 1; 
fi
# Install script to setup all the required entities for running the pipeline

# pip install nltk --upgrade
# exit

# apt-get install the required packages
apt-get update
# pre_req_packages='apache2 unzip wget python-dev python-sqlalchemy python-beautifulsoup python-biopython python-nltk python-pip python-sklearn python-pandas'
apt-get install -yq \
	apache2 \
	unzip \
	wget \
	python-dev \
	python-sqlalchemy \
	python-beautifulsoup \
	python-biopython \
	python-nltk \
	python-pip \
	python-sklearn \
	python-pandas \

# Required NLTK data
cp -r nltk_data ~/
# Copy the MedKatp required config files to /opt
mkdir -p /opt/nlp/
unzip -o opt-nlp.zip -d /opt/nlp

cp dtds/* /usr/lib/python2.7/dist-packages/Bio/Entrez/DTDs/

# Copy the visualization html & corresponding files to /var/www/html
cp src/html/* /var/www/html/

# Change the permissions on /var/www/html so that the user can copy the
# visualization json files
# Need to change this appropriately later. 
chmod -R a+w /var/www/html

wget --no-cookies --no-check-certificate --header "Cookie: gpw_e24=http%3A%2F%2Fwww.oracle.com%2F; oraclelicense=accept-securebackup-cookie"  http://download.oracle.com/otn-pub/java/jdk/8u65-b17/jre-8u65-linux-i586.tar.gz

tar xvzf jre-8u65-linux-i586.tar.gz
