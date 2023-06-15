import time
import paho.mqtt.client as mqtt
import requests
import signal
import sys
from pymongo import MongoClient
from environment import config_aws as config

# Configuración del cliente MQTT
username = config.MQTT_USERNAME
password = config.MQTT_PASSWORD
cli = mqtt.Client()
cli.username_pw_set(username, password)

url = "http://worldtimeapi.org/api/timezone/America/Bogota"

# Configuración MongoDB
mongo_uri = config.MONGO_URI
mClient = MongoClient(mongo_uri)

db = mClient['BE2']
collection = db['alimentador']


def get_hours(data):
    return str(data["datetime"][11:16])


def consume_api(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()


def get_time_now(data):
    return str(get_hours(data))


# El parametro schedule debe tener un formato HH:MM, y debe ser un formato de 24 horas
def is_time_to_feed(scheduleList):
    portionToFeed = 0
    for schedule in scheduleList:
        if (get_time_now(consume_api(url)) == schedule["time"]):
            portionToFeed = schedule["portion"]
            break
    return portionToFeed


# Este método se utiliza para consultar el horario que se tiene definido en el alimentador para "alimentar"
def get_schedule_from_feeder(serial):
    feeder = collection.find_one({"serial": serial})
    return feeder["schedule"]


# Este método valida si se requiere "alimentar" los alimentadores que se encuentren registrados en la bd
def validate_feeders(feederList):
    for feeder in feederList:
        portionToFeed = is_time_to_feed(feeder["schedules"])
        if portionToFeed > 0:
            topic = "feed/" + str(feeder["serial"])
            cli.publish(topic, str(portionToFeed))
            print("El alimentador con serial", feeder["serial"], " acaba de llenarse con", portionToFeed)
        else:
            print("Todavía hay alimento")

def disconnect(signal, frame):
    print("Desconectando del broker MQTT...")
    cli.loop_stop()  # Detener el bucle de eventos MQTT
    cli.disconnect()
    sys.exit(0)

# Asignar el manejador de señal para Ctrl+C
signal.signal(signal.SIGINT, disconnect)

# Función para manejar el evento de conexión
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conexión exitosa al broker MQTT")
    else:
        print("Error de conexión. Código de resultado: " + str(rc))

# Asignar la función de conexión
cli.on_connect = on_connect

# Conexión al broker MQTT
cli.connect("3.83.156.245", 18582)
cli.loop_start() # Iniciar el bucle de eventos MQTT

# Función para manejar el evento de pérdida de conexión
def on_disconnect(client, userdata, rc):
    print("Conexión perdida con el broker MQTT. Intentando reconexión...")
    while rc != 0:
        try:
            time.sleep(1)  # Esperar 1 segundo antes de intentar la reconexión
            rc = cli.reconnect()  # Intentar reconexión al broker MQTT
        except:
            continue

# Asignar la función de pérdida de conexión
cli.on_disconnect = on_disconnect

while True:
    data = consume_api(url)
    validate_feeders(collection.find())
    time.sleep(60)
