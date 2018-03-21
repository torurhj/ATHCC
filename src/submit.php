<?php

$touchX = $_POST['touchX'];
$touchY = $_POST['touchY'];
$targetX = $_POST['targetX'];
$targetY = $_POST['targetY'];
$timeStart = $_POST['timeStart'];
$timeEnd = $_POST['timeEnd'];
$expID = $_POST['expID'];
$name = $_POST['name'];
$age = $_POST['age'];
$hand = $_POST['hand'];
$thumb = $_POST['thumb'];
$gender = $_POST['gender'];
$totalX = $_POST['totalX'];
$totalY = $_POST['totalY'];
$filepath = "data/data.csv";
$fh = fopen($filepath, 'a') or die("Can't create file");
// If the header is missing
if ( 0 == filesize( $filepath ) ){
    fputcsv($fh, ["totalX","totalY","touchX","touchY","targetX","targetY","timeStart","timeEnd","expID","name","age","hand","thumb","gender"]);
}

fputcsv($fh, [$totalX,$totalY,$touchX,$touchY,$targetX,$targetY,$timeStart,$timeEnd,$expID,$name,$age,$hand,$thumb,$gender]);

echo("ohwee");
?>
