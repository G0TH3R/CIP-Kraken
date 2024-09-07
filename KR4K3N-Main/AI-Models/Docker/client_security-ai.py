from pathlib import Path
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
import os
import numpy as np
import zmq
import json
import threading
from icecream import ic
import logging
import joblib
import pandas as pd

BASE_DIR = Path(__file__).resolve(strict=True).parent

ic.configureOutput(includeContext=True, contextAbsPath=True)

app = FastAPI()
logger = logging.getLogger(__name__)
shared_data = {}  # Shared data storage
prediction = {}  # Store predictions
post_request_store = {}  # Store data from POST requests
keys_to_extract = []  # Global variable to store keys

message_mapping = {
    "In Range": "msg_ In Range",
    "Missile Missed": "msg_ Missile Missed",
    "Missile Reloaded successfully": "msg_ Missile Reloaded successfully",
    "Missile armed successfully": "msg_ Missile armed successfully",
    "Missile fired successfully": "msg_ Missile fired successfully",
    "Missile is not Loaded": "msg_ Missile is not Loaded",
    "Missile unarmed successfully": "msg_ Missile unarmed successfully",
    "No Coordinate data": "msg_ No Coordinate data",
    "No More Rounds Remaining": "msg_ No More Rounds Remaining",
    "Out of Range": "msg_ Out of Range",
    "Please wait sometime before reloading": "msg_ Please wait sometime before reloading",
    "In Arming Range": "msg_ In Arming Range",
    "In Ready Range": "msg_ In Ready Range"
}

message_mapping_value = {
    "msg_ In Range": 0,
    "msg_ Missile Missed": 0,
    "msg_ Missile Reloaded successfully": 0,
    "msg_ Missile armed successfully": 0,
    "msg_ Missile fired successfully": 0,
    "msg_ Missile is not Loaded": 0,
    "msg_ Missile unarmed successfully": 0,
    "msg_ No Coordinate data": 0,
    "msg_ No More Rounds Remaining": 0,
    "msg_ Out of Range": 0,
    "msg_ Please wait sometime before reloading": 0,
    "msg_ In Arming Range": 0,
    "msg_ In Ready Range": 0
}

def encoding_msg(msg):
    result_dict = {key: 0 for key in message_mapping_value}
    print(result_dict)

    if msg in message_mapping:
        result_dict[message_mapping[msg]] = 1
    else:
        raise ValueError(f"Unknown message: {msg}")
    return result_dict

def make_prediction(data):
    # print(data)
    data.update(encoding_msg(data.get("Msg")))
    data.pop("Msg", None)
    # print(data)
    data_new = np.array(list(data.values())).reshape(1, -1).astype(int)
    features = np.array(list(data.keys())).ravel()
    dataframe = pd.DataFrame(data=data_new, columns=features)

    model = joblib.load(Path(BASE_DIR).joinpath(f"..\security_ai.pkl"))
    result = model.predict(dataframe)
    # print(result)
    return {"Prediction": result.tolist()}

def load_keys_to_extract():
    global keys_to_extract
    try:
        with open('keys_to_extract.txt', 'r') as file:
            keys_to_extract = [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        print("File 'keys_to_extract.txt' not found.")
    except Exception as e:
        print(f"Error while reading 'keys_to_extract.txt': {e}")

def store_prediction(data):
    for key in keys_to_extract:
        if key in data:
            prediction_key = key.replace('World.PrimaryBattleship.', 'prediction_')
            prediction[prediction_key] = data[key]

def zmq_subscriber():
    zmq_server = os.environ.get('zmq-server', 'localhost')
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(f"tcp://{zmq_server}:5556")
    socket.setsockopt_string(zmq.SUBSCRIBE, '')

    while True:
        message = socket.recv_string()
        try:
            data = json.loads(message)
            store_prediction(data)
            for key in keys_to_extract:
                value = data.get(key)
                if value is not None:
                    shared_data[key] = value
        except json.JSONDecodeError:
            print(f"Received invalid JSON: {message}")


#   INPUT DATA FORMAT
# {
#     "Power Required (Watts)": 60835120.3,
#     "Level": 266,
#     "Weapon Range Status": 1,
#     "Weapons Status": 0,
#     "Msg": "No Coordinate data"
# }
# async def post_prediction():
#     app.post(url)
@app.post('/make_prediction_input')
def make_prediction_input(data: dict = Body(...)):
    try:
        return make_prediction(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post('/store_post_data')
def store_post_data(data: dict = Body(...)):
    key = data.get('key')
    if key:
        post_request_store[key] = data.get('value')
        return {"status": "Data stored"}
    else:
        raise HTTPException(status_code=400, detail="No key provided")

@app.get('/get_post_data')
def get_post_data(key: str or None):
    if key and key in post_request_store:
        return {key: post_request_store[key]}
    else:
        raise HTTPException(status_code=404, detail="Key not found")

@app.get('/get_prediction')
def get_prediction():
    return prediction

def start_fastapi_app():
    threading.Thread(target=zmq_subscriber, daemon=True).start()
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=6010)

if __name__ == "__main__":
    load_keys_to_extract()
    start_fastapi_app()
