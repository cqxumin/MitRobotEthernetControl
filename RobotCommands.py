#!/usr/bin/env python3.4


#### IMPORTS ####
import socket, select, string, sys, time
#from epics import PV
#import epics
#import PVNames
#from MotorClass import Motor


#### DEFINITIONS ####
#pvSampleY = PV(PVNames.sampleStageMotorY)
#pvSampleX = PV(PVNames.sampleStageMotorX)
#pvMTS1 = PV(PVNames.sampleMTS1MotorPVName)
#pvMTS2 = PV(PVNames.sampleMTS2MotorPVName)

#### OPTION MENU ####
def OptionMenu():
	print ('\nPossible Options (Exemple: ./RobotCommands.py 1)')
	print ('\n1 - Reset Alarm')
	print ('2 - Get Errors\n')
	#print ('2 - GET Speed')
	#print ('3 - Change Speed (Put speed too, ex: ./RobotCommands 2 100')
	


#### RESET ALARM ####
def ResetAlarm(s):

	commands=['1;1;RSTALRM']

	for cmd in commands:
	
		s.send(cmd.encode('utf-8'))
		while True:
			data = s.recv(4096)
			if data:
				print (data)
				break

	print('\nDONE!!!\n')
	
	
#### GET ERRORS ####
def GetErrors(s):

	commands=['1;1;ERROR']

	for cmd in commands:
	
		s.send(cmd.encode('utf-8'))
		while True:
			data = s.recv(4096)
			if data:
				print (data.decode('utf-8'))
				break

	print('\nDONE!!!\n')



#### MAIN PROGRAM ####
if __name__ == "__main__":

	if len(sys.argv)==1:
		OptionMenu()
		sys.exit()
    
	else: 
		Function = float(sys.argv[1])

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

		if Function == 1:
			ResetAlarm(s)
			
		if Function == 2:
			GetErrors(s)
	
		








