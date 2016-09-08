#! /usr/bin/env python  
#coding=utf-8 

import struct
import socket  
import time 

if __name__ == '__main__':
  
    HOST = '159.203.20.221'    # The remote host  
    PORT = 8001           # The same port as used by the server  
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    s.connect((HOST, PORT))  
    buffer = struct.pack("cII",'H',10,1)
    print "buffer len=" + str(len(buffer))
    print "pack len=" + str(struct.calcsize("cII"))
    buffer = buffer + bytearray(10)
    print "buffer len=" + str(len(buffer))
    s.sendall(buffer) 
    time.sleep(5)  
    buffer = struct.pack("cII",'H',3,2)
    buffer = buffer + bytearray(30)
    print "buffer len=" + str(len(buffer))
    print "pack len=" + str(struct.calcsize("cII"))
    s.sendall(buffer)   
    time.sleep(5)  
    s.close()  