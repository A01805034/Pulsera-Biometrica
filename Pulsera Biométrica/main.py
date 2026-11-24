import user as us
import device as dv
import database as db
import hashlib as hsh
import platform
import subprocess
import matplotlib.pyplot as plt
import datetime as dt
import broker as bk
import mysql
from plyer import notification as nt

def send_alert(device : dv.Device, user : us.User, time : dt.datetime, type : str, description : str):
    database = db.Database()
    try:
        sql = "INSERT INTO dispositivopersona VALUES (%s, %s, %s, %s, %s)"
        database(sql, device.id, user.username, time, type, description)
        find = "SELECT contact FROM usuariocontacto WHERE username = %s"
        contacts = database(find, user.username)
        for contact in contacts:
            database(sql, device.id, contact[0], time, "From " + user.name + ":\n" + type, description)
        return nt.notify("Alert: " + type, description)
    except mysql.connector.errors.IntegrityError:
        return nt.notify("Alert: " + type, description + "\nWarning: Couldn't register in the database!")

def warn_temperature(values : list[float], time : dt.datetime, device : dv.Device, user : us.User):
    if (average := sum(values) / len(values)) > 37.2:
        return send_alert(device, user, time, "High Temperature", "A high temperature has been detected: " + str(average) + "\nEmission time: " + time.strftime("%d/%m/%Y %H:%M:%S"))
    elif average < 36.1:
        return send_alert(device, user, time, "Low Temperature", "A low temperature has been detected: " + str(average) + "\nEmission time: " + time.strftime("%d/%m/%Y %H:%M:%S"))

def warn_oximetry(values : list[float], time : dt.datetime, device : dv.Device, user : us.User):
    if(average := sum(values) / len(values)) < float(95):
        return send_alert(device, user, time, "Low Oxygen Level", "A low oxygen level has been detected: " + str(average) + "\nEmission time: " + time.strftime("%d/%m/%Y %H:%M:%S"))

def warn_cardiacFrequency(values : list[float], time : dt.datetime, device : dv.Device, user : us.User):
    if(average := sum(values) / len(values)) < float(60): #Asumiendo estado de reposo y que el usuario es un adulto promedio
        return send_alert(device, user, time, "Low Cardiac Frequency", "A low cardiac frequency has been detected while resting: " + str(average) + "\nEmission time: " + time.strftime("%d/%m/%Y %H:%M:%S"))
    elif average > 100: #Asumiendo estado de reposo y que el usuario es un adulto promedio
        return send_alert(device, user, time, "High Cardiac Frequency", "A high cardiac frequency has been detected while resting: " + str(average) + "\nEmission time: " + time.strftime("%d/%m/%Y %H:%M:%S"))

def sort_biometrics(biometric : tuple) -> dt.datetime:
    return biometric[1]

def log_in(username : str, password : str):
    connection = db.Database()
    sql = "SELECT password FROM persona WHERE username = %s"
    concat = username + password
    logger = hsh.sha256(concat.encode()).hexdigest()
    result = connection(sql, username)
    try:
        if result[0][0] == logger:
            sql = "SELECT name, country, domicilio, fechaNacimiento FROM persona WHERE username = %s"
            user_params = connection(sql, username)[0]
            sql = "SELECT number FROM telefonos WHERE username = %s"
            phones = connection(sql, username)
            sql = "SELECT descripcion FROM antecedentes WHERE username = %s"
            events = connection(sql, username)
            sql = "SELECT mail FROM correos WHERE username = %s"
            emails = connection(sql, username)
            user = us.User(username, user_params[0], user_params[1], user_params[2],\
                            user_params[3].strftime("%Y"), user_params[3].strftime("%m"), user_params[3].strftime("%d"), password)
            for phone in phones:
                user.phones.append(phone[0])
            for event in events:
                user.events.append(event[0])
            for email in emails:
                user.emails.append(email[0])
            return user
    except:
        print("Either the username or the password is wrong. Please try again.")
        return False

def visualize(data : list[tuple[float, dt.datetime]], type : str, title : str):
    fig, ax = plt.subplots()
    information = []
    time = []
    for i in data:
        information.append(i[0])
        time.append(i[1].strftime("%d/%m/%Y - %H:%M:%S"))
    ax.plot(time, information)
    ax.set_xlabel("Time")
    ax.set_ylabel(type)
    ax.set_title(title)
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    return plt.show()
    
def main():
    #Loading
    if platform.system() == "Windows":
        subprocess.run(["cls"], shell=True)
    else:
        subprocess.run(["clear"], shell=True)
    has_logged_in = False
    database = db.Database()
    print("Welcome to the Biometric Bracelet Companion App!")
    while(True): #Main Loop
        command = input("What would you like to do?"
                        "\nEnter \"help\" for more information.\n")
        
        if command == "exit":
            if platform.system() == "Windows":
                subprocess.run(["cls"], shell=True)
            else:
                subprocess.run(["clear"], shell=True)
            return 0

        elif command == "log in" and not has_logged_in:
            username = input("Please provide your username: ")
            password = input("Please provide your password: ")
            if platform.system() == "Windows":
                subprocess.run(["cls"], shell=True)
            else:
                subprocess.run(["clear"], shell=True)
            user = log_in(username, password)
            if user != False:
                has_logged_in = True
                sql = "SELECT idDispositivo, modelo FROM dispositivo WHERE username = %s"
                device_params = database(sql, username)
                sql = "SELECT idSensor, modelo, tipoDato FROM sensor WHERE idDispositivo = %s"
                devices = []
                for device in device_params:
                    sensor_params = database(sql, device[0])
                    sensors = []
                    for sensor in sensor_params:
                        sensors.append((sensor[0], sensor[1], sensor[2]))
                    devices.append(dv.Device(device[0], device[1], *sensors))
                username = None
                password = None
                user_biometrics = {}
                user_biometrics["cardiacFrequency"] = []
                user_biometrics["oximetry"] = []
                user_biometrics["temperature"] = []
                user_biometrics["acceleration"] = []
                user_biometrics["rotation"] = []
                for device in devices:
                    biometrics = device.get_biometrics(user.username)
                    user_biometrics["cardiacFrequency"] += biometrics["cardiacFrequency"]
                    user_biometrics["oximetry"] += biometrics["oximetry"]
                    user_biometrics["temperature"] += biometrics["temperature"]
                    user_biometrics["acceleration"] += biometrics["acceleration"]
                    user_biometrics["rotation"] += biometrics["rotation"]
                user_biometrics["cardiacFrequency"].sort(key = sort_biometrics)
                user_biometrics["oximetry"].sort(key = sort_biometrics)
                user_biometrics["temperature"].sort(key = sort_biometrics)
                user_biometrics["acceleration"].sort(key = sort_biometrics)
                user_biometrics["rotation"].sort(key = sort_biometrics)
            
        elif command == "help":
            print("\"exit\": Leaves the Program")
            if not has_logged_in:
                print("\"log in\": Log in to the program\n"
                      "\"create account\": Create an account")
            else:
                print("\"log out\": Log out of the program\n"
                      "\"visualize\": Visualize a chart on a type of biometric\n"
                      "\"live data\": Visualize live data from your sensor\n"
                      "\"add device\": Link a device to your account\n"
                      "\"remove device\": Remove a device to your account")

        elif command == "log out" and has_logged_in:
            user = None
            devices = None
            sensors = None
            has_logged_in = False
            biometrics = None
            user_biometrics = None
            if platform.system() == "Windows":
                subprocess.run(["cls"], shell=True)
            else:
                subprocess.run(["clear"], shell=True)

        elif command == "create account" and not has_logged_in:
            username = input("Provide the username: ")
            name = input("Provide a name: ")
            country = input("Give your country's international short name: ")
            address = input("Provide your address: ")
            year = input("Provide your birth year: ")
            month = input("Provide your birth month: ")
            day = input("Provide your birth day: ")
            password = input("Provide your password: ")
            phones = []
            emails = []
            events = []
            devices = []
            role = False
            jobId = False
            contacts = []
            while True:
                definer = input("Would you like to add anything else? Type \"No\" to make the account\n"
                                "Type \"help\" to get information on what to add.\n")
                if definer == "No":
                    break
                elif definer == "help":
                    print("\"phone\": Add a phone number\n"
                          "\"email\": Add an email\n"
                          "\"data\": Add a description about you or add an existing condition\n"
                          "\"device\": Link your device\n"
                          "\"link\": Add a trusted contact\n"
                          "\"contact \": Add information to be able to become a trusted contact\n")
                elif definer == "phone":
                    phone = input("Please type your phone number: ")
                    phones.append(phone)
                elif definer == "email":
                    email = input("Please type your email: ")
                    emails.append(email)
                elif definer == "data":
                    data = input("Please type what you want others to keep in mind: ")
                    events.append(data)
                elif definer == "device":
                    deviceId = int(input("Please provide the identifier of your device.\n"
                                         "If it's associated with another account, please unregister it before registering for the new account.\n"))
                    devices.append(deviceId)
                elif definer == "contact" and not (role or jobId):
                    if role or jobId:
                        print("You have already given your role and job ID!")
                        continue
                    role = input("Please type your role: ")
                    jobId = input("Please type your jobId if neccesary.\n"
                                  "If not needed, type \"NULL\"\n")
                elif definer == "link":
                    other = input("Please type the username of the account you trust: ")
                    contacts.append(other)
                else:
                    print("Please type a valid command.")
            user = us.User(username, name, country, address, year, month, day, password, phones = phones, emails = emails, events = events)
            if user.add() == False:
                continue
            else:
                user.add_emails()
                user.add_events()
                user.add_phones()
                if role and jobId:
                    user.add_contact(role, jobId)
                for dvc in devices:
                    user.add_device(dvc)
                for contact in contacts:
                    user.link(contact)
                if platform.system() == "Windows":
                    subprocess.run(["cls"], shell=True)
                else:
                    subprocess.run(["clear"], shell=True)
                print("Account succesfully created! To log in, run the corresponding command.")

        elif command == "visualize" and has_logged_in:
            dataType = input("Which data type would you like to visualize?\n"
                             "Type \"help\" for information on what you can visualize.\n")
            if dataType == "help":
                print("\"temperature\", \"oximetry\", \"cardiacFrequency\"\nReturned to main menu.")
            elif dataType == "temperature" or dataType == "oximetry" or dataType == "cardiacFrequency":
                range_selector = input("Would you like to visualize from a range? Type \"yes\" if so and anything else if not.")
                if range_selector.lower() != "yes":
                    visualize(user_biometrics[dataType], dataType, "Registered " + dataType + " of " + user.name)
                    if platform.system() == "Windows":
                        subprocess.run(["cls"], shell=True)
                    else:
                        subprocess.run(["clear"], shell=True)
                else:
                    year = int(input("Please type the lower bound year: "))
                    month = int(input("Please type the lower bound month: "))
                    day = int(input("Please type the lower bound day: "))
                    hour = int(input("Please type the lower bound hour: "))
                    minute = int(input("Please type the lower bound minute: "))
                    second = int(input("Please type the lower bound second: "))
                    lower_bound = dt.datetime(year, month, day, hour, minute, second)
                    year = int(input("Please type the upper bound year: "))
                    month = int(input("Please type the upper bound month: "))
                    day = int(input("Please type the upper bound day: "))
                    hour = int(input("Please type the upper bound hour: "))
                    minute = int(input("Please type the upper bound minute: "))
                    second = int(input("Please type the upper bound second: "))
                    upper_bound = dt.datetime(year, month, day, hour, minute, second)
                    if dataType == "temperature":
                        sql = "SELECT temperatura, tiempoRegistro FROM temperatura NATURAL JOIN biometrico WHERE username = %s AND tiempoRegistro BETWEEN %s AND %s"
                        visualize(database(sql, user.username, lower_bound, upper_bound), dataType, "Registered " + dataType + " of " + user.name
                             + " between " + lower_bound.strftime("%d/%m/%Y %H:%M:%S") + " and " + upper_bound.strftime("%d/%m/%Y %H:%M:%S"))
                        if platform.system() == "Windows":
                            subprocess.run(["cls"], shell=True)
                        else:
                            subprocess.run(["clear"], shell=True)
                    elif dataType == "oximetry":
                        sql = "SELECT oximetria, tiempoRegistro FROM oximetria NATURAL JOIN biometrico WHERE username = %s AND tiempoRegistro BETWEEN %s AND %s"
                        visualize(database(sql, user.username, lower_bound, upper_bound), dataType, "Registered " + dataType + " of " + user.name
                             + " between " + lower_bound.strftime("%d/%m/%Y %H:%M:%S") + " and " + upper_bound.strftime("%d/%m/%Y %H:%M:%S"))
                        if platform.system() == "Windows":
                            subprocess.run(["cls"], shell=True)
                        else:
                            subprocess.run(["clear"], shell=True)
                    else:
                        sql = "SELECT frecuenciaCardiaca, tiempoRegistro FROM frecuenciascardiacas NATURAL JOIN biometrico WHERE username = %s AND tiempoRegistro BETWEEN %s AND %s"
                        visualize(database(sql, user.username, lower_bound, upper_bound), dataType, "Registered " + dataType + " of " + user.name
                             + " between " + lower_bound.strftime("%d/%m/%Y %H:%M:%S") + " and " + upper_bound.strftime("%d/%m/%Y %H:%M:%S"))
                        if platform.system() == "Windows":
                            subprocess.run(["cls"], shell=True)
                        else:
                            subprocess.run(["clear"], shell=True)
            else:
                print("Invalid data type. Returned to main menu.")

        elif command == "live data" and has_logged_in:
            if len(devices) == 0:
                print("Can't see data - you need a device!")
                continue
            print("Which device will you select?")
            for i in range(len(devices)):
                print(i)
            selection = int(input())
            for sensor in devices[selection].sensors:
                if sensor.type == "oxim-fc":
                    oxim_id = sensor.model + "-" + str(sensor.id)
                elif sensor.type == "temp":
                    temp_id = sensor.model + "-" + str(sensor.id)
                
            dataType = input("Which data type would you like to visualize?\n"
                             "Type \"help\" for information on what you can visualize.\n")
            if dataType == "help":
                print("\"temperature\", \"oximetry\", \"cardiacFrequency\"\nReturned to main menu.")
            elif dataType == "temperature":
                bk.livePlot("Time", "Temperature(C)", "reto/temperatura/" + str(temp_id), user.username, user.password,
                            "Temperatura registrada de " + user.name, warn_temperature, device = devices[0], user = user)
                if platform.system() == "Windows":
                    subprocess.run(["cls"], shell=True)
                else:
                    subprocess.run(["clear"], shell=True)
            elif dataType == "oximetry":
                bk.livePlot("Time", "Oximetry %", "reto/oximetria/" + str(oxim_id), user.username, user.password,
                            "Oximetría registrada de " + user.name, warn_oximetry, device = devices[0], user = user)
                if platform.system() == "Windows":
                    subprocess.run(["cls"], shell=True)
                else:
                    subprocess.run(["clear"], shell=True)
            elif dataType == "cardiacFrequency":
                bk.livePlot("Time", "Cardiac Frequency", "reto/frecuenciaCardiaca/" + str(oxim_id), user.username, user.password,
                            "Frecuencia Cardiaca registrada de " + user.name, warn_cardiacFrequency, device = devices[0], user = user)
                if platform.system() == "Windows":
                    subprocess.run(["cls"], shell=True)
                else:
                    subprocess.run(["clear"], shell=True)
            else:
                print("Invalid data type. Returned to main menu.")

        elif command == "add device" and has_logged_in:
            device_id = int(input("What's the device ID?\n"))
            model = input("What's your device model?\n")
            new_device = dv.Device(device_id, model)
            while True:
                sensor_adder = input("Would you like to add a sensor? Type\"yes\" to add, anything else to stop adding.\n")
                if sensor_adder.lower() == "yes":
                    sensor_id = int(input("What's the sensor id?"))
                    sensor_model = input("What's the sensor model?")
                    sensor_type = input("Please type the type of data your sensor gives as your manual indicates:")
                    new_device.add_sensor(sensor_id, sensor_model, sensor_type)
                else:
                    print("Current Sensors Added: ")
                    for sensor in new_device.sensors:
                        print(str(sensor.id) + "-" + sensor.model)
                    sensor_adder = input("Would you like to stop now or keep adding sensors? Type\"yes\" to stop.\n")
                    if sensor_adder.lower() == "yes":
                        user.add_device(new_device.id)
                        devices.append(new_device)
                        if platform.system() == "Windows":
                            subprocess.run(["cls"], shell=True)
                        else:
                            subprocess.run(["clear"], shell=True)
                        print("Device Added! You can now start using it.")
                        break

        elif command == "remove device":
            print("Current devices: ")
            for device in devices:
                print(device.id)
            try:
                old_device = int(input("Type the ID of the device you wish to remove, or type any non-numeric character to abort.\n"))
                user.remove_device(old_device)
                if platform.system() == "Windows":
                    subprocess.run(["cls"], shell=True)
                else:
                    subprocess.run(["clear"], shell=True)
                print("Device succesfully removed.")
            except:
                if platform.system() == "Windows":
                    subprocess.run(["cls"], shell=True)
                else:
                    subprocess.run(["clear"], shell=True)
                print("Aborted Deletion.")
        
        else:
            print("Please enter a valid command.\n")
            
if __name__ == "__main__":
    main()