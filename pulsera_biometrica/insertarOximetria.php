<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);
    include 'conexion.php'; // Abre la conexión a la Base de datos
    include 'insertarBiometrico.php';
    if ($_GET) {
        // Recuperamos los datos enviados. Solo el valor de la temperatura y el id del sensor
        $valor = $_GET['value'];
        // Identifcadores definidos en la Base de datos/tablas
        $sqlInserta = 'INSERT INTO oximetria(idSensor, modelo, idBiometrico, username, oximetria) VALUES (?, ?, ?, ?, ?)';
        $insertar = $pdo->prepare($sqlInserta);
        try {
            $resultado = $insertar->execute(array($idSensor, $modelo, $idBiometrico, $username, $valor));
            if ($resultado == true) {
                $valor = null;
                $pdo = null;
                $sqlInserta = null;
                $insertar = null;
                $valor = null;
                $tiempo = null;
                $idBiometrico = null;
                $username = null;
                $idSensor = null;
                $modelo = null;
                $buscar = null;
                $sqlBusca = null;
                echo 'Datos guardados correctamente';
            } else {
                echo 'Error al insertar ', $resultado;
            }
        } catch(Exception $e) {
            echo $e->getMessage();
        }
    } else {
    echo 'No hay parámetros del método GET';
    }
    // http://localhost/pulsera_biometrica/insertarOximetria.php?idSensor=0&modelo=MAX30102&idBiometrico=0&username=StephaneJunior&value=97
?>