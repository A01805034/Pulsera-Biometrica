<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
 try{
    $pdo = new PDO('mysql:host=localhost;dbname=reto_iot','root','');
    echo '<h1>Conexión exitosa a la base de datos.</h1>';
 }
 catch(PDOException $e){
    echo 'Error al conectarse a la base de datos';
    print 'Error: '.$e;
    die();
 }
?>