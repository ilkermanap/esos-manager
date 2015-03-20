<?php
$name = $_GET['name'];
$ff = "http://".$_SERVER['REMOTE_ADDR'].":8000/".$name;
$content = file_get_contents($ff);
$f =  fopen("/var/esos/confs/".$name,'w');
fwrite($f,$content);
fclose($f);
?>
