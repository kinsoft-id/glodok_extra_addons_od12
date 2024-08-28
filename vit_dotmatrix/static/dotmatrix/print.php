<?php
header('Access-Control-Allow-Origin: *'); 
header('Access-Control-Allow-Methods: GET, PUT, POST, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Origin, X-Requested-With, Content-Type, Accept, Key');

$printer_data = isset($_REQUEST['printer_data'])?$_REQUEST['printer_data']:False;

require_once("printer.php");
$printername = 'Generic Printer';

if($printer_data){
	$printer = new RawPrinter($printername);
	$printer->send($printer_data);
	echo "Done";
}
else{
	echo "Nothing to print!";	
}
