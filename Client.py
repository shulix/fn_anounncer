__author__ = 'shulih'
import xmlrpclib
from socket import socket, AF_INET, SOCK_DGRAM
import sys

if len(sys.argv) < 2:
   sys.exit('Usage: %s Node_type (e.g. hpi,spm,trmon,trmof,reports)' % sys.argv[0])
print sys.argv
PORT = 50000
MAGIC = "fn_announcer"
s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
s.bind(('', PORT))


while 1:
    data, addr = s.recvfrom(1024) #wait for a packet
    if not len(data):
         break
    try:
        if data.startswith(MAGIC):
            print "got service announcement from", data[len(MAGIC):]
            msg = MAGIC+sys.argv[1]
            s.sendto(msg, (data[len(MAGIC):], 50001))
            rpcurl='http://'+data[len(MAGIC):]+':8000'
            server = xmlrpclib.ServerProxy(rpcurl)
            if sys.argv[2] == 'pow':
                print 'Ping:', server.pow()
            elif sys.argv[2] == 'mow':
                print 'Ping:', server.hello('sukar')


    except KeyboardInterrupt:
        print 'Exiting'