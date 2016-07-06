#!/usr/bin/env python

'''

This file is called every 24 hours (cronjob)

Actions:

1. Sync local database with clintouch database 
2. Create static JSON file from local database and save in web folder for the API call

Run with Python 3+
pip3 install { any needed modules }

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

class BBAPI():
	'Main class for creating the data file for the Britain Breathing data visualisation plugin'

	# Constructor
	def __init__(self):
		self.config = self.getConfig()
		
		# Sync the local and source database
		self.syncDatabases()
	
	def syncDatabases(self):
		# Backup the local database
		#self.backupLocalDB()		
		
		# Get an update of data from the remote database
		#self.getRemoteDB()
		
		# TEST
		self.createDataFile()
	
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
			sql = """INSERT INTO remotedata (id, Time_answered_on_phone, Time_uploaded_to_server, How_feeling, Taken_meds_today, Nose, Eyes, Breathing, Year_of_Birth, Gender, Optional_data_shared, hay_fever, asthma, other_allergy, unknown, latitude, longitude, accuracy, time_of_location_fix) VALUES ('', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');
			""".format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17])
			
			# Update the remotedata table
			lcur.execute(sql)
			
			# Update the row count
			rowcount = rowcount+1
		
		print('Rows processed: ', rowcount)
		
		# Done
		lcur.close()
		lconn.close()
		
		# DB sync complete, create the JSON API file
		self.createDataFile()
	
	def createDataFile(self):
		# Update the local database table apidata
		print('Creating API data files...')
		timestart = time.time()
		
		lconn = pymysql.connect(host='127.0.0.1', port=3306, user=self.config['localusername'], passwd=self.config['localpassword'], db=self.config['localdbname'], autocommit=True)
		lcur = lconn.cursor()
		lcur.execute('SELECT * FROM remotedata;')
		
		'''
			Aggregate the remote data by postcode
		'''
		
		# Get the postcode list
		postcodesCSV = csv.reader(open("data/postcodes.csv"), delimiter=",")
		
		# Skip the header
		next(postcodesCSV)
		
		postcodeList = {}
		
		for row in postcodesCSV:
			postcodeList[row[0]] = {'symptom_score': 0, 
									'how_feeling_total': 0,
									'nose_total': 0, 
									'eyes_total': 0, 
									'breathing_total': 0,
									'how_feeling_list': [0],
									'nose_list': [0],
									'eyes_list': [0],
									'breathing_list': [0],
									'responses_total': 0}
		
		i = 0
		for row in lcur:
			# Aggregate the data into the postcode list
			i = i+1
			url = 'http://uk-postcodes.com/latlng/'+str(row[15])+','+str(row[16])+'.json'
			#print(url)
			
			try:
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
			
			currenttime = time.time()-timestart
			print(str(datetime.timedelta(seconds=currenttime)), i, 'Found postcode ', postcodeStub)
			
			# Append to the lists for calculating the medians
			postcodeList[postcodeStub]['how_feeling_list'].append(row[3])
			postcodeList[postcodeStub]['nose_list'].append(row[5])
			postcodeList[postcodeStub]['eyes_list'].append(row[6])
			postcodeList[postcodeStub]['breathing_list'].append(row[7])
		
			# Tally the totals
			postcodeList[postcodeStub]['how_feeling_total'] = int(row[3])+int(postcodeList[postcodeStub]['how_feeling_total'])
			postcodeList[postcodeStub]['nose_total'] = int(row[5])+int(postcodeList[postcodeStub]['nose_total'])
			postcodeList[postcodeStub]['eyes_total'] = int(row[6])+int(postcodeList[postcodeStub]['eyes_total'])
			postcodeList[postcodeStub]['breathing_total'] = int(row[7])+int(postcodeList[postcodeStub]['breathing_total'])
			postcodeList[postcodeStub]['responses_total'] = int(postcodeList[postcodeStub]['responses_total'])+1
		
		# Calculate overall severity of symptoms score for each postcode: total of the symptom medians
		for key, value in postcodeList.items():
			try:
				postcodeList[key]['how_feeling_median'] = round(statistics.median(postcodeList[key]['how_feeling_list']),2)
				postcodeList[key]['nose_median'] = round(statistics.median(postcodeList[key]['nose_list']),2)
				postcodeList[key]['eyes_median'] = round(statistics.median(postcodeList[key]['eyes_list']),2)
				postcodeList[key]['breathing_median'] = round(statistics.median(postcodeList[key]['breathing_list']),2)
				postcodeList[key]['symptom_score'] = round(postcodeList[key]['how_feeling_median']+postcodeList[key]['nose_median']+postcodeList[key]['eyes_median']+postcodeList[key]['breathing_median'],2)
			except KeyError:
				print('Error for', key)
		
		# Sort the list
		sorted(postcodeList)
		
		#print(postcodeList)
		#sys.exit(0)
		
		# Close the connections	
		lcur.close()
		lconn.close()
		
		### Write kml files for the different variables
		
		# Overall symptom score
		ET.register_namespace('', "http://www.opengis.net/kml/2.2")
		tree = ET.parse('data/ukpostcodes_template.kml')
		root = tree.getroot()
		
		for key, value in postcodeList.items():
			for placemark in root[0][7]:
				style = placemark[0]
				name = placemark[1]
				desc = placemark[2]
				
				print('Updating ', name.text)
				
				if name.text == 'Data for postcode '+key:
					desc.set('respondents', str(postcodeList[key]['responses_total']))
					desc.set('symptom-score', str(postcodeList[key]['symptom_score']))
					desc.text = """<p>Data summary:</p>
									<table>
									<tr><td>Entries</td><td>{}</td></tr>
									<tr><td>Symptom score</td><td>{}</td></tr>
									</table>
									<p>The symptom score is calculated as the total of the symptom medians.</p>
								""".format(postcodeList[key]['responses_total'], postcodeList[key]['symptom_score'])
					
					if postcodeList[key]['symptom_score'] == 0:
						style.text = '#none'
					elif postcodeList[key]['symptom_score'] > 0 and postcodeList[key]['symptom_score'] < 1:
						style.text = '#green'
					elif postcodeList[key]['symptom_score'] >= 1 and postcodeList[key]['symptom_score'] < 2:
						style.text = '#yellow'
					elif postcodeList[key]['symptom_score'] >= 2 and postcodeList[key]['symptom_score'] < 3:
						style.text = '#orange'
					elif postcodeList[key]['symptom_score'] >= 3:
						style.text = '#red'
					
		tree.write('/var/www/html/bb/api/symptom_score.kml')
		
		# How feeling total
		ET.register_namespace('', "http://www.opengis.net/kml/2.2")
		tree = ET.parse('data/ukpostcodes_template.kml')
		root = tree.getroot()
		
		for key, value in postcodeList.items():
			for placemark in root[0][7]:
				style = placemark[0]
				name = placemark[1]
				desc = placemark[2]
				
				print('Updating ', name.text)
				
				if name.text == 'Data for postcode '+key:
					desc.set('respondents', str(postcodeList[key]['responses_total']))
					desc.set('symptom-score', str(postcodeList[key]['symptom_score']))
					desc.text = """<p>Data summary:</p>
									<table>
									<tr><td>Entries</td><td>{}</td></tr>
									<tr><td>How feeling median</td><td>{}</td></tr>
									</table>
								""".format(postcodeList[key]['responses_total'], postcodeList[key]['how_feeling_median'])
					
					if postcodeList[key]['how_feeling_median'] == 0:
						style.text = '#none'
					elif postcodeList[key]['how_feeling_median'] > 0 and postcodeList[key]['how_feeling_median'] < 1:
						style.text = '#green'
					elif postcodeList[key]['how_feeling_median'] >= 1 and postcodeList[key]['how_feeling_median'] < 2:
						style.text = '#yellow'
					elif postcodeList[key]['how_feeling_median'] >= 2 and postcodeList[key]['how_feeling_median'] < 3:
						style.text = '#orange'
					elif postcodeList[key]['how_feeling_median'] >= 3:
						style.text = '#red'
					
		tree.write('/var/www/html/bb/api/how_feeling_score.kml')
		
		# Nose total
		ET.register_namespace('', "http://www.opengis.net/kml/2.2")
		tree = ET.parse('data/ukpostcodes_template.kml')
		root = tree.getroot()
		
		for key, value in postcodeList.items():
			for placemark in root[0][7]:
				style = placemark[0]
				name = placemark[1]
				desc = placemark[2]
				
				print('Updating ', name.text)
				
				if name.text == 'Data for postcode '+key:
					desc.set('respondents', str(postcodeList[key]['responses_total']))
					desc.set('symptom-score', str(postcodeList[key]['symptom_score']))
					desc.text = """<p>Data summary:</p>
									<table>
									<tr><td>Entries</td><td>{}</td></tr>
									<tr><td>Nose median</td><td>{}</td></tr>
									</table>
								""".format(postcodeList[key]['responses_total'], postcodeList[key]['nose_median'])
					
					if postcodeList[key]['nose_median'] == 0:
						style.text = '#none'
					elif postcodeList[key]['nose_median'] > 0 and postcodeList[key]['nose_median'] < 1:
						style.text = '#green'
					elif postcodeList[key]['nose_median'] >= 1 and postcodeList[key]['nose_median'] < 2:
						style.text = '#yellow'
					elif postcodeList[key]['nose_median'] >= 2 and postcodeList[key]['nose_median'] < 3:
						style.text = '#orange'
					elif postcodeList[key]['nose_median'] >= 3:
						style.text = '#red'
					
		tree.write('/var/www/html/bb/api/nose_score.kml')
		
		# Eyes total
		ET.register_namespace('', "http://www.opengis.net/kml/2.2")
		tree = ET.parse('data/ukpostcodes_template.kml')
		root = tree.getroot()
		
		for key, value in postcodeList.items():
			for placemark in root[0][7]:
				style = placemark[0]
				name = placemark[1]
				desc = placemark[2]
				
				print('Updating ', name.text)
				
				if name.text == 'Data for postcode '+key:
					desc.set('respondents', str(postcodeList[key]['responses_total']))
					desc.set('symptom-score', str(postcodeList[key]['symptom_score']))
					desc.text = """<p>Data summary:</p>
									<table>
									<tr><td>Entries</td><td>{}</td></tr>
									<tr><td>Eyes median</td><td>{}</td></tr>
									</table>
								""".format(postcodeList[key]['responses_total'], postcodeList[key]['eyes_median'])
					
					if postcodeList[key]['eyes_median'] == 0:
						style.text = '#none'
					elif postcodeList[key]['eyes_median'] > 0 and postcodeList[key]['eyes_median'] < 1:
						style.text = '#green'
					elif postcodeList[key]['eyes_median'] >= 1 and postcodeList[key]['eyes_median'] < 2:
						style.text = '#yellow'
					elif postcodeList[key]['eyes_median'] >= 2 and postcodeList[key]['eyes_median'] < 3:
						style.text = '#orange'
					elif postcodeList[key]['eyes_median'] >= 3:
						style.text = '#red'
					
		tree.write('/var/www/html/bb/api/eyes_score.kml')
	
		# Breathing total
		ET.register_namespace('', "http://www.opengis.net/kml/2.2")
		tree = ET.parse('data/ukpostcodes_template.kml')
		root = tree.getroot()
		
		for key, value in postcodeList.items():
			for placemark in root[0][7]:
				style = placemark[0]
				name = placemark[1]
				desc = placemark[2]
				
				print('Updating ', name.text)
				
				if name.text == 'Data for postcode '+key:
					desc.set('respondents', str(postcodeList[key]['responses_total']))
					desc.set('symptom-score', str(postcodeList[key]['symptom_score']))
					desc.text = """<p>Data summary:</p>
									<table>
									<tr><td>Entries</td><td>{}</td></tr>
									<tr><td>Breathing median</td><td>{}</td></tr>
									</table>
								""".format(postcodeList[key]['responses_total'], postcodeList[key]['breathing_median'])
					
					if postcodeList[key]['breathing_median'] == 0:
						style.text = '#none'
					elif postcodeList[key]['breathing_median'] > 0 and postcodeList[key]['breathing_median'] < 1:
						style.text = '#green'
					elif postcodeList[key]['breathing_median'] >= 1 and postcodeList[key]['breathing_median'] < 2:
						style.text = '#yellow'
					elif postcodeList[key]['breathing_median'] >= 2 and postcodeList[key]['breathing_median'] < 3:
						style.text = '#orange'
					elif postcodeList[key]['breathing_median'] >= 3:
						style.text = '#red'
					
		tree.write('/var/www/html/bb/api/breathing_score.kml')
		
	def getConfig(self):
		# Get the config file details (database login)
		d = {}
		with open("./config.ini") as f:
			for line in f:
			   (key, val) = line.split(':')
			   d[key] = val.replace('\n', '').strip()
			   
		return d
	

BBAPI()
