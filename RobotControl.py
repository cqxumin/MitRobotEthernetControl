#!/usr/bin/env python3.4


#### IMPORTS ####
import socket, select, string, sys, time
from epics import PV
import PVNames

#### DEFINITIONS ####
pvSampleY = PV(PVNames.sampleStageMotorY)


#### SAMPLE Y CALIBRATION FUNCTION ####
def SampleYcalibration(s):

	OFFSET=pvSampleY.get()

	print('OFFSET: ', OFFSET)

	POSITION='1;1;VAL=P3=(+174.64,-177.74,+'+ str(OFFSET+592.76) + ',+93.39,+42.81,+46.83)(7,0)'

	commands=['1;1;STATE',
		  '1;1;OPEN=IMX',
		  '1;1;CNTLON',
		  '1;1;STOP',
		  '1;1;SLOTINIT',
		  '1;1;LOAD=T1',
		  POSITION,
		  '1;1;SAVE',
		  '1;1;RUNT1;1',
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

					while 'START;1;1'.encode('utf-8') in state:					
						s.send('1;1;STATE'.encode('utf-8'))
						time.sleep(.4)
						state=s.recv(4096)

					print('\nDONE!!!\n')

 
#### MAIN PROGRAM ####
if __name__ == "__main__":
     
     
	host = '10.2.1.200'	# STRING!!!
	port = 10001		# INT!!!
     
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
     
	# connect to remote host
	try :
		s.connect((host, port))
	except :
		print ('Unable to connect')
		sys.exit()

	print ('Connected to remote host')

	socket_list = [sys.stdin, s]

	SampleYcalibration(s)
		








