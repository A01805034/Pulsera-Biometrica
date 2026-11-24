<?php
    ini_set('display_errors', 1);
    ini_set('display_startup_errors', 1);
    error_reporting(E_ALL);
    include 'conexion.php'; // Abre la conexión a la Base de datos
    if ($_GET) {
        // Recuperamos los datos enviados. Solo el valor de la temperatura y el id del sensor
        $idSensor = $_GET['idSensor'];
        $modelo = $_GET['modelo'];
        $tiempo = date('Y-m-d H:i:s');
        // Identifcadores definidos en la Base de datos/tablas
        $sqlBusca = 'SELECT username FROM persona INNER JOIN dispositivo USING (username) WHERE idDispositivo = (SELECT idDispositivo FROM sensor INNER JOIN dispositivo USING (idDispositivo) WHERE idSensor = ? AND sensor.modelo = ?)';
        $buscar = $pdo ->prepare($sqlBusca);
        $buscar -> execute(array($idSensor, $modelo));
        $resultado = $buscar -> fetch();
        $username = $resultado['username'];
        $sqlBusca = 'SELECT MAX(idBiometrico) AS max FROM biometrico WHERE idSensor = ? AND username = ? AND modelo = ?';
        $buscar = $pdo ->prepare($sqlBusca);
        $buscar -> execute(array($idSensor, $username, $modelo));
        $resultado = $buscar -> fetch();
        if($resultado['max'] !== null){
            $idBiometrico = $resultado['max'];
            $idBiometrico++;
        }
        else{
            $idBiometrico = 0;
        }
        $sqlInserta = 'INSERT INTO biometrico(idSensor, modelo, idBiometrico, username, tiempoRegistro) VALUES (?, ?, ?, ?, ?)';
        $insertar = $pdo->prepare($sqlInserta);
        try {
            $resultado = $insertar->execute(array($idSensor, $modelo, $idBiometrico, $username, $tiempo));
            if ($resultado == true) {
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
?>