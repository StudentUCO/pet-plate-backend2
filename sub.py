import paho.mqtt.client as mqtt
import requests
import json
from pymongo import MongoClient

url_chat_bot = "http://35.169.9.170:3030/send_alarm"
url_be_1 = "http://35.169.9.170:8080/api/user/public/get-by-feeder/"
mongo_uri = 'mongodb://IOTUCO:LifeIsIoT@35.169.9.170:27017/?authMechanism=DEFAULT'
client = mqtt.Client()
username = "argfonaa"
password = "1Ec9pVVoAPpK"

# Crear el objeto de cliente MQTT y especificar las credenciales
# client = mqtt.Client(client_id="tu_id_de_cliente")
client.username_pw_set(username=username, password=password)

client.connect("3.83.156.245", 18582)
monClient = MongoClient(mongo_uri)
db = monClient["BE2"]
collection = db["comunicaciones"]


def on_connect(client, userdata, flags, rc):
    print("Se conectó con mqtt: " + str(rc))
    client.subscribe("alarm")
    client.subscribe("weight")


def clean_payload(payld):
    payld = payld[2:len(payld) - 1]
    return payld


def str_to_json(message):
    return message.replace("'", '"')


def on_message(client, userdata, msg):
    # Se guardan el payload y el topic del mensaje en las variables payload y topic
    payload = clean_payload(str(msg.payload))
    topic = str(msg.topic)

    # Se guarda una versión inicial del json que se guardará dentro de la bd pero con comillas simples
    bd_data = str({"topic": topic, "mensaje": payload})

    # Se utiliza el metodo str_to_json para reemplazar las comillas simples por comillas dobles
    # Esto con el fin de que el json tenga el formato correcto
    bd_data = (str_to_json(bd_data))
    print(bd_data)
    print("serialBackend2 ", "va a ejecutar collection")
    collection.insert_one(json.loads(bd_data))
    print("serialBackend2 ", "Ejecuto collection")
    if msg.topic == "alarm":
        print("serialBackend2 ", "Entro a alarma")
        # client.publish("feed","5 kg")
        response2 = requests.get(url_be_1 + payload)
        print(url_be_1 + payload)
        print(response2.json)
        if response2.status_code == 200:
            data = str(response2.content).split("'")
            if data[1] != "":
                print(data[1])
                response = requests.post(url_chat_bot, json=json.loads(data[1]))
                print(json.loads(data[1]))
                print(response)
        elif response2.status_code == 403:
            print("plop")
    elif msg.topic == "weight":
        print("serialBackend2 ", "Entro a weight")
        print("Actualmente hay esta cantidad en el alimentador: " + str(msg.payload))


client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
