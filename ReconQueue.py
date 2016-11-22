#!/usr/bin/env python3.4
'''
FILENAME... recon
USAGE...    Script for reconstruction queue at IMX
/*
 *      Original Author: IMX Beamline Group
 *      Date: 02/05/2016
 */
'''

import os
import subprocess
import time
import re
from epics import PV
import PVNames
import paramiko
import smtplib
import sys



###########################################################################
#
# DEFINITIONS
#
###########################################################################
pvRLoc = PV(PVNames.detectorRLoc)
pvRUserName = PV(PVNames.detectorRUserName)
pvRExpPath = PV(PVNames.detectorRExpPath)
pvReconPath = PV(PVNames.detectorReconPath)
error8 = PV(PVNames.Error8)
error9 = PV(PVNames.Error9)
pvrAxis = PV(PVNames.rAxis)
pvsSlice = PV(PVNames.sSlice)
pveSlice = PV(PVNames.eSlice)
pvreconWait = PV(PVNames.reconWait)
pvPsize = PV(PVNames.pSize)
pvQueueWait = PV(PVNames.queueWait)


#os.chdir('/home/ABTLUS/userimx/Scripts_Recon/Queue')



### READING LINES ###
def readLines():

	f=open('/storage/Queue/Queue.par', 'r')	
	#f=open('/home/ABTLUS/userimx/Scripts_Recon/Queue/Queue.par', 'r')

	lines = f.readlines()

	f.close()

	if lines:
		for x in lines:
			if '1 -' in x:
				if 'PyHST' in x:
					Path = re.search('%s(.*)%s' % ('Path: ', ', ReconMod:'), x).group(1)
					sSlice = re.search('%s(.*)%s' % ('Start Slice: ', ', End Slice:'), x).group(1)
					eSlice = re.search('%s(.*)%s' % ('End Slice: ', ', CCD Filter'), x).group(1)
					ReconMOD = 'PyHST'	

				if 'PyRaft' in x:
					Path = re.search('%s(.*)%s' % ('Path: ', ', ReconMod:'), x).group(1)
					sSlice = re.search('%s(.*)%s' % ('Start Slice: ', ', End Slice:'), x).group(1)
					eSlice = re.search('%s(.*)%s' % ('End Slice: ', ', Regularization:'), x).group(1)
					ReconMOD = 'PyRaft'	

				nSlices = (int(eSlice) - int(sSlice)) + 1

				l=x
				pvQueueWait.put(1)
				msg = 'Recon Started using ' + ReconMOD + ' at ' + time.strftime("%H:%M - %d-%m-%Y") + '\n' + 'With ' + str(nSlices) + ' slice(s)\n' + 'Path: ' + Path
				error9.put(msg)
				#print('\n',msg,'\n\n')


	else:
		print('\n\nQueue Empty\n\n')
		l=0
		pvQueueWait.put(0)


	return l,lines





### DELETE LINE ###
def deleteLine():
	
	f=open('/storage/Queue/Queue.par', 'r+')
	#f=open('/home/ABTLUS/userimx/Scripts_Recon/Queue/Queue.par', 'r+')

	lines = f.readlines()

	f.seek(0)
	f.truncate()

	del lines[0:2]

	for x in lines:
		if ' - ' in x:
			position = re.search('%s(.*)%s' % ('', ' - '), x).group(1)
			position = str(int(position)-1)			
			line = re.search('%s(.*)%s' % ('- ', '\n'), x).group(1)
		
			f.write(position + ' - ' + line + '\n')
		
		else:
			f.write(x)


	f.close()



### GET PARAMETERS ###
def getParametersPyHST(l):

	Path = re.search('%s(.*)%s' % ('Path: ', ', ReconMod:'), l).group(1)
	#print (Path+'\n')

	rAxis = re.search('%s(.*)%s' % ('Rot Axis: ', ', Start Slice:'), l).group(1)
	#print (rAxis+'\n')

	sSlice = re.search('%s(.*)%s' % ('Start Slice: ', ', End Slice:'), l).group(1)
	#print (sSlice+'\n')

	eSlice = re.search('%s(.*)%s' % ('End Slice: ', ', CCD Filter'), l).group(1)
	#print (eSlice+'\n')

	if 'CCD Filter OFF' in l:
		CCDFilter = str(0)
		#print (CCDFilter+'\n')
		CCDFilterThres = re.search('%s(.*)%s' % ('CCD Filter OFF(', '), Ring Filter'), l).group(1)
		CCDFilterThres = re.search('%s(.*)%s' % ('( ', ' )'), CCDFilterThres).group(1)
		CCDFilterThres = re.search('%s(.*)%s' % (' ', ' '), CCDFilterThres).group(1)
		#print (CCDFilterThres+'\n')

	if 'CCD Filter ON' in l:
		CCDFilter = str(1)
		#print (CCDFilter+'\n')
		CCDFilterThres = re.search('%s(.*)%s' % ('CCD Filter ON(', '), Ring Filter'), l).group(1)
		CCDFilterThres = re.search('%s(.*)%s' % ('( ', ' )'), CCDFilterThres).group(1)
		CCDFilterThres = re.search('%s(.*)%s' % (' ', ' '), CCDFilterThres).group(1)
		#print (CCDFilterThres+'\n')


	if 'Ring Filter OFF' in l:
		RingFilter = str(0)
		#print (RingFilter+'\n')
		RingFilterThres = re.search('%s(.*)%s' % ('Ring Filter OFF(', '), Paganin Filter'), l).group(1)
		RingFilterThres = re.search('%s(.*)%s' % ('( ', ' )'), RingFilterThres).group(1)
		RingFilterThres = re.search('%s(.*)%s' % (' ', ' '), RingFilterThres).group(1)
		#print (RingFilterThres+'\n')

	if 'Ring Filter ON' in l:
		RingFilter = str(1)
		#print (RingFilter+'\n')
		RingFilterThres = re.search('%s(.*)%s' % ('Ring Filter ON(', '), Paganin Filter'), l).group(1)
		RingFilterThres = re.search('%s(.*)%s' % ('( ', ' )'), RingFilterThres).group(1)
		RingFilterThres = re.search('%s(.*)%s' % (' ', ' '), RingFilterThres).group(1)
		#print (RingFilterThres+'\n')


	if 'Paganin Filter OFF' in l:
		PaganinFilter = str(0)
		#print (PaganinFilter+'\n')
		PaganinFilterThres = re.search('%s(.*)%s' % ('Paganin Filter OFF(', ')'), l).group(1)
		PaganinFilterThres = re.search('%s(.*)%s' % ('( ', ' )'), PaganinFilterThres).group(1)
		PaganinFilterThres = re.search('%s(.*)%s' % (' ', ' '), PaganinFilterThres).group(1)
		#print (PaganinFilterThres+'\n')

	if 'Paganin Filter ON' in l:
		PaganinFilter = str(1)
		#print (PaganinFilter+'\n')
		PaganinFilterThres = re.search('%s(.*)%s' % ('Paganin Filter ON(', ')'), l).group(1)
		PaganinFilterThres = re.search('%s(.*)%s' % ('( ', ' )'), PaganinFilterThres).group(1)
		PaganinFilterThres = re.search('%s(.*)%s' % (' ', ' '), PaganinFilterThres).group(1)			
		#print (PaganinFilterThres+'\n')


	return(Path, rAxis, sSlice, eSlice, CCDFilter, CCDFilterThres, RingFilter, RingFilterThres, PaganinFilter, PaganinFilterThres)




def getParametersPyRaft(l):

	Path = re.search('%s(.*)%s' % ('Path: ', ', ReconMod:'), l).group(1)
	#print (Path+'\n')

	sSlice = re.search('%s(.*)%s' % ('Start Slice: ', ', End Slice:'), l).group(1)
	#print (sSlice+'\n')

	eSlice = re.search('%s(.*)%s' % ('End Slice: ', ', Regularization:'), l).group(1)
	#print (eSlice+'\n')

	Regularization = re.search('%s(.*)%s' % ('Regularization: ', ', Composition Factor:'), l).group(1)
	#print (Regularization+'\n')

	Regularization = (float(Regularization)/100000)

	Composition = re.search('%s(.*)%s' % ('Composition Factor: ', ', Threshold:'), l).group(1)
	#print (Composition+'\n')

	Threshold = re.search('%s(.*)%s' % ('Threshold: ', ', Image Size:'), l).group(1)
	#print (Threshold+'\n')

	ImageSize = re.search('%s(.*)%s' % ('Image Size: ', ', Image Format:'), l).group(1)
	#print (ImageSize+'\n')

	ImageFormat = re.search('%s(.*)%s' % ('Image Format: ', ', Blocks Number:'), l).group(1)
	#print (ImageFormat+'\n')

	BlocksNumber = re.search('%s(.*)%s' % ('Blocks Number: ', ', GPU Number:'), l).group(1)
	#print (BlocksNumber+'\n')

	aRange = re.search('%s(.*)%s' % ('Angle Range: ', '\n'), l).group(1)
	#print (aRange+'\n')

	if float(aRange)==360:
		GPUNumber = re.search('%s(.*)%s' % ('GPU Number: ', ', Centering:'), l).group(1)
		#print (GPUNumber+'\n')

		Centering = re.search('%s(.*)%s' % ('Centering: ', ', Shift:'), l).group(1)
		#print (Centering+'\n')

		Shift = re.search('%s(.*)%s' % ('Shift: ', ', Angle Range:'), l).group(1)
		#print (Shift+'\n')

	else:
		GPUNumber = re.search('%s(.*)%s' % ('GPU Number: ', ', Shift:'), l).group(1)
		#print (GPUNumber+'\n')

		Centering = 0
		#print (str(Centering)+'\n')

		Shift = re.search('%s(.*)%s' % ('Shift: ', ', Angle Range:'), l).group(1)
		#print (Shift+'\n')


	return(Path, sSlice, eSlice, Regularization, Composition, Threshold, ImageSize, ImageFormat, BlocksNumber, GPUNumber, Centering, Shift, aRange)



### DO THE RECON WITH PYHST ###
def reconStartPyHST(Path, rAxisNew, sSliceNew, eSliceNew, ccdFilterNew, ccdFilterThresNew, ringFilterNew, ringFilterThresNew, pagFilterNew, pagFilterThresNew, pSize):

	nSlices = (int(eSliceNew) - int(sSliceNew)) +1


	sftpURL   =  '10.2.105.181'
	sftpUser  =  '******'
	sftpPass  =  '******'


	ssh = paramiko.SSHClient()
	# automatically add keys without requiring human intervention
	ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

	ssh.connect(sftpURL, username=sftpUser, password=sftpPass)

	sftp_client=ssh.open_sftp()

	path="cd /" + Path + "; ls"

	stdin, stdout, stderr = ssh.exec_command(path)

	pvQueueWait.put(1)

	x=[]

	while True:
		line = stdout.readline()
		line = line.replace('\n','')

		if line != '':
			x.append(line)    

		else:
			break

	path2 = Path + "/"

	if 'input.par' in x:

		path3= Path + "/input.par"
		path4= Path + "/arquivo.par"

		inputpar=sftp_client.open(path3, '+r')
		arquivopar=sftp_client.open(path4, '+w')
			
		try:
			words = ['ROTATION_AXIS_POSITION', 'START_VOXEL_3', 'END_VOXEL_3', 'DO_RING_FILTER', 'DO_PAGANIN', 'DO_CCD_FILTER', 'CCD_FILTER_PARA', 'RING_FILTER_PARA', 'PAGANIN_Lmicron', 'PAGANIN_MARGE']


			#with sftp_client.open(path3, 'wb') as oldfile, sftp_client.open(path4, 'wb') as newfile:
			for line in inputpar:
		            
				if not any(word in line for word in words):
					arquivopar.write(line)
		        
				if (words[0] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[0]+' = %0.2f \n' %float(rAxisNew))
					else:
						arquivopar.write(line)
		        
				if (words[1] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[1]+' = %d \n' %int(sSliceNew))
					else:
						arquivopar.write(line)

	
				if (words[2] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[2]+' = %d \n' %int(eSliceNew))
					else:
						arquivopar.write(line)


				if (words[3] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[3]+' = %d \n' %int(ringFilterNew))
					else:
						arquivopar.write(line)


				if (words[4] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[4]+' = %d \n' %int(pagFilterNew))
					else:
						arquivopar.write(line)


				if (words[5] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[5]+' = %d \n' %int(ccdFilterNew))
					else:
						arquivopar.write(line)

		        
				if (words[6] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[6]+' = {"threshold": %0.4f }\n' %float(ccdFilterThresNew))
					else:
						arquivopar.write(line)


				if (words[7] in line)==True:
					if not '#RING_FILTER_PARA' in line:					
						arquivopar.write(words[7]+' = {"FILTER": ar, "threshold":%0.4f }# {"FILTER": ar }\n' %float(ringFilterThresNew))
					else:
						arquivopar.write(line)


				if (words[8] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[8]+' = %0.2f \n' %float(pagFilterThresNew))
					else:
						arquivopar.write(line)


				if (words[9] in line)==True:
					if not '#' in line:					
						pagFilterMARGEThresNew=(float(pagFilterThresNew)/pSize.get())
						pagFilterMARGEThresNew=int(pagFilterMARGEThresNew)
						arquivopar.write(words[9]+' = %d \n' %pagFilterMARGEThresNew)
					else:
						arquivopar.write(line)


		finally:
			msg = 'Recon Started with PyHST' + ' at ' + time.strftime("%H:%M - %d-%m-%Y") + '\n' + 'With a total of ' + str(nSlices) + ' image(s)' + '\n' + 'Path: ' + str(path2) + '\n' + 'WAIT!!!'
			error8.put(msg)
			print('\n',msg,'\n\n')
	
		inputpar.close()
		arquivopar.close()

		sftp_client.remove(path3)
		sftp_client.rename(path4, path3)


		recon_cmd="cd /" + Path + "; time PyHST2_33beta2 input.par lnls112,0 > garbage"

		#print (recon_cmd)

		stdin, stdout, stderr = ssh.exec_command(recon_cmd)

		print (stdout.readline())


		ssh.close()

		msg = 'Recon with PyHST FINISHED' + ' at ' + time.strftime("%H:%M - %d-%m-%Y") + '\n' + 'With a total of ' + str(nSlices) + ' image(s)' + '\n' + 'Path: ' + str(path2)
		error8.put(msg)
		print('\n',msg,'\n\n')

	
	else:
		msg = 'ERROR!!! \nThere is no input.par on ' + str(path2)
		error8.put(msg)
		print('\n',msg,'\n\n')
	


### DO THE RECON WITH PYRAFT ###
def reconStartPyRaft(Path, sSliceNew, eSliceNew, Regularization, Composition, Threshold, ImageSize, ImageFormat, BlocksNumber, GPUNumber, Centering, Shift, aRange):

	nSlices = (int(eSliceNew) - int(sSliceNew)) +1


	sftpURL   =  '10.2.105.44'
	sftpUser  =  '********'
	sftpPass  =  '********'


	ssh = paramiko.SSHClient()
	# automatically add keys without requiring human intervention
	ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

	ssh.connect(sftpURL, username=sftpUser, password=sftpPass)

	sftp_client=ssh.open_sftp()

	path="cd /" + Path + "; ls"

	stdin, stdout, stderr = ssh.exec_command(path)

	pvQueueWait.put(1)

	x=[]

	while True:
		line = stdout.readline()
		line = line.replace('\n','')

		if line != '':
			x.append(line)    

		else:
			break

	path2 = Path + "/"

	if 'input.par' in x:
		path3= Path + "/input.par"
		path4= Path + "/arquivo.par"

		inputpar=sftp_client.open(path3, '+r')
		arquivopar=sftp_client.open(path4, '+w')

		words = ['#START_SLICE', '#END_SLICE', '#ROTATION_SHIFT', '#CENTERING' , '#THRESHOLD', '#REGULARIZATION', '#FILTER_COMPOSITION', '#NUMBER_OF_BLOCKS', '#IMAGE_FORMAT', '#IMAGE_SIZE', '#GPU_NUMBER']

		for line in inputpar:
           
			if not any(word in line for word in words):
				arquivopar.write(line)

			if (words[0] in line)==True:
				arquivopar.write(words[0]+' = ' + sSliceNew + '\n')
	
			if (words[1] in line)==True:
				arquivopar.write(words[1]+' = ' + eSliceNew + '\n')

			if (words[2] in line)==True:
				arquivopar.write(words[2]+' = ' + Shift + '\n')

			if (words[3] in line)==True:
				arquivopar.write(words[3]+' = ' + Centering + '\n')

			if (words[4] in line)==True:
				arquivopar.write(words[4]+' = ' + Threshold + '\n')

			if (words[5] in line)==True:
				arquivopar.write(words[5]+' = ' + str(Regularization) + '\n')

			if (words[6] in line)==True:
				arquivopar.write(words[6]+' = ' + Composition + '\n')

			if (words[7] in line)==True:
				arquivopar.write(words[7]+' = ' + BlocksNumber + '\n')
	
			if (words[8] in line)==True:
				arquivopar.write(words[8]+' = ' + ImageFormat + '\n')

			if (words[9] in line)==True:
				arquivopar.write(words[9]+' = ' + ImageSize + '\n')

			if (words[10] in line)==True:
				arquivopar.write(words[10]+' = ' + GPUNumber + '\n')


		msg = 'Recon Started with PyRaft' + ' at ' + time.strftime("%H:%M - %d-%m-%Y") + '\n' + 'With a total of ' + str(nSlices) + ' image(s)' + '\n' + 'Path: ' + str(path2) + '\n' + 'WAIT!!!'
		error8.put(msg)
		print('\n',msg,'\n\n')
	
		inputpar.close()
		arquivopar.close()

		sftp_client.remove(path3)
		sftp_client.rename(path4, path3)

		path5="cd /" + Path + "/recon; ls"

		stdin2, stdout2, stderr2 = ssh.exec_command(path5)

		x=[]

		while True:
			line = stdout2.readline()
			line = line.replace('\n','')
	
			if line != '':
				x.append(line)    

			else:
				break

		ssh.close()

		### PYTHON ###	
		#cmd_recon = 'ssh -X 10.2.105.181 "python /storage/imx_recon_slice.py ' + Path + ' ' + sSliceNew + ' ' + eSliceNew + ' ' + str(Regularization) + ' ' + str(Composition) + ' ' + str(ThresholdMAX) + ' ' + str(ThresholdMIN) + ' 0"' 
		#os.system(cmd_recon)

		NumberOfSlices = (int(eSliceNew)-int(sSliceNew))+1
		BlockSize=1
		if (1<NumberOfSlices<=20):
			BlockSize = 4			
		elif (20<NumberOfSlices<60):
			BlockSize = 40
		elif (NumberOfSlices>=60):
			BlockSize = 60
		
		### C ###

		#cmd_recon = 'ssh 10.2.105.44 "/apps/IMX/ReconSoft/raft/bin/raft_imx -p ' + Path + '/ -i ' + str(int(sSliceNew)-1) + ' -f ' + str(int(eSliceNew)) + ' -b ' + str(BlockSize) + ' -r ' + str(Regularization) + ' -c ' + str(Composition) + ' -m ' + str(Threshold) + '"'

		if float(aRange)==360:
			cmd_recon = 'ssh 10.2.105.44 "/apps/IMX/ReconSoft/raft/bin/raft_imx -p ' + Path + '/ -i ' + str(int(sSliceNew)-1) + ' -f ' + eSliceNew + ' -b ' + str(BlockSize) + ' -r ' + str(Regularization) + ' -c ' + Composition + ' -m ' + Threshold + ' -s ' + ImageSize + ' -n ' + ImageFormat + ' -d ' + BlocksNumber + ' -g ' + GPUNumber + ' -o ' + Shift + ' -a ' + Centering +  ' -h 3"'

		else:
			cmd_recon = 'ssh 10.2.105.44 "/apps/IMX/ReconSoft/raft/bin/raft_imx -p ' + Path + '/ -i ' + str(int(sSliceNew)-1) + ' -f ' + eSliceNew + ' -b ' + str(BlockSize) + ' -r ' + str(Regularization) + ' -c ' + Composition + ' -m ' + Threshold + ' -s ' + ImageSize + ' -n ' + ImageFormat + ' -d ' + BlocksNumber + ' -g ' + GPUNumber + ' -o ' + Shift + '"' 

		print(cmd_recon)
		os.system(cmd_recon)
		
		if float(ImageFormat)==1: #8Bits
			volfromslice = 'ssh 10.2.105.44 "python /apps/IMX/ReconSoft/imx_volfromslice.py ' + Path + ' ' + str(int(sSliceNew)-1) + ' ' + str(int(eSliceNew)-1) + ' ' + str(ImageSize) + '"' 	# NEW RECON MACHINE
			#volfromslice = 'ssh 10.2.105.181 "python /storage/imx_volfromslice.py ' + Path + ' ' + str(sSliceNew-1) + ' ' + str(eSliceNew-1) + '"' 						# OLD RECON MACHINE

		if float(ImageFormat)==0: #32Bits
			volfromslice = 'ssh 10.2.105.44 "python /apps/IMX/ReconSoft/imx_volfromslice32.py ' + Path + ' ' + str(int(sSliceNew)-1) + ' ' + str(int(eSliceNew)-1) + ' ' + str(ImageSize) + '"' 	# NEW RECON MACHINE
			#volfromslice = 'ssh 10.2.105.181 "python /storage/imx_volfromslice.py ' + Path + ' ' + str(sSliceNew-1) + ' ' + str(eSliceNew-1) + '"' 						# OLD RECON MACHINE
		
		os.system(volfromslice)


		if not 'SLICES' in x:
			makedir = 'ssh 10.2.105.44 "cd ' + Path + '/recon/; mkdir SLICES"'
			os.system(makedir)

		moveSlices = 'ssh 10.2.105.44 "cd ' + Path + '/recon/; mv slice* SLICES"'
		os.system(moveSlices)


		msg = 'Recon with PyRaft FINISHED' + ' at ' + time.strftime("%H:%M - %d-%m-%Y") + '\n' + 'With a total of ' + str(nSlices) + ' image(s)' + '\n' + 'Path: ' + str(path2)
		error8.put(msg)
		print('\n',msg,'\n\n')

	
	else:
		msg = 'ERROR!!! \nThere is no input.par on ' + str(path2)
		error8.put(msg)
		print('\n',msg,'\n\n')



### SEND EMAIL ###
def sendEmail(Samples, Email):
	gmail_user = '****************'
	gmail_pwd = '*****************'
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

	l, lines = readLines()
	
	Samples=[]

	while len(lines)>0:	
		deleteLine()
		pvQueueWait.put(0)

		if 'PyHST' in l:	
			Path, rAxis, sSlice, eSlice, CCDFilter, CCDFilterThres, RingFilter, RingFilterThres, PaganinFilter, PaganinFilterThres = getParametersPyHST(l)
			Samples.append(Path)
			reconStartPyHST(Path, rAxis, sSlice, eSlice, CCDFilter, CCDFilterThres, RingFilter, RingFilterThres, PaganinFilter, PaganinFilterThres, pvPsize)

		if 'PyRaft' in l:
			Path, sSlice, eSlice, Regularization, Composition, Threshold, ImageSize, ImageFormat, BlocksNumber, GPUNumber, Centering, Shift, aRange = getParametersPyRaft(l)
			Samples.append(Path)
			reconStartPyRaft(Path, sSlice, eSlice, Regularization, Composition, Threshold, ImageSize, ImageFormat, BlocksNumber, GPUNumber, Centering, Shift, aRange)

		l, lines = readLines()


	SendEmail = int(sys.argv[1])

	if (SendEmail==1):
		Email = str(sys.argv[2])
		sendEmail(Samples, Email)








