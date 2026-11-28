import mysql.connector

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="reto_iot"
            )
        self.iterator = self.connection.cursor()

    def __call__(self, query : str, *args):
        if len(args) == 0:
            self.iterator.execute(query)
            try:
                self.connection.commit()
            except:
                pass
            result = self.iterator.fetchall()
        else:
            self.iterator.execute(query, args)
            try:
                self.connection.commit()
            except:
                pass
            result = self.iterator.fetchall()
        return result

    def modify(self):
        query = input("Please type the SQL input: ")
        values = int(input("How much arguements do you want?"))
        if values == 0:
            return self(query)
        val = []
        for i in range(values):
            data = input("Please insert data #" + str(i))
            val.append(data)
        val = tuple(data)
        return self(query, *val)

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":
    test = Database()
    query = "SHOW TABLES"
    result = test(query)
    for table in result:
        print(table)

    # myresult = mycursor.fetchall() / fetchone()
    # % = wildcard
    # %s = Escape Query Values