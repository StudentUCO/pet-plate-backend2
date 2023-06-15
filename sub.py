import datetime

import paho.mqtt.client as mqtt
import requests
import json
from pymongo import MongoClient
from environment import config_dev as config

url_chat_bot = "http://" + config.CHATBOT_IP + ":" + str(config.CHATBOT_PORT)
url_be_1 = "http://" + config.BACKEND1_IP + ":" + str(config.BACKEND1_PORT) + "/api/user/public/get-by-feeder/"
mongo_uri = config.MONGO_URI
client = mqtt.Client()
username = config.MQTT_USERNAME
password = config.MQTT_PASSWORD

# Crear el objeto de cliente MQTT y especificar las credenciales
# client = mqtt.Client(client_id="tu_id_de_cliente")
client.username_pw_set(username=username, password=password)

client.connect(config.MQTT_IP, config.MQTT_PORT)
monClient = MongoClient(mongo_uri)
db = monClient["BE2"]
collection = db["comunicaciones"]


def on_connect(client, userdata, flags, rc):
    print("Se conectó con mqtt: " + str(rc))
    client.subscribe("alarm")
    client.subscribe("status/#")


def clean_payload(payld):
    payld = payld[2:len(payld) - 1]
    return payld


def str_to_json(message):
    return message.replace("'", '"')


def on_message(client, userdata, msg):
    try:
        # Se guardan el payload y el topic del mensaje en las variables payload y topic
        payload = clean_payload(str(msg.payload))
        topic = str(msg.topic)

        # Se guarda una versión inicial del json que se guardará dentro de la bd pero con comillas simples
        bd_data = str(
            {"topic": topic, "mensaje": payload, "datetime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

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
                    response = requests.post(url_chat_bot + "/send_alarm", json=json.loads(data[1]))
                    print(json.loads(data[1]))
                    print(response)
            elif response2.status_code == 403:
                print("plop")
        elif "status" in topic:
            print(str(msg.payload))
            if payload == 'RECEIVED':
                print(topic, payload)
            else:
                response2 = requests.get(url_be_1 + topic.split('/')[1])
                print(response2.json)
                if response2.status_code == 200:
                    data = str(response2.content).split("'")
                    if data[1] != "":
                        json_object = json.loads(str_to_json(data[1]))
                        json_object['status'] = payload.split(':')[0]
                        json_object['portion'] = payload.split(':')[1]
                        print(json_object)

                        response = requests.post(url_chat_bot + "/send_status", json=json_object)
                        print(response)
                elif response2.status_code == 403:
                    print("plop")
    except Exception as e:
        # Manejo de la excepción genérica
        print("Error:", str(e))


client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()
