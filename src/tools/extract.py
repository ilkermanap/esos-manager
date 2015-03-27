import os, sys
from fdisk import Fdisk
URL = "http://download.esos-project.com/packages/trunk/"
REVCACHE = "esos-zip"
WORKDIR = "workspace"

os.system("mkdir -p %s %s " % (REVCACHE, WORKDIR))

class Cpio:
    def __init__(self, tempdir):
        self.temp = tempdir
        os.system("mkdir -p %s"  % self.temp)

    def create(self, directory, parameters):
        pass

    def addFile(self, newfile, location):
        pass

    def open(self, cpiofile):
        c = ""
        ext = cpiofile.split(".")[-1]
        if ext == "xz":
            c = "xzcat "
        if ext == "gz":
            c = "gzcat "
        if ext == "cpio":
            c = ""
        if ext == "bz2":
            c = "bzcat "
        cmd = "cd %s; %s  ../%s | cpio -idv   " % (self.temp, c, cpiofile )
        os.system(cmd)

class Esos:
    def __init__(self, rev, url, cache, workdir):
        self.url = url
        self.rev = rev
        self.cache = cache
        self.image = None
        self.workdir = "%s/%d" % (workdir, rev)
        if not(os.path.exists(self.workdir)):
            os.system("mkdir -p %s" % self.workdir)
        if not(os.path.exists("%s/esos-trunk_r%d.zip" % (cache, rev))):
            status = self.retrieve()
            if status != 0:
                print "Problem with image download"
                print "%s/esos-trunk_r%d.zip" % (url, rev)
                sys.exit()
        else:
            print("%s/esos-trunk_r%d.zip exists" % (cache, rev))


    def setupWorkdir(self):
        if not(os.path.exists(self.workdir)):
            print "xx"
            os.system("mkdir -p %s" % self.workdir)
            cmd = "cd %s; unzip ../../%s/esos-trunk_r%d.zip" \
                  % (self.workdir, self.cache, self.rev)
            os.system(cmd)
        self.image = EsosImage("%s/esos-trunk_r%d/esos-trunk_r%d.img" \
                               % (self.workdir, self.rev, self.rev))
        self.image.extractDir("root")
        self.image.extractDir("boot")

    def unzip(self):
        cmd = "mkdir -p %s"

    def retrieve(self):
        cmd = "wget  %s/esos-trunk_r%d.zip -O  %s/esos-trunk_r%d.zip" \
              % (self.url, self.rev, self.cache,self.rev)
        return os.system(cmd)



class EsosImage(Fdisk):
    def __init__(self, imageName):
        Fdisk.__init__(self, imageName)
        if len(self.partitions) < 4:
            print("Esos images must have 4 partitions. %s image doesn't" % self.name)
            sys.exit(1)
        self.parts = {}
        self.parts["boot"] = self.partitions[0]
        self.parts["root"] = self.partitions[1]
        self.parts["conf"] = self.partitions[2]
        self.parts["logs"] = self.partitions[3]

if __name__ == "__main__":
    x = Esos(766, URL, REVCACHE, WORKDIR)
    x.setupWorkdir()
