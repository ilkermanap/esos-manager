#!/usr/bin/env python 
import os, sys, urllib
import time


SERVER = sys.argv[2]
FNAME = sys.argv[1]
url = "http://%s/esos/recvconf.php?name=%s" % (SERVER, sys.argv[1])
os.system("mkdir -p temporary")
os.system("cp %s temporary" % sys.argv[1])
os.chdir("temporary")
os.system("python -m SimpleHTTPServer & ")
time.sleep(1)
x = urllib.urlopen(url).read()
os.system("ps aux | grep SimpleHTTP | grep -v grep | awk '{print $1}' | xargs kill -9")
