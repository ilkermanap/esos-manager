import os, sys
from fdisk import Fdisk

URL = "http://download.esos-project.com/packages/trunk/"
REVCACHE = "esos-zip"
WORKDIR = "workspace"


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
    def __init__(self, imgfile):
        if imgfile.find("/") > -1:
            self.imageFile = imgfile.split("/")[-1]
        else:
            self.imageFile = imgfile        
        self.rev = self.imageFile[:self.imageFile.rfind(".")]

        print "Creating work dir ", self.rev
        os.system("mkdir -p %s/boot" % self.rev)
        os.system("mkdir -p %s/root" % self.rev)
        print "Copying image file into work dir ", self.imageFile
        os.system("cp %s %s/." % (imgfile, self.rev))
        os.chdir(self.rev)
        self.image = EsosImage("%s" % (self.imageFile))
        print "Extracting root"       
        self.image.extractDir("root")
        print "Extracting boot"
        self.image.extractDir("boot")
        

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
    x = Esos(sys.argv[1])

