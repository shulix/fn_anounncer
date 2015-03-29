#!/usr/bin/python
__author__ = 'shulih'
import threading
from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import sys

announcement = 5
bc_port = 50000
listen_port=50001
rpc_port=8000
MAGIC = "fn_announcer"
my_ip= gethostbyname(gethostname()) #get our IP. Be careful if you have multiple network interfaces or IPs

s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
s.bind((my_ip, listen_port))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket

def announcer():
    data = MAGIC+my_ip

    while 1:
        try:
            s.sendto(data, ('<broadcast>', bc_port))
            print "sent service announcement"
            sleep(announcement)
        except KeyboardInterrupt:
            print 'Exiting'



def pow():
    return "got RPC"

def rpcserver():
    server = SimpleXMLRPCServer((my_ip, rpc_port), logRequests=True)
    server.register_function(pow)
    try:
        print 'Use Control-C to exit'
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Exiting'

threading.Thread(target=announcer).start()
threading.Thread(target=rpcserver).start()

while 1:
    message, address = s.recvfrom(2048)
    if message.startswith(MAGIC):
        print address[0],'is ', message[len(MAGIC):]
    try:
        sleep(5)
    except (KeyboardInterrupt, SystemExit):
        for thread in threading.enumerate():
            if thread.isAlive():
                try:
                    thread._Thread__stop()
                except:
                    print(str(thread.getName()) + ' could not be terminated')
        sys.exit()




