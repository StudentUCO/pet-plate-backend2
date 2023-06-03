from flask import Flask, request
from flask_cors import CORS
from pymongo import MongoClient

mongo_uri = 'mongodb://IOTUCO:LifeIsIoT@35.169.9.170:27017/?authMechanism=DEFAULT'
mClient = MongoClient(mongo_uri)

db = mClient['BE2']
collection = db['alimentador']

app = Flask(__name__)
CORS(app, origins='*')


@app.route('/alimentadores', methods=['POST'])
def add_feeders():
    data = request.json
    print(data)
    filter = {"serial": data["serial"]}
    feeder = collection.find_one(filter)
    if feeder:
        collection.update_one(filter, {'$set': data})
    else:
        collection.insert_one(data)
    return "received"


if __name__ == '__main__':
    app.run(debug=True, port=4000, host='localhost')
