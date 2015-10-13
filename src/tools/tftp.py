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
        if (self.parts[0] != "append"):
            return None
        self.values = {}
        if len(self.parts) > 1:
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
        pass
    
class TftpConfig:
    def __init__(self, fname=None):
        labelfound = False
        self.header = []
        self.entries = {}
        if fname is None:
            self.header = ['DEFAULT menu.c32','prompt 0','timeout 5']
        else:
            print "ttfpconfig icinde ", fname
            self.lines = read_file(fname)
            temp_entry = None
            for line in self.lines:
                if line.lower().startswith("label"):
                    if labelfound == True:
                        self.entries[temp_entry.label] = temp_entry
                    labelfound = True
                    lbl = line.split()[1]
                    temp_entry = TftpEntry()
                    temp_entry.label = lbl

                if not labelfound:
                    self.header.append(line)
                else:
                    if line.lower().startswith("label"):
                        pass
                    else:
                        if line.strip().lower().startswith("menu label"):
                            temp_entry.menulabel = line.split()[2]
                        elif line.strip().lower().startswith("menu"):
                            temp_entry.menu = line.split()[1]
                        if line.strip().lower().startswith("kernel"):
                            temp_entry.kernel = line.split()[1]
                        if line.strip().lower().startswith("append"):
                            temp_entry.append = TftpAppend(line = line.strip())

    def add_entry(self, new_entry):
        self.entries[new_entry.label] = new_entry


class Tftpboot:
    def __init__(self, basedir="/tftpboot"):
        self.basedir = basedir
        self.config_files = glob.glob("%s/pxelinux.cfg/*" % self.basedir)
        self.configs = {}
        for f in self.config_files:
            self.configs[f] = TftpConfig(f)



if __name__ == "__main__":
    tft = Tftpboot()

