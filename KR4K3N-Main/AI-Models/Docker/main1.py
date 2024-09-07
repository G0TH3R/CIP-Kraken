from fastapi import FastAPI, Body,HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import ast
import numpy as np
import joblib

app = FastAPI()

prediction ={}
heading_model_path = 'nav_ai_heading_waypoint.pkl'
with open(heading_model_path, 'rb') as model_file:
    nav_ai_heading_model = joblib.load(model_file)
    
import ast
import numpy as np

def calculate_distance(ship_x, ship_y, radar_objects):
    distances = []
    
    for radar_point in radar_objects:
        if len(radar_point) == 2:
            x, y = radar_point
            distance = np.sqrt((ship_x - x) ** 2 + (ship_y - y) ** 2)
            distances.append(distance)
    
    # Fill with zeros if less than 4 radar points
    #while len(distances) < 4:
    #    distances.append(0)
    
    # Take only the first 4 distances
    distances = distances[:4]
    
    return distances
    
def preprocessing_heading(data):
    # Assuming 'data' is a dictionary
    #waypoints = ast.literal_eval(data['World.PrimaryBattleship.Navigation.waypoints'])
    #distances = calculate_distance(data['World.PrimaryBattleship.x'], data['World.PrimaryBattleship.y'], waypoints)
    distances = data["World.PrimaryBattleship.Navigation.waypoints"]
    data['distance_to_point_1'] = distances[0] if distances else 0
    data['distance_to_point_2'] = distances[1] if len(distances) > 1 else 0
    data['distance_to_point_3'] = distances[2] if len(distances) > 2 else 0
    data['distance_to_point_4'] = distances[3] if len(distances) > 3 else 0

    radar_objects = ast.literal_eval(data['World.PrimaryBattleship.RadarSonar.radar_objects'])
    distanced = calculate_distance(data['World.PrimaryBattleship.x'], data['World.PrimaryBattleship.y'], radar_objects)
    data['distance_to_radar_obj_1'] = distanced[0] if distanced else 0
    data['distance_to_radar_obj_2'] = distanced[1] if len(distanced) > 1 else 0
    data['distance_to_radar_obj_3'] = distanced[2] if len(distanced) > 2 else 0
    data['distance_to_radar_obj_4'] = distanced[3] if len(distanced) > 3 else 0
    
    # Optionally, you can uncomment the following lines if needed
    data['direction_port'] = int(data['World.PrimaryBattleship.chosen_direction'] == 'port')
    data['direction_starboard'] = int(data['World.PrimaryBattleship.chosen_direction'] == 'starboard')
    data['World.PrimaryBattleship.RadarSonar.collision_warning'] = int(data['World.PrimaryBattleship.RadarSonar.collision_warning'])
    data['World.PrimaryBattleship.RadarSonar.collision_event'] = int(data['World.PrimaryBattleship.RadarSonar.collision_event'])
    data['World.PrimaryBattleship.out_of_bounds'] = int(data['World.PrimaryBattleship.out_of_bounds'])

    # Optionally, drop unnecessary keys
    keys_to_drop = ['World.PrimaryBattleship.Engine.desired_speed','World.PrimaryBattleship.chosen_direction','World.PrimaryBattleship.Navigation.waypoints', 'World.PrimaryBattleship.RadarSonar.radar_objects', 'World.PrimaryBattleship.current_speed']
    for key in keys_to_drop:
        data.pop(key, None)

    return data

@app.post('/make_prediction_input', response_model=dict)
async def make_prediction_input(data: dict = Body(...)):
    try:
        result = await make_prediction(data)
        return result
    except Exception as e:
        error_message = str(e)
        status_code = 500  # Internal Server Error
        if isinstance(e, HTTPException):
            # If it's an HTTPException, use the status code and detail provided by the exception
            status_code = e.status_code
            error_message = e.detail

        # Log the error message for debugging purposes
        print(f"Error: {error_message}")

        # Return a detailed error response
        return JSONResponse(content={"error": error_message}, status_code=status_code)

async def make_prediction(data: dict):
    print("Received data:", data)
    post_request_store = {
        "World.PrimaryBattleship.x": data['x'],
        "World.PrimaryBattleship.y": data['y'],
        "World.PrimaryBattleship.heading": data['heading'],
        "World.PrimaryBattleship.option_port": data['option_port'],
        "World.PrimaryBattleship.option_starboard": data['option_starboard'],
        "World.PrimaryBattleship.chosen_direction": data['chosen_direction'],
        "World.PrimaryBattleship.out_of_bounds": data['out_of_bounds'],
        "World.PrimaryBattleship.Navigation.waypoints": data['Navigation.waypoint_distances'],
        "World.PrimaryBattleship.RadarSonar.collision_warning": data['RadarSonar.collision_warning'],
        "World.PrimaryBattleship.RadarSonar.collision_event": data['RadarSonar.collision_event'],
        "World.PrimaryBattleship.RadarSonar.radar_objects": "[]",
        "World.PrimaryBattleship.current_speed": data['current_speed'],
        "World.PrimaryBattleship.Engine.desired_speed": 5,
        "Security AI": 1
    }
    #record_df = pd.DataFrame([post_request_store])
    if post_request_store['Security AI'] == 3:
       speed_prediction = 0
    else:
       speed_prediction = 5

    X = preprocessing_heading(post_request_store)
    X_df = pd.DataFrame([X])
    print(X_df.columns)
    heading_prediction = nav_ai_heading_model.predict(X_df)

# Optionally, convert the predictions to the desired format if needed
    heading_prediction = heading_prediction.item() if hasattr(heading_prediction, 'item') else heading_prediction
    speed_prediction = speed_prediction.item() if hasattr(speed_prediction, 'item') else speed_prediction
    print("heading prediction:{} speed_prediction:{}".format(heading_prediction,speed_prediction))
    return {"heading": heading_prediction, "speed": speed_prediction}


