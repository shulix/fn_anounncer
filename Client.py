__author__ = 'shulih'
import xmlrpclib
from socket import socket, AF_INET, SOCK_DGRAM

PORT = 50000
MAGIC = "fn_announcer"
s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
s.bind(('', PORT))


while 1:
    data, addr = s.recvfrom(1024) #wait for a packet
    if not len(data):
        break
    if data.startswith(MAGIC):
        print "got service announcement from", data[len(MAGIC):]
        msg = MAGIC+'alive'
        s.sendto(msg, (data[len(MAGIC):], 50001))
        rpcurl='http://'+data[len(MAGIC):]+':8000'
        server = xmlrpclib.ServerProxy(rpcurl)
        print 'Ping:', server.pow()