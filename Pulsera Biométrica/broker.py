import paho.mqtt.client as paho
import datetime as dt
import matplotlib.pyplot as plt
import platform
import subprocess

def livePlot(xlabel: str, ylabel: str, topic: str, username: str, password: str, title: str, *args : function[list[float]], **fargs):
    plt.ion()
    y = [float(0) for i in range(20)]
    x = [float(0) for i in range(20)]
    fig = plt.plot(x, y)[0]
    plt.pause(1)

    def on_connect(client, userdata, flags, reason_code, properties):
        print("To stop the program, enter Control + C or equivalent in the terminal.")

    def subscribe(client: paho):

        def on_message(client, userdata, msg): 
            nonlocal fig
            nonlocal y
            nonlocal x
            nonlocal xlabel
            nonlocal ylabel
            nonlocal topic
            nonlocal title
            nonlocal args
            nonlocal fargs

            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            y.append(float(msg.payload.decode()))
            x.append(dt.datetime.now().strftime('%H:%M:%S'))
            fig.remove()
            plt.clf()
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.title(title)
            x = x[-20:]
            y = y[-20:]
            fig = plt.plot(x, y)[0]
            plt.xticks(rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.30)
            plt.pause(0.5)
            all_functional = True
            for data in y:
                if data == float(0):
                    all_functional = False
            if all_functional:
                for function in args:
                    function(y, dt.datetime.now(), **fargs)

        client.subscribe(topic)
        client.on_message = on_message

    client = paho.Client(paho.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.username_pw_set(username, password)
    client.connect('localhost', 1883)
    subscribe(client)
    while(True):
        try:
            client.loop_forever()
        except KeyboardInterrupt:
            client.disconnect()
            if platform.system() == "Windows":
                subprocess.run(["cls"], shell=True)
            else:
                subprocess.run(["clear"], shell=True)
            plt.ioff()
            plt.close()
            break

if __name__ == "__main__":
    livePlot("Tiempo", "Datos Recibidos", "reto/admin/#", "admin", "pass", "Testing")