# !/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Name          : Duplicate Address Finder
# Author  		: Mark Pooley (mark-pooley@uiowa.edu)
# Github		: http://github.com/markpooley
# Link    		: http://www.ppc.uiowa.edu
# Date    		: 2015-05-06
# Version		: 1.0
# Description	: Takes an address and creates uniform/standard directions, street abbreviations, and
# omits certain identifiers (i.e. po box)
#--------------------------------------------------------------------------------------------------

###################################################################################################
#Import python modules
###################################################################################################
import os
import arcpy
from arcpy import env
from operator import itemgetter
from collections import defaultdict

###################################################################################################
#Input Variable loading and environment declaration
###################################################################################################
inTable = arcpy.GetParameterAsText(0)#input table of addresses
addrField = arcpy.GetParameterAsText(1)#address field

###################################################################################################
#Global variables to be used in process
###################################################################################################
omitList = ['po box','ste','suite', 'box']

dirDict = {
	'N': 'NORTH',
	'S': 'SOUTH',
	'E': 'EAST',
	'W': 'WEST',
	'NE': 'NORTHEAST',
	'SE': 'SOUTHEAST',
	'SW': 'SOUTHWEST',
	'NW': 'NORTHWEST'
}
stDict = {
	'STREET': 'ST',
	'AVENUE': 'AVE',
	'ROAD': 'RD',
	'COURT': 'CT',
	'DRIVE': 'DR'
}
###################################################################################################
# Defining global functions
###################################################################################################

#function to look for any address elements to omit
def omit(addr):
	try:
		if any(x in addr.lower() for x in omitList):
			for i in omitList:
				if i in addr.lower():
					addr = addr[addr.lower().index(i):]
	except:
		pass

	return addr

#function to look for any directions and correct them to a consistent abbreviation
def direction(addr):
	try:
		for k, v in dirDict.iteritems():
		    if v in addr:
		        addr = addr.replace(v,k)
	except:
		pass

	return addr

# function to look for street names/identifiers and correct them to a consistent abbreviation
def stCorrect(addr):
	try:
		for k, v in stDict.iteritems():
		    if k in addr:
		        addr = addr.replace(k,v)
	except:
		pass
	return addr
###################################################################################################
#update cursor to look through address field and make corrections
###################################################################################################
featureCount = int(arcpy.GetCount_management(inTable).getOutput(0))
arcpy.SetProgressor('step','looking through addresses to make corrections',0,featureCount,1)
with arcpy.da.UpdateCursor(inTable,addrField) as cursor:
	for row in cursor:
		try:
			addr = row[0].upper() #conver tot upper case
			addr = omit(addr)
			addr = direction(addr)
			addr = stCorrect(addr)
			row[0] = addr
			arcpy.SetProgressorPosition()
			cursor.updateRow(row)
		except:
			pass

###################################################################################################
#Final Output and cleaning of temp data/variables
###################################################################################################
arcpy.AddMessage("Process complete!")
