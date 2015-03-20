<?php

$client = $_SERVER['REMOTE_ADDR'];
$mac = popen('arp -a '.$client, 'r').read();
$fname = "/var/esos/confs/".$mac."-conf.cpio.gz";
$tempdir = popen

system("mkdir -p /var/www/html/");
system("cp ".$fname. "");



<?
