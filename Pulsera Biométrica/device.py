import database as db

class Device:
    class Sensor:
        def __init__(self, id : int, model : str, type : str):
            self.id = id
            self.model = model
            self.type = type

    def __init__(self, id : int, model : str, *args : tuple[int, str, str]):
        self.id = id
        self.model = model
        self.sensors = []
        for data in args:
            sensor = self.Sensor(data[0], data[1], data[2])
            self.sensors.append(sensor)
        self.database = db.Database()

    def add_sensor(self, id : int, model: str, type: str):
        self.sensors.append(self.Sensor(id, model, type))
        return self.database("INSERT INTO sensor VALUES (%s, %s, %s, %s)", id, self.id, model, type)

    def add(self):
        try:
            sql = "INSERT INTO dispositivo (idDispositivo, modelo) VALUES (%s, %s)"
            self.database(sql, self.id, self.model)
            for sensor in self.sensors:
                sql = "INSERT INTO sensor VALUES (%s, %s, %s, %s)"
                self.database(sensor.id, self.id, sensor.model, sensor.type)
        except:
            print("Data Not Added!")
            return False

    def __call__(self):
        values = []
        sql = "SELECT * FROM biometrico WHERE idSensor = %s AND modelo = %s AND username = (SELECT username FROM dispositivo WHERE idDispositivo = %s)"
        for sensor in self.sensors:
            values.append(self.database(sql, sensor.id, sensor.model, self.id))
        return values

    def get_biometrics(self, username : str) -> dict:
        result = {}
        for sensor in self.sensors:
            if sensor.type == "oxim-fc":
                sql = "SELECT frecuenciaCardiaca, tiempoRegistro FROM frecuenciascardiacas NATURAL JOIN biometrico WHERE username = %s AND idSensor = %s AND modelo = %s"
                result["cardiacFrequency"] = self.database(sql, username, sensor.id, sensor.model)
                sql = "SELECT oximetria, tiempoRegistro FROM oximetria NATURAL JOIN biometrico WHERE username = %s AND idSensor = %s AND modelo = %s"
                result["oximetry"] = self.database(sql, username, sensor.id, sensor.model)
            elif sensor.type == "temp":
                sql = "SELECT temperatura, tiempoRegistro FROM temperatura NATURAL JOIN biometrico WHERE username = %s AND idSensor = %s AND modelo = %s"
                result["temperature"] = self.database(sql, username, sensor.id, sensor.model)
            elif sensor.type == "gyro":
                sql = "SELECT acc_X, acc_Y, acc_X, tiempoRegistro FROM caidas NATURAL JOIN biometrico WHERE username = %s AND idSensor = %s AND modelo = %s"
                result["acceleration"] = self.database(sql, username, sensor.id, sensor.model)
                sql = "SELECT rot_X, rot_Y, rot_X, tiempoRegistro FROM caidas NATURAL JOIN biometrico WHERE username = %s AND idSensor = %s AND modelo = %s"
                result["rotation"] = self.database(sql, username, sensor.id, sensor.model)
        return result
    
if __name__ == "__main__":
    device = Device(0, "Pilot", (0, "MAX30102", "oxim-fc"), (0, "DS18B20", "temp"), (0, "IMU MPU6050", "gyro"))
    for data in device():
        print(data)