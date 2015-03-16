#! /bin/sh

# $Id: startup.sh 429 2013-03-29 04:45:38Z msmith626@gmail.com $

# System startup script; this script will check for vmcore files, grab some
# information from the ESOS system, and then emails the root user everything.

EMAIL_TO="root"
EMAIL_FROM="root"
LOGS_MNT="/mnt/logs"

# Check for vmcore files on the esos_logs filesystem
mount ${LOGS_MNT}
if ls ${LOGS_MNT}/*vmcore* > /dev/null 2>&1; then
	vmcore_files=""
	for i in `ls ${LOGS_MNT}/*vmcore*`; do
		vmcore_files="${vmcore_files}${i}\n"
	done
fi
umount ${LOGS_MNT}

# Send the email message
sendmail -t << _EOF_
To: ${EMAIL_TO}
From: ${EMAIL_FROM}
Subject: ESOS System Startup - `hostname` (`date`)
Enterprise Storage OS on host "`hostname`" has started. If this system startup is expected, you can probably ignore this.

`test "${vmcore_files}" != "" && echo "** Warning! Kernel crash dump file(s) detected:"; echo -e "${vmcore_files}"`

`test -d "/sys/kernel/scst_tgt" && scstadmin -list_target`
`test -d "/sys/kernel/scst_tgt" && scstadmin -list_device`
_EOF_
