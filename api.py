from flask import Flask, request
from flask_cors import CORS
from pymongo import MongoClient
from environment import config_aws as config

mongo_uri = config.MONGO_URI
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
        if len(data["schedules"]) > 0:
            collection.update_one(filter, {'$set': data})
        else:
            collection.delete_one(filter)
    else:
        collection.insert_one(data)
    return "received"


if __name__ == '__main__':
    app.run(debug=True, port=config.PORT, host=config.IP)
