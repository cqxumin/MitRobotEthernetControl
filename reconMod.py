#!/usr/bin/env python3.4
'''
FILENAME... recon
USAGE...    Script for reconstruction at IMX
/*
 *      Original Author: IMX Beamline Group
 *      Date: 02/05/2016
 */
'''

import sys
import os
import time
from epics import PV
import PVNames
import configparser
import re
import time
import paramiko
import subprocess

###########################################################################
#
# PARAMETERS PARSER
#
###########################################################################
#sSliceNew = int(sys.argv[1])
#eSliceNew = int(sys.argv[2])
#rAxisNew = float(sys.argv[3])


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
pvrAxis = PV(PVNames.rAxis)
pvsSlice = PV(PVNames.sSlice)
pveSlice = PV(PVNames.eSlice)
pvreconWait = PV(PVNames.reconWait)

pvaRange = PV(PVNames.aRange)




###########################################################################
#
# PYHST RECON
#
###########################################################################

def PyHSTRecon(rAxisNew, sSliceNew, eSliceNew, ringFilterNew, pagFilterNew, ccdFilterNew, ccdFilterThresNew, ringFilterThresNew, pagFilterThresNew, pSize, OpenImage, RecMetodo, nSlices):


	sftpURL   =  '10.2.105.44'
	sftpUser  =  'userimx'
	sftpPass  =  'syncro!14'


	ssh = paramiko.SSHClient()
	# automatically add keys without requiring human intervention
	ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

	ssh.connect(sftpURL, username=sftpUser, password=sftpPass)

	sftp_client=ssh.open_sftp()

	path="cd /" + pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True) + "; ls"

	stdin, stdout, stderr = ssh.exec_command(path)

	x=[]

	pvreconWait.put(1)

	while True:
		line = stdout.readline()
		line = line.replace('\n','')

		if line != '':
			x.append(line)    

		else:
			break


	path2 = "/"+ pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True) + "/"

	if 'input.par' in x:

		path3= "/"+ pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True)+ "/input.par"
		path4= "/"+ pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True)+ "/arquivo.par"

		inputpar=sftp_client.open(path3, '+r')
		arquivopar=sftp_client.open(path4, '+w')
			
		try:
			words = ['ROTATION_AXIS_POSITION', 'START_VOXEL_3', 'END_VOXEL_3', 'DO_RING_FILTER', 'DO_PAGANIN', 'DO_CCD_FILTER', 'CCD_FILTER_PARA', 'RING_FILTER_PARA', 'PAGANIN_Lmicron', 'PAGANIN_MARGE']

			for line in inputpar:
		            
				if not any(word in line for word in words):
					arquivopar.write(line)
		        
				if (words[0] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[0]+' = %0.2f \n' %rAxisNew)
					else:
						arquivopar.write(line)
		        
				if (words[1] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[1]+' = %d \n' %sSliceNew)
					else:
						arquivopar.write(line)

	
				if (words[2] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[2]+' = %d \n' %eSliceNew)
					else:
						arquivopar.write(line)


				if (words[3] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[3]+' = %d \n' %ringFilterNew)
					else:
						arquivopar.write(line)


				if (words[4] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[4]+' = %d \n' %pagFilterNew)
					else:
						arquivopar.write(line)


				if (words[5] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[5]+' = %d \n' %ccdFilterNew)
					else:
						arquivopar.write(line)

		        
				if (words[6] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[6]+' = {"threshold": %0.4f }\n' %ccdFilterThresNew)
					else:
						arquivopar.write(line)


				if (words[7] in line)==True:
					if not '#RING_FILTER_PARA' in line:					
						arquivopar.write(words[7]+' = {"FILTER": ar, "threshold":%0.4f }# {"FILTER": ar }\n' %ringFilterThresNew)
					else:
						arquivopar.write(line)


				if (words[8] in line)==True:
					if not '#' in line:					
						arquivopar.write(words[8]+' = %0.2f \n' %pagFilterThresNew)
					else:
						arquivopar.write(line)


				if (words[9] in line)==True:
					if not '#' in line:					
						pagFilterMARGEThresNew=(pagFilterThresNew/pSize)
						pagFilterMARGEThresNew=int(pagFilterMARGEThresNew)
						arquivopar.write(words[9]+' = %d \n' %pagFilterMARGEThresNew)
					else:
						arquivopar.write(line)


		finally:
			inputpar.close()
			arquivopar.close()

			sftp_client.remove(path3)
			sftp_client.rename(path4, path3)
		

		NumberOfSlices = (int(eSliceNew)-int(sSliceNew))+1


		msg = 'Recon Started using PyHST' + ' at ' + time.strftime("%H:%M - %d-%m-%Y") + '\n' + 'With a total of ' + str(nSlices) + ' image(s)' + '\n' + 'Path: ' + str(path2) + '\n' + 'WAIT!!!'
		error8.put(msg)
		print('\n',msg,'\n\n')

		recon_cmd="cd /" + pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True)+ "; time PyHST2_33beta2 input.par lnls112,0 > garbage"

		print (recon_cmd)
		stdin, stdout, stderr = ssh.exec_command(recon_cmd)
		print (stdout.readline())


	else:
		msg = 'ERROR!!! \nThere is no input.par on ' + str(path2)
		error8.put(msg)
		print('\n',msg,'\n\n')

		OpenImage=0
	

	if(OpenImage==1):
		os.system('Scripts_Recon/Open_Image.py tomo.vol &')


	ssh.close()

	pvreconWait.put(0)


###########################################################################
#
# PYRaft RECON
#
###########################################################################

def PyRaftRecon(sSliceNew, eSliceNew, Shift, Centering, Regularization, Composition, Threshold, ImageSize, ImageFormat, BlocksNumber, GPUNumber, OpenImage, RecMetodo, nSlices):

	sftpURL   =  '10.2.105.44'
	sftpUser  =  'userimx'
	sftpPass  =  'syncro!14'


	ssh = paramiko.SSHClient()
	# automatically add keys without requiring human intervention
	ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )

	ssh.connect(sftpURL, username=sftpUser, password=sftpPass)

	sftp_client=ssh.open_sftp()

	path="cd /" + pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True) + "; ls"

	stdin, stdout, stderr = ssh.exec_command(path)

	x=[]

	pvreconWait.put(1)

	while True:
		line = stdout.readline()
		line = line.replace('\n','')

		if line != '':
			x.append(line)    

		else:
			break


	path2 = "/"+ pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True) + "/"

	if 'input.par' in x:

		path3= "/"+ pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True)+ "/input.par"
		path4= "/"+ pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True)+ "/arquivo.par"

		inputpar=sftp_client.open(path3, '+r')
		arquivopar=sftp_client.open(path4, '+w')
			
		try:
			words = ['#START_SLICE', '#END_SLICE', '#ROTATION_SHIFT', '#CENTERING' , '#THRESHOLD', '#REGULARIZATION', '#FILTER_COMPOSITION', '#NUMBER_OF_BLOCKS', '#IMAGE_FORMAT', '#IMAGE_SIZE', '#GPU_NUMBER']

			for line in inputpar:
		            
				if not any(word in line for word in words):
					arquivopar.write(line)

				if (words[0] in line)==True:
					arquivopar.write(words[0]+' = %d \n' %sSliceNew)
	
				if (words[1] in line)==True:
					arquivopar.write(words[1]+' = %d \n' %eSliceNew)

				if (words[2] in line)==True:
					arquivopar.write(words[2]+' = %f \n' %Shift)

				if (words[3] in line)==True:
					arquivopar.write(words[3]+' = %f \n' %Centering)
	
				if (words[4] in line)==True:
					arquivopar.write(words[4]+' = %d \n' %Threshold)

				if (words[5] in line)==True:
					arquivopar.write(words[5]+' = %f \n' %Regularization)

				if (words[6] in line)==True:
					arquivopar.write(words[6]+' = %d \n' %Composition)

				if (words[7] in line)==True:
					arquivopar.write(words[7]+' = %d \n' %BlocksNumber)
	
				if (words[8] in line)==True:
					arquivopar.write(words[8]+' = %d \n' %ImageFormat)

				if (words[9] in line)==True:
					arquivopar.write(words[9]+' = %d \n' %ImageSize)

				if (words[10] in line)==True:
					arquivopar.write(words[10]+' = %d \n' %GPUNumber)

		finally:
			inputpar.close()
			arquivopar.close()

			sftp_client.remove(path3)
			sftp_client.rename(path4, path3)
		

		msg = 'Recon Started using PyRaft' + ' at ' + time.strftime("%H:%M - %d-%m-%Y") + '\n' + 'With a total of ' + str(nSlices) + ' image(s)' + '\n' + 'Path: ' + str(path2) + '\n' + 'WAIT!!!'
		error8.put(msg)
		print('\n',msg,'\n\n')

		Path = "/" + pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True)


		### C ###
		BlockSize=1
		if (1<nSlices<=20):
			BlockSize = 4			
		elif (20<nSlices<60):
			BlockSize = 40
		elif (nSlices>=60):
			BlockSize = 60

		Regularization = (Regularization/100000)

		if (pvaRange.get()==360):
			cmd_recon = 'ssh 10.2.105.44 "/apps/IMX/ReconSoft/raft/bin/raft_imx -p ' + Path + '/ -i ' + str(sSliceNew-1) + ' -f ' + str(eSliceNew) + ' -b ' + str(BlockSize) + ' -r ' + str(Regularization) + ' -c ' + str(Composition) + ' -m ' + str(Threshold) + ' -s ' + str(ImageSize) + ' -n ' + str(ImageFormat) + ' -d ' + str(BlocksNumber) + ' -g ' + str(GPUNumber) + ' -o ' + str(Shift) + ' -a ' + str(int(Centering)) +  ' -h 3"' # NEW RECON MACHINE
			#error8.put("360 Recon Not Working Yet...")
			#pvreconWait.put(0)
			#sys.exit()

		else:
			cmd_recon = 'ssh 10.2.105.44 "/apps/IMX/ReconSoft/raft/bin/raft_imx -p ' + Path + '/ -i ' + str(sSliceNew-1) + ' -f ' + str(eSliceNew) + ' -b ' + str(BlockSize) + ' -r ' + str(Regularization) + ' -c ' + str(Composition) + ' -m ' + str(Threshold) + ' -s ' + str(ImageSize) + ' -n ' + str(ImageFormat) + ' -d ' + str(BlocksNumber) + ' -g ' + str(GPUNumber) + ' -o ' + str(Shift) + '"' 				# NEW RECON MACHINE

		#cmd_recon = 'ssh 10.2.105.181 "/storage/raft/bin/raft_imx -p ' + Path + '/ -i ' + str(sSliceNew-1) + ' -f ' + str(eSliceNew) + ' -b ' + str(BlockSize) + ' -r ' + str(Regularization) + ' -c ' + str(Composition) + ' -m ' + str(ThresholdMAX) + '"' 				# OLD RECON MACHINE

		os.system(cmd_recon)

		print (cmd_recon)

		if ImageFormat==1: #8Bits
			volfromslice = 'ssh 10.2.105.44 "python /apps/IMX/ReconSoft/imx_volfromslice.py ' + Path + ' ' + str(int(sSliceNew)-1) + ' ' + str(int(eSliceNew)-1) + ' ' + str(ImageSize) + '"' 	# NEW RECON MACHINE
			#volfromslice = 'ssh 10.2.105.181 "python /storage/imx_volfromslice.py ' + Path + ' ' + str(sSliceNew-1) + ' ' + str(eSliceNew-1) + '"' 						# OLD RECON MACHINE

		if ImageFormat==0: #32Bits
			volfromslice = 'ssh 10.2.105.44 "python /apps/IMX/ReconSoft/imx_volfromslice32.py ' + Path + ' ' + str(int(sSliceNew)-1) + ' ' + str(int(eSliceNew)-1) + ' ' + str(ImageSize) + '"' 	# NEW RECON MACHINE
			#volfromslice = 'ssh 10.2.105.181 "python /storage/imx_volfromslice.py ' + Path + ' ' + str(sSliceNew-1) + ' ' + str(eSliceNew-1) + '"' 						# OLD RECON MACHINE
		

		os.system(volfromslice)


		#cmd_remove = 'ssh 10.2.105.44 "rm ' + Path + '/recon/slice_*"' 
		#os.system(cmd_remove)
	
		msg = 'Recon FINISHED' + ' at ' + time.strftime("%H:%M - %d-%m-%Y") + '\n' + 'With a total of ' + str(nSlices) + ' image(s)' + '\n' + 'Path: ' + str(path2)
		error8.put(msg)
		print('\n',msg,'\n\n')

	else:
		msg = 'ERROR!!! \nThere is no input.par on ' + str(path2)
		error8.put(msg)
		print('\n',msg,'\n\n')

		OpenImage=0


	if(OpenImage==1 and ImageFormat==1): #8Bits
		os.system('Scripts_Recon/Open_Image.py tomo' + str(nSlices) + '.b &')

	if(OpenImage==1 and ImageFormat==0): #8Bits
		os.system('Scripts_Recon/Open_Image.py tomo' + str(nSlices) + '_32.b &')

	pvreconWait.put(0)

	
	
###########################################################################
#
# CONTROL OF RECON
#
###########################################################################
if __name__ == '__main__':
     


	path3= "/"+ pvRLoc.get(as_string=True) + "/" + pvRUserName.get(as_string=True) + "/" + pvRExpPath.get(as_string=True) + "/" + pvReconPath.get(as_string=True)

	RecMetodo = int(sys.argv[1])
	
	sSliceNew = int(sys.argv[2])
	eSliceNew = int(sys.argv[3])

	nSlices=eSliceNew-sSliceNew+1

	if RecMetodo == 0:
		rAxisNew = float(sys.argv[4])
		ccdFilterNew = int(sys.argv[5])
		ringFilterNew = int(sys.argv[6])
		pagFilterNew = int(sys.argv[7])
		ccdFilterThresNew = float(sys.argv[8])
		ringFilterThresNew = float(sys.argv[9])
		pagFilterThresNew = float(sys.argv[10])
		pSize = float(sys.argv[11])
		OpenImage = float(sys.argv[12])

		PyHSTRecon(rAxisNew, sSliceNew, eSliceNew, ringFilterNew, pagFilterNew, ccdFilterNew, ccdFilterThresNew, ringFilterThresNew, pagFilterThresNew, pSize, OpenImage, RecMetodo, nSlices)

	

	if RecMetodo == 1:
		Regularization = float(sys.argv[4])
		Composition = int(sys.argv[5])
		Threshold = float(sys.argv[6])
		ImageSize = int(float(sys.argv[7]))
		ImageFormat = int(float(sys.argv[8]))
		BlocksNumber = int(float(sys.argv[9]))
		GPUNumber = int(float(sys.argv[10]))
		Shift = float(sys.argv[11])
		Centering = float(sys.argv[12])
		OpenImage = float(sys.argv[13])
		
		PyRaftRecon(sSliceNew, eSliceNew, Shift, Centering, Regularization, Composition, Threshold, ImageSize, ImageFormat, BlocksNumber, GPUNumber, OpenImage, RecMetodo, nSlices)



