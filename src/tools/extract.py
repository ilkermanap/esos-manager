import os, sys

class Partition:
    def __init__(self, partline, sectorsize):
        self.partname, self.start, self.end, self.blocks, self.partid, self.system = self.parse(partline)
        self.sector = sectorsize
        
    def parse(self, line):
        line = line.replace("*","")
        x = line.split()
        partname = x[0]
        start = int(x[1])
        end = int(x[2])
        blocks = int(x[3])
        partid = x[4]
        system = ""
        for i in x[4:]:
            system += i + " "
        return (partname, start, end, blocks, partid, system)

class Fdisk:
    def __init__(self, imageName):
        self.name = imageName
        self.fname = self.name.split("/")[-1]
        self.sector = 0
        self.partitions = []
        self.probe()
        
    def probe(self):
        print("Probing partitions of %s" % self.fname)
        cmd = "fdisk -lu %s 2>/dev/null| grep -v Partition" % self.name
        ans = os.popen(cmd,"r").readlines()
        for line in ans[2:]:
            l = line.strip()
            p = l.split()
            if l.find("Units =") > -1:
                self.sector = int(p[-2])
            if l.find(self.name) > -1:
                self.partitions.append(Partition(l, self.sector))

    def mount(self, partname):
        print("Mounting %s from %s" % (partname, self.name))
        start = self.parts[partname].start
        mountcmd = "mkdir -p %s; mount -o loop,offset=%d %s  %s" % (partname, self.sector * start, self.name, partname)
        os.system(mountcmd)

    def extractDir(self, partname):
        self.mount(partname)
        print("Copying from %s's %s partition to %s" % (self.name, partname, self.fname))
        cmd = "mkdir -p %s; cp -ar %s %s/. " % (self.fname, partname, self.fname)
        os.system(cmd)
        os.system("umount %s" % partname)

    def extractTar(self, partname):
        self.mount(partname)
        cmd = "tar -Jcf  %s-%s.tar.xz %s " % (self.fname, partname, partname)
        print("Creating tar of %s partition" % partname)
        os.system(cmd)
        os.system("umount %s" % partname)
    
    def extractCpio(self, partname):
        self.mount(partname)
        print("Creating cpio of %s partition" % partname)
        cmd = "cd %s; find . -print -depth | cpio -ov > ../%s-%s.cpio ; cd .." % (partname, self.fname,  partname)
        os.system(cmd)
        os.system("umount %s" % partname)

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
    x = EsosImage(sys.argv[1])
    x.extractDir("root")
