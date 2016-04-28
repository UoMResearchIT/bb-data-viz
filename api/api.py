#!/usr/bin/env python

'''

This file is called every 24 hours (cronjob)

Actions:

1. Sync local database with clintouch database 
2. Create static JSON file from local database and save in web folder for the API call

'''

class BBAPI():
	'Main class for creating the data file for the Britain Breathing data visualisation plugin'

	# Constructor
	def __init__(self):
		self.config = self.getConfig()
	
		# Sync the local and source database
		self.syncDatabase()
		
		# Generate the JSON data file
		self.createDataFile()
	
	def syncDatabase(self):
		print(self.config['hostname'])
		
		# Connect to remote database
		
		# Get dump of tables
		
		# Update local database
	
		# On success, create the JSON data file
	
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
