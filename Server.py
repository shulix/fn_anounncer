#!/usr/bin/python

"""

"""
__author__ = 'shuli'

import threading
from time import sleep
from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
import SimpleXMLRPCServer
#from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
handler = logging.FileHandler('fn_ac.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

announcement = 5
bc_port = 50000
listen_port = 50001
rpc_port = 8000
MAGIC = "fn_announcer"
my_ip = gethostbyname(gethostname()) #get our IP. Be careful if you have multiple network interfaces or IPs

roles_dic = dict()
roles_dic.setdefault('hpi', [])
roles_dic.setdefault('spm', [])
roles_dic.setdefault('reports' ,[])
roles_dic.setdefault('trmon' ,[])
roles_dic.setdefault('trmof' ,[])

#Create socket
s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
s.bind((my_ip, listen_port))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket


class LoggingSimpleXMLRPCRequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    """
    Overrides the default SimpleXMLRPCRequestHandler to support logging.
    Logs client IP and the XML request and response.
    """
    def do_POST(self):
        clientIP, port = self.client_address
	# Log client IP and Port
        logger.debug('Client IP: %s - Port: %s' % (clientIP, port))
        try:
            # get arguments
            data = self.rfile.read(int(self.headers["content-length"]))
            # Log client request
	    logger.debug('Client request: \n%s\n' % data)
            response = self.server._marshaled_dispatch(
                    data, getattr(self, '_dispatch', None)
                )
	    # Log server response
            logger.debug('Server response: \n%s\n' % response)
	except:
            #Report internal server error (HTTP 500) if the module has an error
            self.send_response(500)
            self.end_headers()
        else:
            # got a valid XML RPC response
            self.send_response(200)
            self.send_header("Content-type", "text/xml")
            self.send_header("Content-length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # shut down the connection
            self.wfile.flush()
            self.connection.shutdown(1)

class REMOTEMETHODS:
    def IsAlive(self, string):
        return "Hello %s" % string


def pow():
    return "got RPC"

def announcer():
    data = MAGIC+my_ip

    while 1:
        try:
            s.sendto(data, ('<broadcast>', bc_port))
            logger.info("sent service announcement")
            sleep(announcement)
        except KeyboardInterrupt:
            print 'Exiting'

def rpc_server():
    server = SimpleXMLRPCServer.SimpleXMLRPCServer((my_ip, rpc_port), LoggingSimpleXMLRPCRequestHandler)
    server.register_function(pow)
    object = REMOTEMETHODS()
    server.register_instance(object)
    try:
        logger.debug('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        logger.debug('Exiting')

def addRole(addr,role):
    log = addr,'requesting role ',role
    logger.debug(log)
    for nodeType in roles_dic.values():
        if addr not in nodeType:
            roles_dic[role].append(addr)

threading.Thread(target=announcer).start()
threading.Thread(target=rpc_server).start()

while 1:
    message, address = s.recvfrom(2048)
    if message.startswith(MAGIC):
        addRole(address[0],message[len(MAGIC):])
    try:
        sleep(5)
    except (KeyboardInterrupt, SystemExit):
        for thread in threading.enumerate():
            if thread.isAlive():
                try:
                    thread._Thread__stop()
                except:
                    log = (str(thread.getName()) + ' could not be terminated')
                    logger.debug(log)
        sys.exit()