#! /bin/sh

# $Id: conf_sync.sh 520 2013-09-06 15:18:59Z msmith626@gmail.com $

# Write the SCST configuration to a file (we don't hide stderr)
/usr/sbin/scstadmin -force -nonkey -write_config /etc/scst.conf > /dev/null || exit 1
# Synchronize the local configuration with the USB flash drive
#/usr/local/sbin/usb_sync.sh || exit 1
/usr/local/sbin/web_sync.sh || exit 1

