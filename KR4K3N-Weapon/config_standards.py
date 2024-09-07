# Weapons Status
arm = 0
unarm = 1
fire = 2
reload = 3
waiting = 4

# Status
fail = 0
success = 1
error = 2

# Configurations
weapons_range = 200
total_rounds = 100
time_difference_between_reloads = 20

# Range Status
in_range = 1
off_range = 0

weapons_tag = 0
weapons_range_tag = 1

navigators_ip = "localhost"
navigators_port = "5000"

coordinates = []

def get_coordinates():
    return coordinates

def get_last_coordinate():
    return coordinates.pop()

def update_coordinates_list(data):
    global coordinates
    coordinates.append(data)

def set_coordinates(new_coordinates):
    global coordinates
    coordinates = new_coordinates

def get_weapons_range():
    return weapons_range

def get_total_rounds():
    return total_rounds

def get_fire_status():
    return fire

def get_arm_status():
    return arm

def get_unarm_status():
    return unarm

def get_reload_status():
    return reload

def get_waiting_status():
    return waiting

def get_time_difference():
    return time_difference_between_reloads
