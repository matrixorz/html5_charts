#!/usr/bin/env python

"""

Simple http server.

Just handles 2 path calls:
- One terminated with json
- One terminated with html

Json sends a Json dummy file
HTML plots in real time the json data

"""


import time
import BaseHTTPServer
import threading
from datetime import datetime
import random
import json
import urlparse
from SocketServer import ThreadingMixIn

__author__ = "Ricardo FERRAZ LEAL"
__credits__ = ["Ricardo FERRAZ LEAL"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Ricardo FERRAZ LEAL"
__email__ = "ricleal@gmail.com"
__status__ = "Testing"


HOST_NAME = 'localhost' # 
PORT_NUMBER = 8080 # 

# html the server handles
html_page = "plot.html"

# Global variable (For threading)
simLog = None


class SimulateLogFetcherThread(threading.Thread):
    """
    This thread will simulate a log reader from a file and 
    return an json object
    
    Call as:
    t = SimulateLogFetcherThread()
    t.start()
    """
    def __init__(self):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        # This stacks contains the last stackSize readings from the log file 
        self.stack1 = []
        self.stack2 = []
        self.stackSize = 50
        self.jsonOutput = None
    
    def stop(self):
        print "Stopping thread..."
        self._stop.set()

    def stopped(self):        
        return self._stop.isSet()
    
    def autoAppendStack(self,stack,el):
        """ Appends the stack and
        Keeps the stack size constant """
        if len(stack) > self.stackSize :
            stack.pop(0)
        stack.append(el)
            
    
    def run(self):
        """ 
        Plot is date vs random number
        """
        while not self.stopped():
            # date format handled by javascript
            nowStr = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            # random value. It should come from the logger in a real example
            value1 = random.randint(1,10)
            pair1 = []
            pair1.append(nowStr)
            pair1.append(value1)
            self.autoAppendStack(self.stack1,pair1)
            
            value2 = random.randint(1,10)
            pair2 = []
            pair2.append(nowStr)
            pair2.append(value2)
            self.autoAppendStack(self.stack2,pair2)
            
            out1 = {}
            out1["label"] = "Sim Data 1"
            out1["data"] = self.stack1
            
            out2 = {}
            out2["label"] = "Sim Data 2"
            out2["data"] = self.stack2
            
            out = [out1,out2]
            
            self.jsonOutput = json.dumps(out)
            time.sleep(1)

class JsonHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """
    This class will only handle the GET and POST calls to the server
    
    I will ignore the posts for now.
    
    """
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", 'application/json; charset=utf8')
        self.end_headers()
    def do_GET(self):
        """Respond to a GET request."""
        # Gets URL
        parsedUrlPath = urlparse.urlparse(self.path)
        print "* Parsed path -> ", parsedUrlPath.path
        
        if parsedUrlPath.path.find("htm") >= 0:
            # Send html file defined on the top
            self.send_response(200)
            self.send_header("Content-type", 'text/html; charset=utf8')
            self.end_headers()
            lines = '\n'.join(open(html_page).read().splitlines())
            self.wfile.write(lines)
        elif parsedUrlPath.path.find("json") >= 0:
            global simLog
            out = simLog.jsonOutput
            print 'JsonHandler Content sent:'
            print out
            print '-------------------------'
            self.send_response(200)
            self.send_header("Content-type", 'application/json; charset=utf8')
            self.end_headers()
            self.wfile.write(out)
        else :
            self.send_response(404)
            self.send_header("Content-type", 'text/html; charset=utf8')
            self.end_headers()
            self.wfile.write("<h1>Page is not implemented yet!</h1>")
        
        
        
class ThreadingHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass    

# If needed to open the same server in several ports
#def serve_on_port(port):
#    server = ThreadingHTTPServer(("localhost",port), Handler)
#    server.serve_forever()
#
#Thread(target=serve_on_port, args=[1111]).start()
#serve_on_port(2222)

    

if __name__ == '__main__':
    

    httpd = ThreadingHTTPServer((HOST_NAME, PORT_NUMBER), JsonHandler)    
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    simLog = SimulateLogFetcherThread()
    simLog.start()
    try:
        httpd.serve_forever()
        
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    simLog.stop()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)


