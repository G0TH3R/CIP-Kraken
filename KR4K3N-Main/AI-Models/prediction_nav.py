import pickle
import pandas as pd
import ast
import math
import json
import numpy as np
from sklearn.tree import DecisionTreeRegressor

post_request_store = {
  "World.PrimaryBattleship.x": 2200,
  "World.PrimaryBattleship.y": 1200,
  "World.PrimaryBattleship.chosen_heading": 0.164772309,
  "World.PrimaryBattleship.desired_heading":165.8797722,
  "World.PrimaryBattleship.option_port": 360,
  "World.PrimaryBattleship.option_starboard": 0,
  "World.PrimaryBattleship.chosen_direction": 'starboard',
  "World.PrimaryBattleship.out_of_bounds": False,
  "World.PrimaryBattleship.Navigation.waypoints": "[[3200, 1200], [2400, 1400], [2100, 1600], [2150, 1150]]",
  "World.PrimaryBattleship.RadarSonar.collision_warning": False,
  "World.PrimaryBattleship.RadarSonar.collision_event": False,
  "World.PrimaryBattleship.RadarSonar.radar_objects": "[]",
  "World.PrimaryBattleship.current_speed": 3,
  "World.PrimaryBattleship.Engine.desired_speed": 5,
  "Security AI": 1
}

prediction ={}


def calculate_distance(ship_x, ship_y, radar_objects):
    distances = []
    for radar_point in radar_objects:
        if len(radar_point) > 0:
            distances.extend([np.sqrt((ship_x - x)**2 + (ship_y - y)**2) for x, y in radar_point])
    return distances[:4]

def preprocessing_heading(df_new):
    df_new['World.PrimaryBattleship.Navigation.waypoints'] = df_new['World.PrimaryBattleship.Navigation.waypoints'].apply(ast.literal_eval)
    distances = calculate_distance(df_new['World.PrimaryBattleship.x'], df_new['World.PrimaryBattleship.y'], df_new['World.PrimaryBattleship.Navigation.waypoints'])
    distance_columns = ['distance_to_point_1', 'distance_to_point_2', 'distance_to_point_3', 'distance_to_point_4']
    df_new[distance_columns] = pd.DataFrame([distances]).fillna(0).values

    df_new['World.PrimaryBattleship.RadarSonar.radar_objects'] = df_new['World.PrimaryBattleship.RadarSonar.radar_objects'].apply(ast.literal_eval)
    distanced = calculate_distance(df_new['World.PrimaryBattleship.x'], df_new['World.PrimaryBattleship.y'], df_new['World.PrimaryBattleship.RadarSonar.radar_objects'])
    distance_columns = ['distance_to_radar_obj_1', 'distance_to_radar_obj_2', 'distance_to_radar_obj_3', 'distance_to_radar_obj_4']
    df_new[distance_columns] = pd.DataFrame([distances]).fillna(0).values

    df_new['direction_port'] = (df_new['World.PrimaryBattleship.chosen_direction'] == 'port').astype(int)
    df_new['direction_starboard'] = (df_new['World.PrimaryBattleship.chosen_direction'] == 'starboard').astype(int)
    df_new['World.PrimaryBattleship.RadarSonar.collision_warning'] = df_new['World.PrimaryBattleship.RadarSonar.collision_warning'].astype(int)
    df_new['World.PrimaryBattleship.RadarSonar.collision_event'] = df_new['World.PrimaryBattleship.RadarSonar.collision_event'].astype(int)
    df_new['World.PrimaryBattleship.out_of_bounds'] = df_new['World.PrimaryBattleship.out_of_bounds'].astype(int)

    y1 = df_new['World.PrimaryBattleship.chosen_heading']
    y2 = df_new['World.PrimaryBattleship.current_speed']

    columns_to_drop = ['World.PrimaryBattleship.chosen_heading','World.PrimaryBattleship.chosen_direction', 'World.PrimaryBattleship.Navigation.waypoints','World.PrimaryBattleship.RadarSonar.radar_objects','World.PrimaryBattleship.current_speed']
    df_new = df_new.drop(columns=columns_to_drop)
    return df_new, y1, y2


heading_model_path = 'nav_ai_heading.pkl'
speed_model_path = 'nav_ai_speed.pkl'
with open(heading_model_path, 'rb') as model_file:
        nav_ai_heading_model = pickle.load(model_file)

with open(speed_model_path, 'rb') as model_file:
        nav_ai_speed_model = pickle.load(model_file)

record_df = pd.DataFrame([post_request_store])
X,y1,y2 = preprocessing_heading(record_df)

prediction['heading'] = nav_ai_heading_model.predict(X)
prediction['speed'] = nav_ai_speed_model.predict(X)

print (prediction)




