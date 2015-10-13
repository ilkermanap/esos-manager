import os, sys
from extract import EsosImage, Cpio
from tftp import *
import argparse


prs = argparse.ArgumentParser(description="Test app")
prs.add_argument("--file")
prs.add_argument("--skip_unzip", action="store_true")

args = prs.parse_args()



if args.skip_unzip :
    unzip = False
else:
    unzip = True

if args.file:
    zipf = args.file
else:
    print("No zip file given")
    sys.exit()

img = zipf.replace(".zip","")

if unzip:
    print("Extracting zip")
    os.system("unzip %s" % zipf)
os.chdir(img)
if unzip:
    cmd = "bzip2 -d %s.img.bz2" % img
    print("Extracting image file")
    os.system(cmd)
    img1 = EsosImage("%s.img" % img)
    print("Extracting root")
    img1.extractDir("root")
    print("Extracting boot")
    img1.extractDir("boot")
initramfs = Cpio("initram-temp")
print("extracting initramfs")
initramfs.open("boot/initramfs.cpio.gz")
print("adding init to initramfs")
initramfs.add_file("../../initramfs/init", "/")

cmd = "mkdir -p initram-temp/lib/firmware; cp -r root/lib/firmware/* initram-temp/lib/firmware/."
print "copying firmwares to initramfs"
os.system(cmd)

cmd = "cp ../../rootfs/* root/usr/local/sbin/." 
print("adding new sync utils to rootfs")
os.system(cmd)

wsync = "root/usr/local/sbin/web_sync.sh"
usync = "root/usr/local/sbin/usb_sync.sh"
cmd = "rm -f %s && cp %s %s " % (usync, wsync, usync)
print("Replacing usb_sync.sh with web_sync.sh.")
os.system(cmd)


f = open("root/etc/rc.local", "a")
f.write("dmesg | grep bootserver | awk -F= '{print $2}' | awk -F, '{print $1}' > /etc/esos-bootserver.conf\n")
f.close()

rootfs=Cpio("root")
print("creating the compressed root file system cpio image")
if unzip:
    rootfs.create("rootfs-%s" % img.replace("/",""))
print("creating the uncompressed initramfs cpio image")
initramfs.create("initramfs-%s.cpio" %  img.replace("/",""), gzip = False)
tf = TftpConfig()
tfent = TftpEntry()
tfent.label = img
tfent.menu = "default"
tfent.menulabel = img
print "img=",img
print "%s/*esos.prod*" % img
print  glob.glob("*esos.prod*")
tfent.kernel = "esos/%s" % glob.glob("*esos.prod*")[0].split("/")[-1]
tfappend = TftpAppend()
tfappend.add_value("initrd","esos/initramfs-%s" % img.replace("/",""))
tfappend.add_value("console","ttyS1,115200N8")
tfappend.add_value("ip","dhcp")
tfappend.add_value("hostname","hostname_of_the_appliance")
tfappend.add_value("domain","domain_of_the_network")
tfappend.add_value("ROOTIMAGE_FILE","esos/rootfs-%s" % img.replace("/",""))

print "tftp, initrd=", tfappend.values['initrd']
os.chdir("../.")


