# !/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Name          :Address Finder.py
# Author  		: Mark Pooley (mark-pooley@uiowa.edu)
# Link    		: http://www.ppc.uiowa.edu
# Date    		: 2015-02-17 16:47:07
# Version		: $1.0$
# Description	: Takes a Geocoding result and locates all unmatched/unlocated addresses using
# pygeocoder or geopy depending on the number of unmatched locations.  A new table is output to the
# same working directory as the input Locations so  'Display XY events' can be used.
#-------------------------------------------------------------------------------------------------

###################################################################################################
#Import python modules
###################################################################################################
import os
import time
import arcpy
from arcpy import env
import geocoder
from collections import defaultdict


###################################################################################################
#Input Variable loading and environment declaration
###################################################################################################
Locations = arcpy.GetParameterAsText(0)
MatchStatus = arcpy.GetParameterAsText(1)
MatchAddress = arcpy.GetParameterAsText(2)
Address = arcpy.GetParameterAsText(3)
city = arcpy.GetParameterAsText(4)
state = arcpy.GetParameterAsText(5)
zipCode = arcpy.GetParameterAsText(6)

###################################################################################################
#Global Variables
###################################################################################################
#Create a dictionary to save on queries
AddressDict = defaultdict(list) #dictionary for storing all the geocoded addresses
repeatCount = 0 #count repeats
totalLocated = 0 #count total located
stDict = {
	'IA': 'Iowa',
	'MN': 'Minnesota',
	'WI': 'Wisconsin',
	'IL': 'Illinois',
	'MO': 'Missouri',
	'NE': 'Nebraksa',
	'SD': 'South Dakota',
}
qualList = ['StreetName','StreetAddress','PointAddress'] #list of acceptable goecoding resolution qualities
###################################################################################################
#Geocode the unlocated features using a list of geocoders - looking for the highest resoluation
#match among them. If all the the geocoders area attempted and still no good match is found, then
#the entry will remain unlocated
###################################################################################################

featureCount = int(arcpy.GetCount_management(Locations).getOutput(0))

arcpy.SetProgressor('step','finding locations with city address type...',0,featureCount,1)
with arcpy.da.UpdateCursor(Locations,[MatchStatus,"X","Y",Address,city,state,zipCode,MatchAddress,"Addr_type"]) as cursor:
	for row in cursor:

		#check if row has unmatched status
		if row[0] == 'U':
			addr = "{0}, {1} {2} {3}".format(row[3], row[4], row[5], int(row[6]))

			#-------------------------------------------------------------------------------------------
			#Check if the current address is in the dictionary. If it isn't, go ahead and geocode it.
			#-------------------------------------------------------------------------------------------
			if not AddressDict[addr]:
				arcpy.SetProgressorLabel('Locating {0}'.format(addr))


				loc = geocoder.arcgis(addr)
				st = stDict[row[5]]
				z = str(row[6])
				#check that the quality is sufficient, and zip code and state match the current candidate location
				if loc.quality in qualList: #and loc.postal == z: #and st == loc.address.split(',')[-2].strip():

					arcpy.SetProgressorLabel('Match found for {0}'.format(addr))

					row[2] = loc.lat
					row[1] = loc.lng
					row[0] = 'M'
					row[7] = loc.address
					row[8] = loc.quality

					cursor.updateRow(row)

					#add geocoded address to dictionary with long and lat using the 'extend' method
					AddressDict[addr].extend((loc.address,loc.lat,loc.lng,loc.quality))
					arcpy.SetProgressorLabel('found correct address for: {0}'.format(addr))
					totalLocated += 1
				else:
					arcpy.AddMessage('no suitable address was found for {0}'.format(loc.address))
					pass

			#If first for loop not entered, then the address is a repeat. Simply use the
			#Dictionary to update the address field
			#---------------------------------------------------------------------------
			else:
				arcpy.SetProgressorLabel('{0} is a repeat, using dictionary....'.format(addr))
				row[2] = AddressDict[addr][1]
				row[1] = AddressDict[addr][2]
				row[0] = 'M'
				row[7] = AddressDict[addr][0]
				row[8] = AddressDict[addr][3]

				cursor.updateRow(row)

				arcpy.SetProgressorLabel('Match found for {0}'.format(AddressDict[addr]))
				repeatCount += 1 #update the number of repeats found

				totalLocated += 1 #update the total located number

		#simply pass rows that have been located
		else:
			pass
		arcpy.SetProgressorPosition()


###################################################################################################
#export new table with XY data
###################################################################################################
basename = os.path.basename(Locations)
output = basename + "_Located"
path = os.path.dirname(Locations)

arcpy.SetProgressorLabel('exporting attribute table to {0}\nTable name: {1}'.format(path,output))
arcpy.TableToTable_conversion(Locations,path,output)

###################################################################################################
#Final Output and cleaning of temp data/variables
###################################################################################################


arcpy.AddMessage('{0} total addresses located'.format(totalLocated))
arcpy.AddMessage('{0} repeats were found in the unlocated addresses'.format(repeatCount))
arcpy.AddMessage('New table location: {0}\nTable name: {1}'.format(path,output))
arcpy.AddMessage("Process complete!")


