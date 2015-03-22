= Esos Manager =

== Esos ==

Detailed information about esos is at [https://code.google.com/p/enterprise-storage-os/](https://code.google.com/p/enterprise-storage-os)

Briefly, it is an open source, high performance, block-level storage platform.

== This project ==

The aim of this project is to provide the tools to create the pxe bootable
images from esos images. All development will be on github. Feel free to post issues.

Setting up network boot environment requires pxe, dhpc, tftp knowledge, 
which will not be given here. But the scripts will provide the parts to 
be included in configuration files.

There are some problems to solve. Network booted esos environment has no
place to sync it's configuration. Scripts are being written to provide a 
way to sync configuration with a web server. 

For the first phase, the aim is to write to tools to generate the pxe bootable 
images, and it's pxe and dhcp configuration text's. Also with a working
configuration sync mechanism.

The second phase will include a manager application, which uses the synced 
configurations to change the configurations and apply it to several esos 
appliances.

== Changes ==

* The init script inside initramfs is adapted to download the root image from 
tftp. 

* conf_sync application now points to web_sync.sh. 
* Several startup scripts with references to usb device will be adapted to no usb device




