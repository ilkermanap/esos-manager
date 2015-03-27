#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

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
    """
    this class is not using devices.
    it is using the disk images with partitions in it.
    """
    def __init__(self, imageName):
        """
        usage  x = Fdisk("test.img")
        """
        self.name = imageName
        self.fname = self.name.split("/")[-1]
        self.sector = 0
        self.partitions = []
        self.probe()

    def probe(self):
        """
        Probes the file to look for partitions
        """
        print("Probing partitions of %s" % self.fname)
        cmd = "fdisk -lu %s 2>/dev/null| grep -v Partition" % self.name
        ans = os.popen(cmd,"r").readlines()
        for line in ans[2:]:
            l = line.strip()
            p = l.split()
            if l.find("Units") > -1:
                self.sector = int(p[-2])
            if l.find(self.name) > -1:
                self.partitions.append(Partition(l, self.sector))

    def mount(self, partname):
        """
        mounts the partition given by the partname

        usage :  x.mount("root")
        """
        print("Mounting %s from %s" % (partname, self.name))
        start = self.parts[partname].start
        offset = self.sector * start
        mountcmd = "mkdir -p %s; mount -o loop,offset=%d %s  %s" % (partname, offset, self.name, partname)
        print mountcmd
        os.system(mountcmd)

    def extractDir(self, partname):
        """
        Copy the contents of the partition to the directory named as the
        partition name
        """
        self.mount(partname)
        print("Copying from %s's %s partition to %s" % (self.name, partname, self.fname))
        cmd = "mkdir -p %s; cp -ar %s %s/. " % (self.fname, partname, self.fname)
        os.system(cmd)
        os.system("umount %s" % partname)

    def extractTar(self, partname):
        """
        Create a tar archive for a given partition. xz is used as compression
        tar file is named as imagefilename-partitionname.tar.xz

        usage: x.extractTar("boot")
        """
        self.mount(partname)
        cmd = "tar -Jcf  %s-%s.tar.xz %s " % (self.fname, partname, partname)
        print("Creating tar of %s partition" % partname)
        os.system(cmd)
        os.system("umount %s" % partname)

    def extractCpio(self, partname):
        """
        Create a cpio archive for a given partition.
        Cpio archive is named as imagefilename-partitioname.cpio

        usage:  x.extractCpio("home")
        """
        self.mount(partname)
        print("Creating cpio of %s partition" % partname)
        cmd = "cd %s; find . -print -depth | cpio -ov > ../%s-%s.cpio ; cd .." % (partname, self.fname,  partname)
        os.system(cmd)
        os.system("umount %s" % partname)
