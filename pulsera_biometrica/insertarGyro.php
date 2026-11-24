<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);
    include 'conexion.php'; // Abre la conexión a la Base de datos
    include 'insertarBiometrico.php';
    if ($_GET) {
        // Recuperamos los datos enviados. Solo el valor de la temperatura y el id del sensor
        $accX = $_GET['accX'];
        $accY = $_GET['accY'];
        $accZ = $_GET['accZ'];
        $rotX = $_GET['rotX'];
        $rotY = $_GET['rotY'];
        $rotZ = $_GET['rotZ'];
        // Identifcadores definidos en la Base de datos/tablas
        $sqlInserta = 'INSERT INTO caidas(idSensor, modelo, idBiometrico, username, acc_X, acc_Y, acc_Z, rot_X, rot_Y, rot_Z) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)';
        $insertar = $pdo->prepare($sqlInserta);
        try {
            $resultado = $insertar->execute(array($idSensor, $modelo, $idBiometrico, $username, $accX, $accY, $accZ, $rotX, $rotY, $rotZ));
            if ($resultado == true) {
                $valor = null;
                $pdo = null;
                $sqlInserta = null;
                $insertar = null;
                $tiempo = null;
                $idBiometrico = null;
                $username = null;
                $idSensor = null;
                $modelo = null;
                $accX = null;
                $accY = null;
                $rotX = null;
                $rotY = null;
                $accZ = null;
                $rotZ = null;
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
    // http://localhost/pulsera_biometrica/insertarGyro.php?idSensor=0&modelo=MAX30102&idBiometrico=0&username=StephaneJunior&accX=1&accY=1&accZ=1&rotX=1&rotY=1&rotZ=1
?>