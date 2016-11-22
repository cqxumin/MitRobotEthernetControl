#!/usr/bin/env python3.4


#### IMPORTS ####
import socket, select, string, sys, time
from epics import PV
import epics
import PVNames
from MotorClass import Motor
#import subprocess


#### DEFINITIONS ####
pvSampleY = PV(PVNames.sampleStageMotorY)
pvSampleX = Motor(PVNames.sampleStageMotorX)
pvMTS1 = Motor(PVNames.sampleMTS1MotorPVName)
pvMTS2 =  Motor(PVNames.sampleMTS2MotorPVName)
hutchStatus = PV(PVNames.hutchStatusPVName)

global 	OFFSET


##############################################################################################################################

#### PUT SAMPLE ON ROTATION STAGE FUNCTION ####
def SampleON(s, SampleNumber):
	
	# Update positions based on SampleY Offset
	P2='1;1;VAL=P2=(+160.55,-158.73,+' + str(OFFSET+641.88) + ',+94.73,+44.69,+48.81)(7,0)'
	P3='1;1;VAL=P3=(+294.59,-290.53,+' + str(OFFSET+630.84) + ',+94.73,+44.69,+48.81)(7,0)'
	P4='1;1;VAL=P4=(+294.59,-290.53,+' + str(OFFSET+613.04) + ',+94.73,+44.69,+48.81)(7,0)'
	P5='1;1;VAL=P5=(+254.52,-251.13,+' + str(OFFSET+616.34) + ',+94.73,+44.69,+48.81)(7,0)'
	
	Program = '1;1;RUN' + str(int(SampleNumber)) + 'A;1'  ### Example: '1;1;RUN1A;1'
	
	commands=['1;1;STATE',
		  '1;1;OPEN=IMX',
		  '1;1;CNTLON',
		  '1;1;SLOTINIT',
		  '1;1;LOAD=T1A',
		  P2,
		  P3,
		  P4,
		  P5,
		  '1;1;SAVE',
  		  Program,
		  '1;1;RUNT1A;1',
		  '1;1;CLOSE']

	# Send commands to robot controller
	for cmd in commands:
	
		s.send(cmd.encode('utf-8'))
		wait=1
		while wait==1:
			data = s.recv(4096)
			if data:				
				print (data)
				wait=0
				
				#Stay here until moving command is done
				if 'RUN' in cmd:
					s.send('1;1;STATE'.encode('utf-8'))
					time.sleep(.4)
					state=s.recv(4096)

					print('\nMOVING!!!\n')

					while '.MB5'.encode('utf-8') in state:
						if hutchStatus.get()==1:		# Only move if hutch is armed
							s.send('1;1;STATE'.encode('utf-8'))
							time.sleep(.4)
							state=s.recv(4096)
							
						else:
							while hutchStatus.get()==0:		# Wait for hutch rearmed
							
								print ("Rearm Hutch")
								s.send('1;1;STOP'.encode('utf-8'))
								time.sleep(1)

							if hutchStatus.get()==1:		# Start running again
								s.send('1;1;STATE'.encode('utf-8'))
								time.sleep(.4)
								state=s.recv(4096)
								
								print ("REARMED!!!!")

								if not '.MB5'.encode('utf-8') in state:		# Goes to next command on the list
									#s.send('1;1;RUNT1A;1'.encode('utf-8'))
									print("NEXT PROGRAM...")
									
								else:
									s.send('1;1;RUN;1'.encode('utf-8'))		# Continue running the program
									print("RUNNING !!!")
									
								s.send('1;1;STATE'.encode('utf-8'))
								time.sleep(.4)
								state=s.recv(4096)

								

					print('\nDONE!!!\n')
					

					
#### TAKE SAMPLE ON ROTATION STAGE FUNCTION ####
def SampleOFF(s, SampleNumber):
	
	
	P2='1;1;VAL=P2=(+160.55,-158.73,+' + str(OFFSET+641.88) + ',+94.73,+44.69,+48.81)(7,0)'
	P3='1;1;VAL=P3=(+257.28,-253.85,+' + str(OFFSET+613.53) + ',+94.73,+44.69,+48.81)(7,0)'
	P4='1;1;VAL=P4=(+294.59,-290.53,+' + str(OFFSET+610.45) + ',+94.73,+44.69,+48.81)(7,0)'
	P5='1;1;VAL=P5=(+294.59,-290.53,+' + str(OFFSET+621.45) + ',+94.73,+44.69,+48.81)(7,0)'
	
	Program = '1;1;RUN' + str(int(SampleNumber)) + 'B;1'  ### Example: '1;1;RUN1B;1'
	
	commands=['1;1;STATE',
		  '1;1;OPEN=IMX',
		  '1;1;CNTLON',
		  '1;1;SLOTINIT',
		  '1;1;LOAD=T1B',
		  P2,
		  P3,
		  P4,
		  P5,
		  '1;1;SAVE',
		  '1;1;RUNT1B;1',
		  Program,
		  '1;1;CLOSE']


	for cmd in commands:
	
		s.send(cmd.encode('utf-8'))
		wait=1
		while wait==1:
			data = s.recv(4096)
			if data:
				
				print (data)
				wait=0

				if 'RUN' in cmd:
					s.send('1;1;STATE'.encode('utf-8'))
					time.sleep(.4)
					state=s.recv(4096)

					print('\nMOVING!!!\n')			
					
					while '.MB5'.encode('utf-8') in state:
					#while 'START;1;1'.encode('utf-8') in state:
						if hutchStatus.get()==1:
							s.send('1;1;STATE'.encode('utf-8'))
							time.sleep(.4)
							state=s.recv(4096)
							
						else:
							while hutchStatus.get()==0:
							
								print ("Rearm Hutch")
								s.send('1;1;STOP'.encode('utf-8'))
								time.sleep(1)

							if hutchStatus.get()==1:
								s.send('1;1;STATE'.encode('utf-8'))
								time.sleep(.4)
								state=s.recv(4096)
								
								print ("REARMED!!!!")

								if not '.MB5'.encode('utf-8') in state:
									print("NEXT PROGRAM...")
									
								else:
									s.send('1;1;RUN;1'.encode('utf-8'))
									print("RUNNING !!!")
									
								s.send('1;1;STATE'.encode('utf-8'))
								time.sleep(.4)
								state=s.recv(4096)

								

					print('\nDONE!!!\n')					

					

##############################################################################################################################			
##############################################################################################################################


#### MAIN PROGRAM ####
if __name__ == "__main__":

	if len(sys.argv)<3:
			print('\nWrong input!!!\n\nEnter with Mode and Sample Number.\nExample: ./RobotControl.py 0 1\n\nMode 0 = Take On the sample\nMode 1 = Take Off the Sample\n\nSample number: 1, 2, 3 or 4\n\n')
			sys.exit()


	else:
		while hutchStatus.get()==0:		# Check if hutch is armed and stay here if it's not
			print ("ARM HUTCH...")
			time.sleep(1)
		
		else:
			Mode = int(sys.argv[1])		# Get execution mode (0 = put and 1 = take)						
			SampleNumber = int(sys.argv[2])		#Get Sample number
			 
			host = '10.2.1.200'	# STRING!!!
			port = 10001		# INT!!!
			 
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# Create a socket communication
			s.settimeout(2)		# Goes out If connection don't succed after 2 seconds
		
			'''
			p = subprocess.Popen("python /usr/local/scripts/Robot/Arduino_Server_Test.py", stdout=subprocess.PIPE, shell=True)
	 
			(output, err) = p.communicate()
			p_status = p.wait()
		
			output=output.decode('utf-8')
			'''
					 
			# connect to remote host
			try :
				s.connect((host, port))
			except :
				print ('Unable to connect')
				sys.exit()

			print ('Connected to remote host')

			OFFSET=(pvSampleY.get())-15.		# Get SampleY Offset
	
			print('OFFSET: ', OFFSET)
			
			# MTS1, MTS2 and SampleX go to exchange position
			preSampleX = pvSampleX.getRealPosition()
			preSampleX = round(preSampleX,2)
			print('\nSampleX: ', preSampleX)

			if preSampleX == 0.:
				pass
			else:
				print ('Moving Sample X\n')		
				pvSampleX.setAbsolutePosition(0., True)


			pvMTS1.setUpdateRequest(1)
			time.sleep(.5)
			preMTS1 = pvMTS1.getRealPosition()
			preMTS1 = round(preMTS1,2)
			print('MTS1: ', preMTS1)

			if preMTS1 == 0:
				pass
			else:
				print ('Moving MTS1\n')
				pvMTS1.setAbsolutePosition(0, True)



			pvMTS2.setUpdateRequest(1)
			time.sleep(.5)
			preMTS2 = pvMTS2.getRealPosition()
			preMTS2 = round(preMTS2,2)
			print('MTS2: ', preMTS2)
	
			if preMTS2 == 0:
				pass
			else:
				print ('Moving MTS2\n\n')
				pvMTS2.setAbsolutePosition(0, True)

			# Execute robot Functions
			if Mode == 0:
				SampleON(s, SampleNumber)

			else:
				SampleOFF(s, SampleNumber)

		
			# MTS1, MTS2 and SampleX go to orginal position
			if preSampleX == 0.:
				pass
			else:
				print ('Moving Sample X to ', preSampleX)
				pvSampleX.setAbsolutePosition(preSampleX, True)


			if preMTS1 == 0:
				pass
			else:
				print ('Moving MTS1 to ', preMTS1)
				pvMTS1.setAbsolutePosition(preMTS1, True)


			if preMTS2 == 0:
				pass
			else:
				print ('Moving MTS2 to ', preMTS2)
				pvMTS2.setAbsolutePosition(preMTS2, True)


			s.close()
		








