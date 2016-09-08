#! /usr/bin/env python  
#coding=utf-8  
    
from tornado.tcpserver import TCPServer    
from tornado.ioloop  import IOLoop 
from tornado.ioloop  import PeriodicCallback
from tornado.gen import coroutine  
from tornado import options
from tornado import log
#import struct
import logging
import logging.handlers

datefmt = '%Y-%m-%d %H:%M:%S'
fmt = '%(color)s%(asctime)s|%(levelname)s|%(module)s|%(funcName)s|%(filename)s:%(lineno)d|%(end_color)s%(message)s'

ttlog = logging.getLogger("tornado_tcpserver")
ttlog.setLevel(logging.DEBUG) 

tornado_tcpserver_handler = logging.handlers.TimedRotatingFileHandler(filename="../logs/tornado_tcpserver.log",when="D")
tornado_tcpserver_handler.suffix = "%Y%m%d.log"
tornado_tcpserver_handler.setFormatter(log.LogFormatter(fmt=fmt, datefmt=datefmt))
ttlog.propagate = False
ttlog.addHandler(tornado_tcpserver_handler)

tornado_handler = logging.handlers.TimedRotatingFileHandler(filename="../logs/tornado.log",when="D")
tornado_handler.suffix = "%Y%m%d"
tornado_handler.setFormatter(log.LogFormatter(fmt=fmt, datefmt=datefmt))
log.app_log.propagate = False
log.gen_log.propagate = False
log.access_log.propagate = False
log.access_log.setLevel(logging.DEBUG)
log.app_log.addHandler(tornado_handler) 
log.gen_log.addHandler(tornado_handler) 
log.access_log.addHandler(tornado_handler) 

class Connection(object): 

    DATA_ILLEGAL        = -1
    BUFFER_NO_ENOUGH    = 1

    clients = set()   
    def __init__(self, stream, address):   
        Connection.clients.add(self)
        self._stream = stream    
        self._address = address    
        self._stream.set_close_callback(self.on_close)    
        self.buffer = bytearray()
        self.header = None
        self.timer = PeriodicCallback(self.heart_beat,1000)
        self.timer.start()
        print "A new user has entered the chat room.", address   

    def heart_beat(self):
        print "heart_beat",self._address

    @coroutine   
    def run(self):    
        while True:
            raw_data = yield self._stream.read_bytes(10,partial=True) 
            self.buffer = self.buffer + raw_data
            while True:
                ret = self.parse_message()
                if ret == 0:
                    continue
                elif ret == Connection.BUFFER_NO_ENOUGH:
                    print "buffer not enough"
                    break
                elif ret == Connection.DATA_ILLEGAL:
                    print "data illegal"
                    self._stream.close()
                    return
                else :
                    print "unknow error"
                    return
    
    def parse_message(self):
        print "buffer len=" + str(len(self.buffer))
        header_len = struct.calcsize("cII")
        if self.header is None:
            if len(self.buffer) < header_len:
                return Connection.BUFFER_NO_ENOUGH
            header = struct.unpack('cII',self.buffer[0:header_len])
            print header
            if header[0] != 'H':
                print "magic number is %s" % hex(ord(header[0]))
                return Connection.DATA_ILLEGAL
            self.header = header
            self.buffer = self.buffer[header_len - 1:-1]
            print "split header buffer len=" + str(len(self.buffer))
        if self.header[1] > len(self.buffer):
            return Connection.BUFFER_NO_ENOUGH
        print "decode body"
        self.buffer = self.buffer[self.header[1] - 1:-1]
        print "split body buffer len=" + str(len(self.buffer))
        self.header = None       
        return 0

    def broadcast_messages(self, data):    
        print "User said:", data[:-1], self._address  
        for conn in Connection.clients:    
            conn.send_message(data)    
        self.read_message()    
        
    def send_message(self, data):    
        self._stream.write(data)   
            
    def on_close(self):    
        print "A user has left the chat room.", self._address
        self.timer.stop()  
        Connection.clients.remove(self)    
    
class tornado_tcpserverServer(TCPServer):  
    @coroutine  
    def handle_stream(self, stream, address):   
        print "New connection :", address, stream   
        conn = Connection(stream, address)  
        conn.run()
        print "connection num is:", len(Connection.clients)  
    
if __name__ == '__main__':    
    print "Server start ......" 
    ttlog.info("start") 
    server = tornado_tcpserverServer()    
    server.listen(8001)    
    IOLoop.instance().start()   