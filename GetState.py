#!/usr/bin/env python3.4


#### IMPORTS ####
import socket, select, string, sys, time
from epics import PV
import epics
import PVNames


#### DEFINITIONS ####



#### GETSTATE FUNCTION ####
def GetState(s):

	commands=['1;1;OPEN=IMX',
			  '1;1;STATE',
			  '1;1;CLOSE']


	s.send(commands[0].encode('utf-8'))

	while True:
		data = s.recv(4096)
		if data:
			break


	while True: #### ADD THE PV STATE CHECK!!!
		s.send(commands[1].encode('utf-8'))

		while True:
			data = s.recv(4096)
			if data:
				print ('Controller/Robot read for operating (' + str(data.decode('utf-8')) + ')\n')
				break
				
		break
			

	s.send(commands[2].encode('utf-8'))

	while True:
		data = s.recv(4096)
		if data:
			break
				


#### MAIN PROGRAM ####
if __name__ == "__main__":
     
	host = '10.2.1.200'	# STRING!!!
	port = 10001		# INT!!!
     
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.settimeout(2)
     
	# connect to remote host
	try :
		s.connect((host, port))
		socket_list = [sys.stdin, s]

		print ('\nConnected to remote host\n')
		
		GetState(s)
		
	except :
		print ('\nUnable to connect with robot controller\n')



		








