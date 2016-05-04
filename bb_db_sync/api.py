#!/usr/bin/env python

'''

This file is called every 24 hours (cronjob)

Actions:

1. Sync local database with clintouch database 
2. Create static JSON file from local database and save in web folder for the API call

'''

import pymysql
import os
import datetime

class BBAPI():
	'Main class for creating the data file for the Britain Breathing data visualisation plugin'

	# Constructor
	def __init__(self):
		self.config = self.getConfig()
		
		# Sync the local and source database
		self.syncDatabases()
		
		# Generate the JSON data file
		self.createDataFile()
	
	def syncDatabases(self):
		# Backup the local database
		self.backupLocalDB()		
		
		# Get a dump of the remote database
		file_name = self.getRemoteDB()
		
		# Update the local database
		self.updateLocalDB(file_name)	
	
	def backupLocalDB(self):
		currentTime = str(datetime.datetime.now())
		now = currentTime.replace(" ", "-")
		file_name = "bb_backup_local-"+now+".sql.tar.gz"
		
		x =\
			"mysqldump\
			--host="+self.config['localhostname']+"\
			--port=3306\
			--databases bb\
			--user="+self.config['localusername']+"\
			--password="+self.config['localpassword']+"\
			> ~/bb_db_backups/bb_backup.sql;\
			cd ~/bb_db_backups;\
			tar -zcf "+file_name+" bb_backup.sql;\
			rm bb_backup.sql;"
		
		os.system(x)
	
	def getRemoteDB(self):
		currentTime = str(datetime.datetime.now())
		now = currentTime.replace(" ", "-")
		file_name = "bb_backup_remote-"+now+".sql"
		
		x =\
			"mysqldump\
			--host="+self.config['remoteusername']+"\
			--port=3306\
			--databases bb\
			--user="+self.config['remoteusername']+"\
			--password="+self.config['remotepassword']+"\
			> ~/bb_db_backups/"+file_name+";"
		
		os.system(x)
		
		return file_name
	
	def updateLocalDB(self, file_name):
		# Update the local database with the remote dump file
		x =\
			"mysql\
			-u "+self.config['localusername']+"\
			-p"+self.config['localpassword']+"\
			< ~/bb_db_backups/"+file_name+";\
			cd ~/bb_db_backups;\
			rm "+file_name+";"
		
		os.system(x)
	
	def createDataFile(self):
		pass
		
		# Do the database query
		
		
		# Parse the output into a JSON file
		
		
		# Save the file in the web folder
		
		
	def getConfig(self):
		# Get the config file details (database login)
		d = {}
		with open("./config.ini") as f:
			for line in f:
			   (key, val) = line.split(':')
			   d[key] = val.replace('\n', '').strip()
			   
		return d
	

BBAPI()
