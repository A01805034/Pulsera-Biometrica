import database as db
import hashlib as hsh

class User:
    def __init__(self, username: str, name: str, country: str, address: str, year: int, month: int, day: int, password: str, **kwargs):
        self.username = username
        self.name = name
        self.country = country
        self.address = address
        self.birthday = str(year) + "/" + str(month) + "/" + str(day)
        string = username + password
        self.password = hsh.sha256(string.encode()).hexdigest()
        self.database = db.Database()
        self.phones = []
        self.emails = []
        self.events = []
        try:
            for phone in kwargs["phones"]:
                self.phones.append(phone)
        except KeyError:
            pass
        try:
            for email in kwargs["emails"]:
                self.emails.append(email)
        except KeyError:
            pass
        try:
            for event in kwargs["events"]:
                self.events.append(event)
        except KeyError:
            pass

    def add(self):
        try:
            sql = "INSERT INTO persona (username, name, country, domicilio, fechaNacimiento, password) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (self.username, self.name, self.country, self.address, self.birthday, self.password)
            return self.database(sql, *val)
        except:
            print("Error: Coudln't add this user! Try changing your username and try again.")
            return False

    def update(self):
        try:
            sql = "UPDATE persona SET name = %s, country = %s, domicilio = %s, fechaNacimiento = %s, password = %s WHERE username = %s"
            val = (self.name, self.country, self.address, self.birthday, self.password, self.username)
            return self.database(sql, *val)
        except:
            return print("Database Not Updated!")

    def link(self, other: str):
        if(self.username == other):
            return print("Error: Usernames can't be the same!")
        try:
            sql = "INSERT INTO usuariocontacto VALUES (%s, %s)"
            return self.database(sql, self.username, other)
        except:
            return print("Database Not Updated!")

    def add_phones(self):
        for data in self.phones:
            try:
                self.database("INSERT INTO telefonos VALUES(%s, %s)", self.username, data)
            except:
                return print("Database Not Updated!")

    def add_emails(self):
        for data in self.emails:
            try:
                self.database("INSERT INTO correos VALUES(%s, %s)", self.username, data)
            except:
                return print("Database Not Updated!")

    def add_events(self):
        for data in self.events:
            try:
                self.database("INSERT INTO antecedentes VALUES(%s, %s)", self.username, data)
            except:
                return print("Database Not Updated!")

    def change_credentials(self, new_username : str, new_password : str):
        try:
            sql = "UPDATE persona SET username = %s WHERE username = %s"
            var = (new_username, self.username)
            self.database(sql, *var)
        except:
            return print("Error: This Username Already Exists!")
        self.username = new_username
        string = self.username + new_password
        self.password = hsh.sha256(string.encode()).hexdigest()
        return self.database("UPDATE persona SET password = %s WHERE username = %s", self.password, self.username)

    def delete(self):
        try:
            return self.database("DELETE FROM persona WHERE username = %s", self.username)
        except:
            return print("Error: This entry doesn't exist!")

    def add_contact(self, role : str, id : str = None):
        try:
            sql = "INSERT INTO contacto VALUES (%s, %s, %s)"
            if id != None:
                val = (self.username, role, id)
            else:
                val = (self.username, role, "NULL")
            return self.database(sql, *val)
        except:
            return print("Database Not Updated!")

    def add_device(self, deviceId : int):
        try:
            return self.database("UPDATE dispositivo SET username = %s WHERE idDispositivo = %s AND username IS NULL", self.username, deviceId)
        except:
            return print("Database Not Updated!")

    def remove_device(self, deviceId : int):
        try:
            return self.database("UPDATE dispositivo SET username = NULL WHERE idDispositivo = %s AND username = %s", deviceId, self.username)
        except:
            return print("Database Not Updated!")

if __name__ == "__main__":

    import subprocess
    import platform

    username = input("Provide the username: ")
    name = input("Provide a name: ")
    country = input("Give your country's international short name: ")
    address = input("Provide your address: ")
    year = input("Provide your birth year: ")
    month = input("Provide your birth month: ")
    day = input("Provide your birth day: ")
    password = input("Provide your password: ")
    person = User(username, name, country, address, year, month, day, password)
    if platform.system() == "Windows":
        subprocess.run(["cls"], shell=True)
    else:
        subprocess.run(["clear"], shell=True)
    person.add()
    person.add_device(0)
    person.add_contact("Software Developer", "A01805034")