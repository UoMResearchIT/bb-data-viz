#!/usr/bin/env python

'''

This file is called every 24 hours (cronjob)

Actions:

1. Sync local database with clintouch database 
2. Create static KML files from local database and save in web folder for the API call

Run with Python 3+
pip3 install { any needed modules below }

'''

import pymysql
import os
import sys
import datetime
from sshtunnel import SSHTunnelForwarder
import csv
import json
import urllib.request
from string import digits
import statistics
import xml.etree.ElementTree as ET
import time
import datetime
import pprint
import numpy as np

class BBAPI():
	'Main class for creating the data file for the Britain Breathing data visualisation plugin'

	# Constructor
	def __init__(self):
		self.config = self.getConfig()
		
		# Sync the local and source database
		#self.syncDatabases()
		
		# TESTING
		# self.createDataFile()
		# self.addPostcodesToDB()
		self.createDataFile()
	
	def syncDatabases(self):
		# Backup the local database
		self.backupLocalDB()		
		
		# Get an update of data from the remote database
		self.getRemoteDB()
	
	def backupLocalDB(self):
		x =\
			"mysqldump\
			--databases bb\
			--user="+self.config['localusername']+"\
			--password="+self.config['localpassword']+"\
			> ~/bb_db_backups/bb_backup.sql;\
			cd ~/bb_db_backups;\
			tar -zcf bb_backup_local.sql.tar.gz bb_backup.sql;\
			rm bb_backup.sql;"
		
		os.system(x)
	
	def getRemoteDB(self):
		# TODO: This needs to add new rows since the last update, rather than replace everything.
		'''
		# Get the local database last record timestamp
		conn = pymysql.connect(host='127.0.0.1', port=3306, user=self.config['localusername'], passwd=self.config['localpassword'], db=self.config['localdbname'])
		cur = conn.cursor()
		cur.execute('SELECT Time_uploaded_to_server FROM remotedata ORDER BY Time_uploaded_to_server ASC;')
		lts = cur.fetchone()
		lastTimestamp = lts[0]
		
		cur.close()
		conn.close()
		'''
		
		# The database query
		sql = """select enc.dateTime, enc.pushedToServerDateTime, enc.howFeeling, enc.takenMedsToday+0, 
				 MAX(IF(Observation.question_id = "20140544-1bee-4d02-b764-d80102437adc", Observation.valueNumeric, NULL)) AS Nose, 
				 MAX(IF(Observation.question_id = "22d7940f-eb30-42cd-b511-d0d65b89eec6", Observation.valueNumeric, NULL)) AS Eyes, 
				 MAX(IF(Observation.question_id = "2cd9490f-d8ca-4f14-948a-1adcdf105fd0", Observation.valueNumeric, NULL)) AS Breathing, 
				 demo.birthYear, demo.gender, demo.allergiesDivulged+0, demo.hayFever+0, demo.asthma+0, demo.otherAllergy+0, 
				 demo.unknownAllergy+0, loc.latitude, loc.longitude, loc.accuracy, loc.whenObtained 
				 from Encounter as enc inner join Observation on Observation.encounter_id = enc.id 
				 inner join Question on Observation.question_id = Question.id join Demographics as demo on demo.id = enc.demographics_id 
				 join LocationInfo as loc on loc.id = enc.locationInfo_id 
				 group by enc.id;"""
		
		# Open SSH tunnel
		server = SSHTunnelForwarder(
			(self.config['remotehostname'], 1522),
			ssh_username=self.config['remoteusername'],
			ssh_password=self.config['remotepassword'],
			remote_bind_address=('127.0.0.1', 3306)
		)
		
		# Select data from remote database
		server.start()
		#print(server.local_bind_port)
		#print(server.tunnel_is_up)
		#print(server.local_is_up(('127.0.0.1', 3306)))
		
		if server.is_alive:
			print('Connection up...executing sql...')
			#print(os.system('mysql -h 127.0.0.1 --port='+str(server.local_bind_port)+' -u'+self.config['remoteusername']+' -p'))
			
			try:
				conn = pymysql.connect(host='127.0.0.1', port=server.local_bind_port, user=self.config['remoteusername'], passwd=self.config['remotedbpassword'], db=self.config['remotedbname'])
				cur = conn.cursor()
				cur.execute(sql)
				cur.close()
				conn.close()
				
			except pymysql.err.OperationalError:
				print('MySQL failed...exiting.')
				server.stop()
				sys.exit(0)
			
		# Close the ssh tunnel
		server.stop()
		
		# Update local database
		lconn = pymysql.connect(host='127.0.0.1', port=3306, user=self.config['localusername'], passwd=self.config['localpassword'], db=self.config['localdbname'], autocommit=True)
		lcur = lconn.cursor()
		lcur.execute('TRUNCATE TABLE remotedata;')
		
		rowcount = 0
		for row in cur:
			#print(row[0])
			sql = """INSERT INTO remotedata (id, Time_answered_on_phone, Time_uploaded_to_server, feeling, Taken_meds_today, Nose, Eyes, Breathing, Year_of_Birth, Gender, Optional_data_shared, hay_fever, asthma, other_allergy, unknown, latitude, longitude, accuracy, time_of_location_fix) VALUES ('', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');
			""".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17])
			
			# Update the remotedata table
			lcur.execute(sql)
			
			# Update the row count
			rowcount = rowcount+1
		
		print('Rows processed: ', rowcount)
		
		# Done
		lcur.close()
		lconn.close()
		
		# DB sync complete, update the postcodes
		self.addPostcodesToDB()
	
	def addPostcodesToDB(self):
		# Updating postcode data
		timestart = time.time()
		i=0
		
		lconn = pymysql.connect(host='127.0.0.1', port=3306, user=self.config['localusername'], passwd=self.config['localpassword'], db=self.config['localdbname'], autocommit=True)
		lcur = lconn.cursor()
		lcur.execute('SELECT * FROM remotedata WHERE postcode IS NULL;')
		
		for row in lcur:
			try:
				url = 'http://uk-postcodes.com/latlng/'+str(row[15])+','+str(row[16])+'.json'
				with urllib.request.urlopen(url) as response:
					postcode = json.loads(response.readall().decode('utf-8'))
			except urllib.error.HTTPError:
				print('No postcode found for coordinates.')
				continue
		
			postcodeStub = ''
			for char in list(postcode['postcode']):
				if char.isdigit():
					break
				else:
					postcodeStub += char
			
			# Update the database
			lcur1 = lconn.cursor()
			lcur1.execute('UPDATE remotedata SET postcode="'+postcodeStub+'" WHERE id='+str(row[0])+';')
			
			currenttime = time.time()-timestart
			print(str(datetime.timedelta(seconds=currenttime)), i, 'Found postcode ', postcodeStub)
			i=i+1
		
		print('Updated {} postcode records'.format(i))
		
		# Create the static KML API files when done
		self.createDataFile()
	
	def createDataFile(self):
		# Get data from database
		self.updateMessage('Creating API data files...')
		
		lconn = pymysql.connect(host='127.0.0.1', port=3306, user=self.config['localusername'], passwd=self.config['localpassword'], db=self.config['localdbname'], autocommit=True)
		lcur = lconn.cursor()
		lcur.execute('SELECT * FROM remotedata WHERE postcode IS NOT NULL;')
		
		# Create the dictionary to hold all the processed data from the postcode file
		
		# Calculate the weeks
		startWeekDate = '2016-03-14'
		
		d = datetime.date.today()
		if d.weekday() == 0:
			d += datetime.timedelta(1)
		while d.weekday() != 0:
			d += datetime.timedelta(1)
		
		nextMonday = d.strftime('%Y-%m-%d')
		
		d0 = datetime.datetime.strptime(startWeekDate, '%Y-%m-%d')
		d1 = datetime.datetime.strptime(nextMonday, '%Y-%m-%d')
		delta = d1-d0
		numberOfWeeks = int(delta.days/7)+1
		
		weeksList = {}
		weeksList[startWeekDate] = {}
		weekDates = datetime.datetime.strptime(startWeekDate, '%Y-%m-%d')
		
		self.updateMessage('Building data structure...')
		
		# Week start keys
		for i in range(1, numberOfWeeks):
			weekDates += datetime.timedelta(days=7)
			weeksList[weekDates.strftime('%Y-%m-%d')] = {}
		
		# Add the current week
		weeksList[nextMonday] = {}
		
		# Week end keys
		weekCombinationSize = 1
		
		# Postcode list
		csvData = open("data/postcodes.csv")
		postcodesCSV = csv.reader(csvData, delimiter=",")
		next(postcodesCSV)
		postcodeList = []
		
		# Set up the keys
		for row in postcodesCSV:
			postcodeList.append(row[0])
		
		postcodeList.sort()
		
		for weekstart in weeksList:
			for weekend in weeksList:
				if weekstart != weekend and weekstart < weekend:
					weeksList[weekstart][weekend] ={} 
					
					print('Week combinations generated: ', weekCombinationSize)
					weekCombinationSize = weekCombinationSize+1
					
					for postcode in postcodeList:
						weeksList[weekstart][weekend][postcode] = {'all_total': 0,
																'feeling_total': 0,
																'nose_total': 0, 
																'eyes_total': 0, 
																'breathing_total': 0,
																'all_list': [0],
																'feeling_list': [0],
																'nose_list': [0],
																'eyes_list': [0],
																'breathing_list': [0],
																'all_median': 0,
																'feeling_median': 0,
																'nose_median': 0,
																'eyes_median': 0,
																'breathing_median': 0,
																'all_stddev': 0,
																'feeling_stddev': 0,
																'nose_stddev': 0,
																'eyes_stddev': 0,
																'breathing_stddev': 0}
		
		# Loop through each database row and update the figures
		self.updateMessage('Calculating data...')
		
		for row in lcur:
			self.updateMessage('Adding data to postcodeList for: {}'.format(row[19]))
			
			# Update the corresponding postcode and date range figures
			entryPostcode = row[19]
			entryDate = row[2].split(' ')
			entryDate = entryDate[0]
			
			for weekstart in weeksList:
				for weekend in weeksList:
					if weekstart < entryDate < weekend:
						# Date within range update the data	
						#print(weekstart, entryDate, weekend)
						
						# Append values to the lists to calculate median and standard deviation
						weeksList[weekstart][weekend][row[19]]['all_list'].append(row[3])
						weeksList[weekstart][weekend][row[19]]['all_list'].append(row[5])
						weeksList[weekstart][weekend][row[19]]['all_list'].append(row[6])
						weeksList[weekstart][weekend][row[19]]['all_list'].append(row[7])
						weeksList[weekstart][weekend][row[19]]['feeling_list'].append(row[3])
						weeksList[weekstart][weekend][row[19]]['nose_list'].append(row[5])
						weeksList[weekstart][weekend][row[19]]['eyes_list'].append(row[6])
						weeksList[weekstart][weekend][row[19]]['breathing_list'].append(row[7])
						
						weeksList[weekstart][weekend][row[19]]['all_total'] = len(weeksList[weekstart][weekend][row[19]]['all_list'])
						weeksList[weekstart][weekend][row[19]]['feeling_total'] = len(weeksList[weekstart][weekend][row[19]]['feeling_list'])
						weeksList[weekstart][weekend][row[19]]['nose_total'] = len(weeksList[weekstart][weekend][row[19]]['nose_list'])
						weeksList[weekstart][weekend][row[19]]['eyes_total'] = len(weeksList[weekstart][weekend][row[19]]['eyes_list'])
						weeksList[weekstart][weekend][row[19]]['breathing_total'] = len(weeksList[weekstart][weekend][row[19]]['breathing_list'])
		
		# Calculate the data	
		weekCombinationCurrent = 1
				
		for weekstart in weeksList:
			for weekend in weeksList:
				if weekstart != weekend and weekstart < weekend:
					weekCombinationCurrent = weekCombinationCurrent+1
					
					for postcode in postcodeList:
						
						self.updateMessage('Week: {} to {}, combination {}/{}'.format(weekstart, weekend, weekCombinationCurrent, weekCombinationSize))
					
						# Calculate medians
						self.updateMessage('Calculating medians.')
						weeksList[weekstart][weekend][postcode]['all_median']  = np.median(weeksList[weekstart][weekend][postcode]['all_list'])
						weeksList[weekstart][weekend][postcode]['feeling_median']  = np.median(weeksList[weekstart][weekend][postcode]['feeling_list'])
						weeksList[weekstart][weekend][postcode]['nose_median']  = np.median(weeksList[weekstart][weekend][postcode]['nose_list'])
						weeksList[weekstart][weekend][postcode]['eyes_median']  = np.median(weeksList[weekstart][weekend][postcode]['eyes_list'])
						weeksList[weekstart][weekend][postcode]['breathing_median']  = np.median(weeksList[weekstart][weekend][postcode]['breathing_list'])
						
						# Calculate standard deviation
						self.updateMessage('Calculating standard deviation.')
					
						if len(weeksList[weekstart][weekend][postcode]['all_list']) > 1:
							weeksList[weekstart][weekend][postcode]['all_stddev'] = round(np.std(weeksList[weekstart][weekend][postcode]['all_list']), 3)
						else:
							weeksList[weekstart][weekend][postcode]['all_stddev'] = 'Not enough data available.'
					
						if len(weeksList[weekstart][weekend][postcode]['feeling_list']) > 1:
							weeksList[weekstart][weekend][postcode]['feeling_stddev'] = round(np.std(weeksList[weekstart][weekend][postcode]['feeling_list']), 3)
						else:
							weeksList[weekstart][weekend][postcode]['feeling_stddev'] = 'Not enough data available.'
					
						if len(weeksList[weekstart][weekend][postcode]['nose_list']) > 1:
							weeksList[weekstart][weekend][postcode]['nose_stddev'] = round(np.std(weeksList[weekstart][weekend][postcode]['nose_list']), 3)
						else:
							weeksList[weekstart][weekend][postcode]['nose_stddev'] = 'Not enough data available.'
					
						if len(weeksList[weekstart][weekend][postcode]['eyes_list']) > 1:
							weeksList[weekstart][weekend][postcode]['eyes_stddev'] = round(np.std(weeksList[weekstart][weekend][postcode]['eyes_list']), 3)
						else:
							weeksList[weekstart][weekend][postcode]['eyes_stddev'] = 'Not enough data available.'
					
						if len(weeksList[weekstart][weekend][postcode]['breathing_list']) > 1:
							weeksList[weekstart][weekend][postcode]['breathing_stddev'] = round(np.std(weeksList[weekstart][weekend][postcode]['breathing_list']), 3)
						else:
							weeksList[weekstart][weekend][postcode]['breathing_list_stddev'] = 'Not enough data available.'
					
		#### Create data files	: save files in format, timelineType-YYYY-MM-DD-YYYY-MM-DD.kml'
		self.updateMessage('Writing the KML files...')
		
		symptomList = ['all', 'feeling', 'nose', 'eyes', 'breathing']
		fileCount = 1
		
		for symptom in symptomList:
			print('Symptom type:', symptom)
			
			for weekstart in weeksList:
				for weekend in weeksList:
					if weekstart != weekend and weekstart < weekend:
						
						print('Sorting KML data for ', weekstart, weekend)
						
						# Symptom file
						fileCount = fileCount+1
						ET.register_namespace('', "http://www.opengis.net/kml/2.2")
						tree = ET.parse('data/ukpostcodes_template.kml')
						root = tree.getroot()
										
						for postcode in postcodeList:
							for placemark in root[0][7]:
								style = placemark[0]
								name = placemark[1]
								desc = placemark[2]
								
								if name.text == 'Data for postcode '+postcode:
									desc.set('respondents', str(weeksList[weekstart][weekend][postcode][symptom+'_total']))
									desc.set('symptom-score', str(weeksList[weekstart][weekend][postcode][symptom+'_median']))
									
									desc.set('stddev-score', str(weeksList[weekstart][weekend][postcode][symptom+'_stddev']))
									desc.text = """<p>Data summary:</p>
													<table>
													<tr><td>Entries</td><td>{}</td></tr>
													<tr><td>Median score</td><td>{}</td></tr>
													<tr><td>Standard deviation</td><td>{}</td></tr>
													</table>
												""".format(weeksList[weekstart][weekend][postcode][symptom+'_total'], weeksList[weekstart][weekend][postcode][symptom+'_median'], weeksList[weekstart][weekend][postcode][symptom+'_stddev'])
									
									if weeksList[weekstart][weekend][postcode][symptom+'_median'] == 0:
										style.text = '#none'
									elif weeksList[weekstart][weekend][postcode][symptom+'_median'] == 1:
										style.text = '#green'
									elif weeksList[weekstart][weekend][postcode][symptom+'_median'] == 2:
										style.text = '#orange'
									elif weeksList[weekstart][weekend][postcode][symptom+'_median'] >= 3:
										style.text = '#red'
							
							tree.write('/var/www/html/bb/api/'+symptom+'-'+weekstart+'-'+weekend+'.kml')
							self.updateMessage('Written file: {}'.format(symptom+'-'+weekstart+'-'+weekend+'.kml'))
		
		print('Files written: ', fileCount)
	
	def updateMessage(self, msg):
		print(msg)
		print('Start time: ', time.strftime("%H:%M:%S"))
	
	def getConfig(self):
		# Get the config file details (database login)
		d = {}
		with open("./config.ini") as f:
			for line in f:
			   (key, val) = line.split(':')
			   d[key] = val.replace('\n', '').strip()
			   
		return d
	

BBAPI()
