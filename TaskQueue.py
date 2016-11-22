#!/usr/bin/env python3.4
'''
FILENAME... recon
USAGE...    Script for tomography at IMX
/*
 *      Original Author: IMX Beamline Group
 *      Date: 10/10/2016
 */
'''

import os
import time
import re
from epics import PV
import PVNames
import sys



###########################################################################
#
# DEFINITIONS
#
###########################################################################
#pvRLoc = PV(PVNames.detectorRLoc)
#pvRUserName = PV(PVNames.detectorRUserName)
#pvRExpPath = PV(PVNames.detectorRExpPath)
#pvReconPath = PV(PVNames.detectorReconPath)
#error8 = PV(PVNames.Error8)
#error9 = PV(PVNames.Error9)
#pvrAxis = PV(PVNames.rAxis)
#pvsSlice = PV(PVNames.sSlice)
#pveSlice = PV(PVNames.eSlice)
#pvreconWait = PV(PVNames.reconWait)
#pvPsize = PV(PVNames.pSize)
pvQueueWait = PV(PVNames.queueWait)
pvRecon = PV(PVNames.detectorRecon)
pvTomoWait = PV(PVNames.tomoWait)
pvError7 = PV(PVNames.error7)
pvTaskWait = PV(PVNames.taskWait)


#os.chdir('/home/ABTLUS/userimx/Scripts_Recon/Queue')



### READING LINES ###

def readLines():

	f=open('/usr/local/scripts/Robot/Tasks.par', 'r')

	lines = f.readlines()

	f.close()

	if lines:
		for x in lines:
			if '1 -' in x:
				l=x


	else:
		print('\n\nQueue Empty\n\n')
		l=0

	return l,lines


### DELETE LINE ###

def deleteLine():
	
	f=open('/usr/local/scripts/Robot/Tasks.par', 'r')
	
	lines = f.readlines()
	
	f.close()

	
	y=[]
	
	for x in lines:
		if '1 - ' in x:
			pass

		else:
				position = re.search('%s(.*)%s' % ('', ' - '), x).group(1)
				position = str(int(position)-1)			
				x = x.split(' - ')
				line = x[1]
		
				y.append(position + ' - ' + line)
				
	f=open('/usr/local/scripts/Robot/Tasks.par', 'w')
	
	for z in y:
		f.write(z)
		
	f.close()
	

### GET PARAMETERS ###

def getParameters(l):

	SampleNumber = re.search('%s(.*)%s' % (' - SAMPLE #: ', ' Path:'), l).group(1)
	SampleNumber = SampleNumber.replace(' |','')
	
	Path = re.search('%s(.*)%s' % ('Path: ', ' Snap'), l).group(1)
	Path = Path.replace(' |','')
	
	Path = Path.split('/')
	
	SampleName = Path[-1]
	
	del Path[-1]
	
	Path = '/'.join(Path)+'/'
		
	Snap = re.search('%s(.*)%s' % ('Snap = ', ' Corrected = '), l).group(1)
	Snap = Snap.replace('  |', '')
				
	Corrected = re.search('%s(.*)%s' % ('Corrected = ', ' Tomography = '), l).group(1)
	Corrected = Corrected.replace('  |', '')
				
	Tomography = re.search('%s(.*)%s' % ('Tomography = ', '    '), l).group(1)
				
	if len(Tomography)>=20:
		Tomography = 'YES'
					
		Range = re.search('%s(.*)%s' % ('Range: ', ' ,  # Projections: '), l).group(1)
		Range = Range.split('-')
			
		StartAngle = str(int(Range[0]))
		FinalAngle = str(int(Range[1]))
					
		NProjections = re.search('%s(.*)%s' % ('# Projections: ', '    '), l).group(1)
		NProjections=NProjections.replace(') |','')
			
	else:
		Tomography = 'NO'


	if Tomography=='YES':
		return SampleNumber, Path, SampleName, Snap, Corrected, Tomography, StartAngle, FinalAngle, NProjections
		
	else:
		return SampleNumber, Path, SampleName, Snap, Corrected, Tomography
		
		
		
### ADD RECON ###

###################################################################################################################################################################################################################
#1 - Path: /ddn/IMX/IMXTemp/20160582/A.Thaliana_Experiment/Sample#3, ReconMod: PyRaft, Start Slice: 1, End Slice: 2048, Regularization: 0.0, Composition Factor: 1, Threshold MAX: 20, Threshold MIN: -20

def AddRecon(Path, SampleName):
	
	f = open('/storage/Queue/Queue.par', 'r')
	lines = f.readlines()
	f.close()
	
	if lines:
		Position = re.search('%s(.*)%s' % ('', ' - '), lines[-1]).group(1)
		lines.append(lines[0])

		NewLine = str(int(Position)+1) + ' - Path: ' + Path + SampleName + ', ReconMod: PyRaft, Start Slice: 1, End Slice: 2048, Regularization: 0.0, Composition Factor: 1, Threshold MAX: 20, Threshold MIN: -20\n'
		
		lines.append(NewLine)


	else:
		lines=[]
		lines.append('###################################################################################################################################################################################################################\n')
		lines.append('1 - Path: ' + Path + SampleName + ', ReconMod: PyRaft, Start Slice: 1, End Slice: 2048, Regularization: 0.0, Composition Factor: 1, Threshold MAX: 20, Threshold MIN: -20\n')

	f = open('/storage/Queue/Queue.par', 'w')
	for x in lines:
		f.write(x)
	f.close()
	
	pvQueueWait.put(0)
	time.sleep(.5)
	pvQueueWait.put(1)


### SEND EMAIL ###

def sendEmail(Samples, Email):
	gmail_user = 'imxbeamline@gmail.com'
	gmail_pwd = 'syncro!14'
	FROM = 'IMX Beamline'
	recipient = Email
	TO = recipient if type(recipient) is list else [recipient]
	SUBJECT = 'Recon Queue Finished'
	
	Paths = ''

	for t in Samples:
		Paths=Paths+'\n\n'+t

	TEXT = 'Your Recon Queue has finished with the following samples:' + Paths + '\n\n' + "\n\nDON'T REPLY THIS EMAIL\n\n" +'\nIMX Beamline Group\n' + 'Brazilian Synchrotron Light Source - LNLS\n'

	# Prepare actual message
	message = """From: %s\nTo: %s\nSubject: %s\n\n%s
	""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
	try:
		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(gmail_user, gmail_pwd)
		server.sendmail(FROM, TO, message)
		server.close()
		print ('\nSuccessfully sent the mail\n')
	except:
		print ('\nFailed to send mail\n')




###MAIN PROGRAM###
if __name__ == '__main__':

	AutomaticRecon = float(sys.argv[1])
	
	pvTaskWait.put(1)

	l, lines = readLines()
	
	Samples=[]

	while len(lines)>0:	

		deleteLine()

		if 'Tomography = YES' in l:
				SampleNumber, Path, SampleName, Snap, Corrected, Tomography, StartAngle, FinalAngle, NProjections = getParameters(l)

				#print ('\n\n\n\n####### SAMPLE: ' + SampleName + ' ####### \n')

				os.chdir(Path)
				
				msg = 'Sample: ' + SampleNumber + ' -> Creating sample ' + SampleName + ' in ' + Path
				msg=str.encode(msg)
				pvError7.put(msg)				
				#print ('\n\nCreating New Sample...\n')																		
				os.system('/usr/local/scripts/IMX_craft_sample -n '+ SampleName +' Using_ROBOT')										### CREATE NEW SAMPLE


				msg = 'Sample: ' + SampleNumber + ' -> Moving Robot'
				msg=str.encode(msg)
				pvError7.put(msg)
				#print ('\n\nMoving Robot...\n')
				os.system('/usr/local/scripts/Robot/RobotControl.py 0 ' + str(int(SampleNumber)))														### MOVE ROBOT

				msg = 'Sample: ' + SampleNumber + ' -> Doing Alignment of ' + SampleName
				msg=str.encode(msg)
				pvError7.put(msg)
				#print ('\n\nDoing Alignment...\n')
				#os.system('/usr/local/scripts/Robot/alignSampleRobot.py')																### DO ALIGNMENT					
				os.system('/usr/local/scripts/alignSample')
				
								
				if Corrected == 'YES':
					msg = 'Sample: ' + SampleNumber + ' -> Taking Corrected of ' + SampleName
					msg=str.encode(msg)
					pvError7.put(msg)
					#print ('\n\nTaking Corrected...\n')
					os.system('/usr/local/scripts/snapWithCorrection')																	### TAKE CORRECTED
					
				if Snap == 'YES':
					msg = 'Sample: ' + SampleNumber + ' -> Taking Snap of ' + SampleName
					msg=str.encode(msg)
					pvError7.put(msg)
					#print ('\n\nTaking Snap...\n')
					os.system('/usr/local/scripts/snap')																				### TAKE SNAP
					
				msg = 'Sample: ' + SampleNumber + ' -> Doing Tomography of ' + SampleName + '\nAngle Range: ' +  StartAngle + ' - ' + FinalAngle + '\nNumber of images: ' + NProjections 
				msg=str.encode(msg)
				pvError7.put(msg)
				#print ('\n\nDoing Tomo...\n')
				pvRecon.put(0)																											### DO/DON'T RECON
				os.system('/usr/local/scripts/tomo '+ StartAngle + ' ' + FinalAngle + ' ' + NProjections +' 1024 1024')					### DO TOMO
				
				if AutomaticRecon==1:
					AddRecon(Path, SampleName)
					
				msg = 'Sample: ' + SampleNumber + ' -> Moving Robot'
				msg=str.encode(msg)
				pvError7.put(msg)
				#print ('\n\nMoving Robot...\n')
				os.system('/usr/local/scripts/Robot/RobotControl.py 1 ' + str(int(SampleNumber)))														### MOVE ROBOT
		
		if 'Tomography = NO' in l:
				SampleNumber, Path, SampleName, Snap, Corrected, Tomography = getParameters(l)

				#print ('\n\n\n\n####### SAMPLE: ' + SampleName + '####### \n')

				os.chdir(Path)
				msg = 'Sample: ' + SampleNumber + ' -> Creating sample ' + SampleName + ' in ' + Path
				msg=str.encode(msg)
				pvError7.put(msg)		
				#print ('\n\nCreating New Sample...\n')																		
				os.system('/usr/local/scripts/IMX_craft_sample -n '+ SampleName +' Using_ROBOT')										### CREATE NEW SAMPLE

				msg = 'Sample: ' + SampleNumber + ' -> Moving Robot'
				msg=str.encode(msg)
				pvError7.put(msg)
				#print ('\n\nMoving Robot...\n')
				os.system('/usr/local/scripts/Robot/RobotControl.py 0 ' + str(int(SampleNumber)))														### MOVE ROBOT

				msg = 'Sample: ' + SampleNumber + ' -> Doing Alignment of ' + SampleName
				msg=str.encode(msg)
				pvError7.put(msg)
				#print ('\n\nDoing Alignment...\n')
				#os.system('/usr/local/scripts/Robot/alignSampleRobot.py')																### DO ALIGNMENT
				os.system('/usr/local/scripts/alignSample')
								
				if Corrected == 'YES':
					msg = 'Sample: ' + SampleNumber + ' -> Taking Corrected of ' + SampleName
					msg=str.encode(msg)
					pvError7.put(msg)
					#print ('\n\nTaking Corrected...\n')
					os.system('/usr/local/scripts/snapWithCorrection')																	### TAKE CORRECTED
					
				if Snap == 'YES':
					msg = 'Sample: ' + SampleNumber + ' -> Taking Snap of ' + SampleName
					msg=str.encode(msg)
					pvError7.put(msg)
					#print ('\n\nTaking Snap...\n')
					os.system('/usr/local/scripts/snap')																				### TAKE SNAP


				msg = 'Sample: ' + SampleNumber + ' -> Moving Robot'
				msg=str.encode(msg)
				pvError7.put(msg)
				print ('\n\nMoving Robot...\n')
				os.system('/usr/local/scripts/Robot/RobotControl.py 1 ' + str(int(SampleNumber)))														### MOVE ROBOT



		l, lines = readLines()
		
	pvTaskWait.put(0)


	#SendEmail = int(sys.argv[1])

	#if (SendEmail==1):
		#Email = str(sys.argv[2])
		#sendEmail(Samples, Email)
	







