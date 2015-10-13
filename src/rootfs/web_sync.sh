#! /bin/sh

# This script will synchronize configuration files between the 
# TFTP Server and the root tmpfs filesystem.


WEBSERVER=`cat /etc/esos-bootserver.conf` 
CONF_MNT="/mnt/conf"
CONF_CPIO="/mnt/confcpio"
SYNC_DIRS="/etc /var/lib" # These are absolute paths (leading '/' required)
MKDIR="mkdir -m 0755 -p"
CP="cp -af"
CPIO="cpio -pdum --quiet"
LOOP_IFS=$(echo -en "\n\b")
ORIG_IFS=${IFS}


DATE=`date +%Y%m%d%H%m`
HWADDR=`ifconfig | grep -v "127.0.0" | grep -B1 "inet addr" | head -n1 | awk '{print $NF}'`
IPADDR=`ifconfig | grep -v "127.0.0" | grep -B1 "inet addr" | head -n2 | tail -n1 | awk -F: '{print $2}' | awk '{print $1}'`
FNAME1=${HWADDR}-conf.cpio.gz
FNAME2=${HWADDR}-${IPADDR}-${DATE}-conf.cpio.gz


mkdir -p ${CONF_MNT} ${CONF_CPIO}
mount -t tmpfs -o size=50m tmpfs ${CONF_MNT}   || exit 1
mount -t tmpfs -o size=50m tmpfs ${CONF_CPIO}   || exit 1

# Get conf from tftp
cd ${CONF_CPIO}
#FIXME get latest from webserver
#tftp -g -r /esos/conf/${FNAME1} ${TFTPSERVER}
# extract from cpio archive
curl http://${WEBSERVER}/esos/sendconf.php?mac=${HWADDR} > ${FNAME1}

cd ${CONF_MNT}
gzip -d -c ${CONF_CPIO}/${FNAME1} |  cpio -imd

# Synchronize each directory
for i in ${SYNC_DIRS}; do
    ${MKDIR} ${CONF_MNT}${i}
    # Make sure all of the local directories exist on TFTP
    local_dir_base="${i}"
    IFS=${LOOP_IFS}
    for j in `test -d ${local_dir_base} && find ${local_dir_base} -type d \( ! -name rc.d \)`; do
        IFS=${ORIG_IFS}
        local_dir=${j}
        tftp_dir=${CONF_MNT}${local_dir}
        # The directory doesn't exist on the USB drive
        if [ ! -d "${tftp_dir}" ]; then
            # Create the directory
            echo ${local_dir} | ${CPIO} ${CONF_MNT}
            continue
        fi
        IFS=${LOOP_IFS}
    done
    # Make sure all of the local files exist on TFTP
    IFS=${LOOP_IFS}
    for j in `test -d ${local_dir_base} && find ${local_dir_base} -path /etc/rc.d -prune -o -type f -print`; do
        IFS=${ORIG_IFS}
        local_file=${j}
        tftp_file=${CONF_MNT}${local_file}
        # The file doesn't exist on the TFTP drive
        if [ ! -f "${tftp_file}" ]; then
            # Copy the local file to TFTP
            ${CP} "${local_file}" "${tftp_file}"
            continue
        fi
        # The file exists in both locations
        if [ -f "${tftp_file}" ] && [ -f "${local_file}" ]; then
            # Check and see which version is the newest
            if [ "${local_file}" -nt "${tftp_file}" ]; then
                # Update the USB file with the local copy
                ${CP} "${local_file}" "${tftp_file}"
            elif [ "${local_file}" -ot "${tftp_file}" ]; then
                # Update the local file with the USB copy
                ${CP} "${tftp_file}" "${local_file}"
            else
                # The files are the same; do nothing
                continue
            fi
        fi
        IFS=${LOOP_IFS}
    done
    # Make sure all of the USB directories exist locally
    tftp_dir_base="${CONF_MNT}${i}"
    IFS=${LOOP_IFS}
    for j in `test -d ${tftp_dir_base} && find ${tftp_dir_base} -type d`; do
        IFS=${ORIG_IFS}
        tftp_dir=${j}
        local_dir=`echo "${tftp_dir}" | sed -e s@${CONF_MNT}@@`
        # The directory doesn't exist on the local file system
        if [ ! -d "${local_dir}" ]; then
            # Create the directory
            cd ${CONF_MNT} && echo ${tftp_dir} | sed -e s@${CONF_MNT}/@@ | ${CPIO} / && cd - > /dev/null
            continue
        fi
        IFS=${LOOP_IFS}
    done
    # Make sure all of the USB files exist locally
    IFS=${LOOP_IFS}
    for j in `test -d ${tftp_dir_base} && find ${tftp_dir_base} -type f`; do
        IFS=${ORIG_IFS}
        tftp_file=${j}
        local_file=`echo "${tftp_file}" | sed -e s@${CONF_MNT}@@`
        # The file doesn't exist on the local file system
        if [ ! -f "${local_file}" ]; then
            # Copy the USB file to the local FS
            ${CP} "${tftp_file}" "${local_file}"
            continue
        fi
        # The file exists in both locations
        if [ -f "${local_file}" ] && [ -f "${tftp_file}" ]; then
            # Check and see which version is the newest
            if [ "${tftp_file}" -nt "${local_file}" ]; then
                # Update the local file with the USB copy
                ${CP} "${tftp_file}" "${local_file}"
            elif [ "${tftp_file}" -ot "${local_file}" ]; then
                # Update the USB file with the local copy
                ${CP} "${local_file}" "${tftp_file}"
            else
                # The files are the same; do nothing
                continue
            fi
        fi
        IFS=${LOOP_IFS}
    done
done

# Make sure our sole symbolic link for the time zone is up to date
local_tz_link="/etc/localtime"
tftp_tz_link="${CONF_MNT}${local_tz_link}"
if [ ! -L "${tftp_tz_link}" ] && [ -L "${local_tz_link}" ]; then
    # The link doesn't exist on the USB drive
    ${CP} ${local_tz_link} ${tftp_tz_link}
elif [ ! -L "${local_tz_link}" ] && [ -L "${tftp_tz_link}" ]; then
    # The link doesn't exist on the local file system
    ${CP} ${tftp_tz_link} ${local_tz_link}
elif [ -L "${tftp_tz_link}" ] && [ -L "${local_tz_link}" ]; then
    # The link exists in both locations
    if [ $(stat -c %Y ${local_tz_link}) -gt $(stat -c %Y ${tftp_tz_link}) ]; then
        # Update the USB link with the local copy
        ${CP} ${local_tz_link} ${tftp_tz_link}
    elif [ $(stat -c %Y ${local_tz_link}) -lt $(stat -c %Y ${tftp_tz_link}) ]; then
        # Update the local link with the USB copy
        ${CP} ${tftp_tz_link} ${local_tz_link}
    else
        # The links are the same; do nothing
        continue
    fi
fi





# create new cpio archive
cd ${CONF_MNT}
find . -print | cpio -ov -H newc | gzip -9 -c >  ${CONF_CPIO}/${FNAME1}
find . -print | cpio -ov -H newc | gzip -9 -c >  ${CONF_CPIO}/${FNAME2}


# put conf to tftp
cd ${CONF_CPIO}

/usr/local/sbin/web.py ${FNAME1} ${WEBSERVER}
sleep 5
/usr/local/sbin/web.py ${FNAME2} ${WEBSERVER}
cd /
umount ${CONF_MNT} || exit 1
umount ${CONF_CPIO} || exit 1
