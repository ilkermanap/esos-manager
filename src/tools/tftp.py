import glob
import os

def read_file(fname):
    temp = []
    lines = open(fname, "r").readlines()
    for line in lines:
        if line.strip().startswith("#"):
            continue
        else:
            if len(line.strip()) > 0:
                temp.append(line)
    return temp
        
class TftpAppend:
    def __init__(self, line="append"):
        self.content = line.strip()
        self.parts = self.content.split()
        if self.parts[0] is not "append":
            return None
        self.values = {}
        if len(self.parts > 1):
            for vals in self.parts[1:]:
                key, val = vals.split("=")
                self.values[key] = val

    def add_value(self, key, value):
        self.values[key] = value

    def append_str(self):
        temp = "    append "
        for k,v in self.values.items():
            temp += " %s=%s" % (k,v)
        return temp

    def control(self, basedir):
        ans = True
        msg = "OK"
        for k, v in self.values.items():
            if k in ["initrd", "ROOTIMAGE_FILE"]:
                if not os.path.isfile("%s/%s" % (basedir, v)):
                    ans = False
                    msg = "%s/%s missing" % (basedir, v)
                    return (ans, msg)
            if k == "TFTPSERVER_IP_ADDR":
                resp = os.system("ping -c 1 %s" % v)
                if resp is not 0:
                    ans = False
                    msg = "tftp server %s cannot be reached" % v
                    return (ans, msg)
        return (ans, msg)


class  TftpEntry:
    def __init__(self):
        self.label = None
        self.menu = None
        self.menulabel = None
        self.kernel = None
        self.append = None
    
    def add_line(self, line):
        if 
    
class TftpConfig:
    def __init__(self, fname):
        self.lines = read_file(fname)
        

class Tftpboot:
    def __init__(self, basedir="/tftpboot"):
        self.basedir = basedir
        self.config_files = glob.glob("%s/pxelinux.cfg/*")

