import os, sys
from extract import EsosImage, Cpio


zipf = sys.argv[1]
img = zipf.replace(".zip","")


print("Extracting zip")
os.system("unzip %s" % zipf)
os.chdir(img)
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
initramfs.add_file("../src/initramfs/init", "/")
cmd = "cp ../src/rootfs/* root/usr/local/sbin/." 
print("adding new sync utils to rootfs")
os.system(cmd)
rootfs=Cpio("root")
print("creating the compressed root file system cpio image")
rootfs.create("rootfs-%s" % img.replace("/",""))
print("creating the uncompressed initramfs cpio image")
initramfs.create("initramfs-%s" %  img.replace("/",""), gzip = False)
os.chdir("../.")


