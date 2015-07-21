# !/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Name          : Address Cleaner
# Author  		: Mark Pooley (mark-pooley@uiowa.edu)
# Link    		: http://www.ppc.uiowa.edu
# Date    		: 2015-02-17 10:10:11
# Version		: $1.1$
# Description	: Clean table with 2 address fields. Fields are compared for length and checked for
# for occurence of PO Box in the address field. Checks to make sure the correct address has digits in
# it as well. Leading spaces and '#' characters are removed from # the correct address.
#
# Instances where the correct address is only a PO Box are omitted
#-------------------------------------------------------------------------------------------------

###################################################################################################
#Import python modules
###################################################################################################
import os
import arcpy
from arcpy import env


###################################################################################################
#Input Variable loading and environment declaration
###################################################################################################
TableInput= arcpy.GetParameterAsText(0)
Address1 = arcpy.GetParameterAsText(1)
Address2 = arcpy.GetParameterAsText(2)
statefield = arcpy.GetParameterAsText(3)
POBoxDelete = arcpy.GetParameterAsText(4).capitalize()
NonIowa = arcpy.GetParameterAsText(5).capitalize() #remove non Iowa States
KeepBorders = arcpy.GetParameterAsText(6).capitalize() #boolean to keep only border states

arcpy.AddMessage('User selected PO Boxes to be deleted: {0}'.format(POBoxDelete.title()))


###################################################################################################
# Defining global functions
###################################################################################################
#compare address lengths, whichever is longer is likey to be the correct address. Return the longer
#of the two with leading # and spaces stripped
def addresscleaner(addr1,addr2):

	if addr1 == None:
		correct = str(addr2).lstrip(' #')
	elif addr2 == None:
		correct = str(addr1).lstrip(' #')
	#-------------------------------------------------------------------------------------------
	#check for instance of PO Box by stripping spaces and converting all letters to lower case
	#-------------------------------------------------------------------------------------------
	elif len(addr1) > len(addr2) and 'pobox' not in str(addr1).translate(None,' .').lower():
		#make sure addr1 has digits in it, if not default to addr2
		if any(x.isdigit() for x in addr1) == True:
			correct = str(addr1).lstrip(' #')
		else:
			correct = str(addr2).lstrip(' #')
	else:
		#check that address2 has digits in it, if not default to addr1
		if any(x.isdigit() for x in addr2):
			correct = str(addr2).lstrip(' #')
		else:
			correct = str(addr1).lstrip(' #')

	return correct

###################################################################################################
#Add 'street_corrected' field if it's not already in the table
###################################################################################################
if "Street_Corrected" not in [f.name for f in arcpy.ListFields(TableInput)]:
	arcpy.AddField_management(TableInput,"Street_Corrected","TEXT")
StreetCorrected = "Street_Corrected"

###################################################################################################
#Find the correct address from the two original address fields
###################################################################################################
featureCount = int(arcpy.GetCount_management(TableInput).getOutput(0))
arcpy.AddMessage('Total Number of Entries in Dataset: {0}'.format(featureCount))
arcpy.SetProgressor("step","finding correct address for each line....",0,featureCount,1)

with arcpy.da.UpdateCursor(TableInput,[Address1,Address2,StreetCorrected]) as cursor:
	for row in cursor:
		addr = addresscleaner(row[0],row[1])
		row[2] = addr
		arcpy.SetProgressorLabel('correct address: {0}'.format(addr))
		cursor.updateRow(row)
		arcpy.SetProgressorPosition()

####################################################################################################
#If user checked option to delete PO Boxes, this will take care of that
####################################################################################################

if bool(POBoxDelete):
	arcpy.SetProgressor('step','Deleting lines with only a PO Box for address...',0,featureCount,1)
	deleteCount = 0
	with arcpy.da.UpdateCursor(TableInput,'Street_Corrected') as cursor:
		for row in cursor:
			if 'pobox' in row[0].replace(' ','').lower():
				cursor.deleteRow()
				deleteCount += 1
			arcpy.SetProgressorPosition()

	arcpy.AddMessage('{0} PO Box entries deleted from dataset...'.format(deleteCount))

####################################################################################################
#If user selects to delete non Iowa States, they are deleted in this process
####################################################################################################
if bool(NonIowa):
	#get state field name from input
	state = [f.name for f in arcpy.ListFields(TableInput) if 'state' in f.name.lower()][0]

	arcpy.SetProgressor('step','Deleting lines where state is not Iowa...',0,featureCount,1)
	deleteCount = 0
	with arcpy.da.UpdateCursor(TableInput,state) as cursor:
		for row in cursor:
			if 'IA' not in row[0].upper():
				cursor.deleteRow()
				deleteCount += 1
			arcpy.SetProgressorPosition()

	arcpy.AddMessage('{0} entries deleted from dataset...'.format(deleteCount))

####################################################################################################
#Keep only IA and border states
####################################################################################################
if bool(KeepBorders):
	states = ['IA','MN','WI','IL','MO','NE','SD']

	arcpy.SetProgressor('step','Removing all states that do not border Iowa...',0,featureCount,1)
	deleteCount = 0
	with arcpy.da.UpdateCursor(TableInput,statefield) as cursor:
		for row in cursor:
			if row[0] not in states:
				deleteCount += 1
				cursor.deleteRow()
			arcpy.SetProgressorPosition()

	arcpy.AddMessage('{0} non border states deleted from dataset...'.format(deleteCount))
####################################################################################################
#Final Output and cleaning of temp data/variables
####################################################################################################
arcpy.AddMessage("Process complete!")