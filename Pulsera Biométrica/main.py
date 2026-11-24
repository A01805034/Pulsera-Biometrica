import user as us
import device as dv
import database as db
import hashlib as hsh
import platform
import subprocess
import matplotlib.pyplot as plt
import datetime as dt
import broker as bk

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
    if platform.system() == "Windows":
        subprocess.run(["cls"], shell=True)
    else:
        subprocess.run(["clear"], shell=True)
    has_logged_in = False
    database = db.Database()
    print("Welcome to the Biometric Bracelet Companion App!")
    while(True):
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
                      "\"visualize\": Visualize a chart on a type of biometric\n" \
                      "\"live data\": Visualize the live data from your sensor\n")

        elif command == "log out" and has_logged_in:
            user = None
            devices = None
            sensors = None
            has_logged_in = False
            biometrics = None
            user_biometrics = None

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
                print("Account succesfully created! To log in, run the corresponding command.")

        elif command == "visualize" and has_logged_in:
            dataType = input("Which data type would you like to visualize?\n"
                             "Type \"help\" for information on what you can visualize.\n")
            if dataType == "help":
                print("\"temperature\", \"oximetry\", \"cardiacFrequency\"\nReturned to main menu.")
            elif dataType == "temperature" or dataType == "oximetry" or dataType == "cardiacFrequency":
                visualize(user_biometrics[dataType], dataType, "Registered " + dataType + " of " + user.name)
            else:
                print("Invalid data type. Returned to main menu.")

        elif command == "live data" and has_logged_in:
            if len(devices) > 1:
                print("Which device will you select?")
                for i in range(len(devices)):
                    print(i)
                selection = int(input())
                for sensor in devices[selection]:
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
                            "Temperatura registrada de " + user.name)
            elif dataType == "oximetry":
                bk.livePlot("Time", "Oximetry %", "reto/oximetria/" + str(oxim_id), user.username, user.password,
                            "Oximetría registrada de " + user.name)
            elif dataType == "cardiacFrequency":
                bk.livePlot("Time", "Cardiac Frequency", "reto/frecuenciaCardiaca/" + str(oxim_id), user.username, user.password,
                            "Frecuencia Cardiaca registrada de " + user.name)
            else:
                print("Invalid data type. Returned to main menu.")
        
        else:
            print("Please enter a valid command.\n")
            
if __name__ == "__main__":
    main()