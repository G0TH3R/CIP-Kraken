from flask import Flask, render_template, request, jsonify
import math
import threading

import config_standards as cst
import utils
import logging
import logger as log
import zmq
import json

app = Flask(__name__)
datalogger = logging.getLogger(__name__)
datalogger.addHandler(log.get_filehandler())

# Initial missile state (unarmed by default)
missile_color = '#00FF00'  # Green color for unarmed missile
missile_status = cst.unarm  # Unarm Default
missile_fire_time = utils.get_current_time()
required_time_difference = cst.get_time_difference()
total_rounds = cst.get_total_rounds()
fired_rounds = 0
max_range = cst.get_weapons_range()
in_range = False

@app.route('/')
def index():
    return render_template('index.html')

# API route to arm the missile
@app.route('/arm', methods=['POST'])
def arm_missile():
    datalogger.debug("/arm info: {}".format(request))
    if checkNumberOfRemainingRounds():
        global missile_color
        missile_color = '#FF0000'  # Red color for armed missile
        global missile_status
        missile_status = cst.arm
        message = '{},{},Missile armed successfully'.format(cst.weapons_tag, cst.get_arm_status())
        datalogger.warning(message)
        utils.send_alert_to_security_api(message)
        return jsonify({'message': 'Missile armed successfully','status':'Armed'})
    else:
        message = '{},{},No More Rounds Remaining'.format(cst.weapons_tag, cst.get_arm_status())
        datalogger.warning(message)
        utils.send_alert_to_security_api(message)
        return jsonify({'message': 'No More Rounds Remaining','status':'Error'})

# API route to unarm the missile
@app.route('/unarm', methods=['POST'])
def unarm_missile():
    datalogger.debug("/unarm info: {}".format(request))
    global missile_color
    missile_color = '#00FF00'  # Green color for unarmed missile
    global missile_status
    missile_status = cst.unarm
    message = '{},{},Missile unarmed successfully'.format(cst.weapons_tag, cst.get_unarm_status())
    datalogger.warning(message)
    utils.send_alert_to_security_api(message)
    return jsonify({'message': 'Missile unarmed successfully','status':'Unarmed'})

# API route to fire the missile
@app.route('/fire', methods=['POST'])
def fire_missile():
    # datalogger.debug("/fire info: {}".format(request))
    message = ""
    global missile_status
    if checkNumberOfRemainingRounds():
        if missile_status == cst.arm:
            global missile_color
            missile_color = '#000000'  # Green color for unarmed missile
            missile_status = cst.fire
            global missile_fire_time
            missile_fire_time = utils.get_current_time()
            global fired_rounds
            fired_rounds = fired_rounds + 1
            global in_range
            if in_range:
                message = '{},{},Missile fired successfully'.format(cst.weapons_tag, cst.get_fire_status())
                datalogger.warning(message)
                utils.send_alert_to_security_api(message)
                return jsonify({'message': 'Missile fired successfully','status':'fired'})
            else:
                message = '{},{},Missile Missed'.format(cst.weapons_tag, cst.get_fire_status())
                datalogger.warning(message)
                utils.send_alert_to_security_api(message)
                return jsonify({'message': 'Missile Missile Missed','status':'fail'})
        else:
            message = '{},{},Missile is not Loaded'.format(cst.weapons_tag, cst.get_fire_status())
            datalogger.warning(message)
            utils.send_alert_to_security_api(message)
            return jsonify({'message': 'Missile is not Loaded','status':'Error'})
    else:
        message = '{},{},Missile is not Loaded'.format(cst.weapons_tag, cst.get_fire_status())
        datalogger.warning(message)
        utils.send_alert_to_security_api(message)
        return jsonify({'message': 'No More Rounds Remaining','status':'Error'})

# API route to reload the missile
@app.route('/reload', methods=['POST'])
def reload_missile():
    datalogger.debug("/reload info: {}".format(request))
    message = ''
    if checkNumberOfRemainingRounds():
        if checkTimeElapsed():
            global missile_color
            missile_color = '#FF0000'  # Green color for unarmed missile
            global missile_status
            missile_status = cst.ready
            message = '{},{},Missile Ready to Arm'.format(cst.weapons_tag, cst.ready)
            datalogger.warning(message)
            utils.send_alert_to_security_api(message)
            return jsonify({'message': 'Missile Reloaded successfully','status':'Reloaded'})
        else:
            message = '{},{},Please wait sometime before reloading'.format(cst.weapons_tag, cst.get_reload_status())
            datalogger.warning(message)
            utils.send_alert_to_security_api(message)
            return jsonify({'message': 'Please wait sometime before reloading','status':'Error'})
    else:
        message = '{},{},No More Rounds Remaining'.format(cst.weapons_tag, cst.get_reload_status())
        datalogger.warning(message)
        utils.send_alert_to_security_api(message)
        return jsonify({'message': 'No More Rounds Remaining','status':'Error'})

def checkTimeElapsed():
    current_time = utils.get_current_time()
    global missile_fire_time
    global required_time_difference
    time_difference = current_time - missile_fire_time
    if time_difference.total_seconds() > required_time_difference:
        return True
    else:
        return False

def checkNumberOfRemainingRounds():
    global fired_rounds
    global total_rounds
    if total_rounds <= fired_rounds:
        return False
    else:
        return True

@app.route('/getData', methods=['POST'])
def get_data():
    try:
        datalogger.info("/getData info: {}".format(request))
        cst.update_coordinates_list(request.form)
        return jsonify({'success': True})
    except Exception as e:
        datalogger.error(f"Error in /getData: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

def checkIfTargetInRange():
    try:
        if len(cst.get_coordinates()) > 0:
            data = cst.get_last_coordinate()
            print("data:" + str(data))
            shipX = float(data.get('shipX'))
            shipY = float(data.get('shipY'))
            targetX = float(data.get('targetX'))
            targetY = float(data.get('targetY'))
            distance = math.sqrt((shipX - targetX)**2 + (shipY - targetY)**2)
            global in_range
            global missile_status
            print("dist: " + str(distance))
            if cst.weapon_fire_range > distance:
                in_range = True
                fire_missile()
                # datalogger.warning('{} | {} | {} | Fired'.format(cst.weapons_range_tag, cst.in_range, cst.success))
                return True
            if cst.weapon_arming_range > distance:
                in_range = True
                missile_status = cst.arm  #Arm status
                message = '{},{},In Arming Range'.format(cst.weapons_range_tag, cst.arm)
                datalogger.warning(message)
                utils.send_alert_to_security_api(message)
                return True
            if cst.get_weapons_range() < distance:
                in_range = False
                missile_status = cst.unarm  #Unarm status
                message = '{},{},Out of Range'.format(cst.weapons_range_tag, cst.get_unarm_status())
                datalogger.warning(message)
                utils.send_alert_to_security_api(message)
                return  False
            else:
                in_range = True
                missile_status = cst.ready  #Ready status
                message = '{},{},In Ready Range'.format(cst.weapons_range_tag, cst.ready)
                datalogger.warning(message)
                utils.send_alert_to_security_api(message)
                return True
        else:
            message = '{},{},No Coordinate data'.format(cst.weapons_range_tag, cst.fail)
            datalogger.warning(message)
            utils.send_alert_to_security_api(message)
            return 'NA'
    except Exception as e:
        datalogger.error(e)

@app.route('/get_missile_color', methods=['GET'])
def get_missile_color():
    global missile_color
    global missile_status
    global total_rounds
    global fired_rounds
    status = {
        0:'ARMED', 1:'UNARMED', 2:'FIRED', 3:'RELOADING', 4:'WAITING', 5:'READY'
    }
    return jsonify({'color': missile_color, 'status': status.get(missile_status), 'rounds': total_rounds-fired_rounds, 'range_status': checkIfTargetInRange()})

def zmq_client():
    socket = None
    context = None
    try:
        # Create a ZeroMQ context
        context = zmq.Context()

        # Create a REQ (request) socket
        socket = context.socket(zmq.SUB)

        # Connect to the server
        server_address = "tcp://{}:{}".format(cst.navigators_ip, cst.navigators_port)  # Replace with the actual server address
        socket.connect(server_address)
        datalogger.warning("Connecting to the server:" + server_address)

        # Subscribe to all messages
        socket.setsockopt_string(zmq.SUBSCRIBE, '')
        keys_to_extract = {
            "World.PrimaryBattleship.x" : 'shipX',
            "World.PrimaryBattleship.y": 'shipY',
            "World.PrimaryBattleship.Weapons.targets": 'target'
            # "World.AircraftCarrier.y": 'targetY'
        }

        while True:
            message = socket.recv_string()
            try:
                data = json.loads(message)
                info = {}
                for key in keys_to_extract.keys():
                    value = data.get(key)
                    if value is not None:
                        if key == "World.PrimaryBattleship.Weapons.targets":
                            info['targetX']= value[0][0]
                            info['targetY'] = value[0][1]
                        else:
                            info[keys_to_extract.get(key)] = value
                    else:
                        datalogger.error(f"{key} not available in received data.")
                        break

                # print("len: " + str(len(cst.get_coordinates())))
                cst.update_coordinates_list(info)

            except json.JSONDecodeError:
                datalogger.error(f"Received invalid JSON: {message}")

    except KeyboardInterrupt:
        datalogger.error("Client stopped.")
    except Exception as e:
        datalogger.error(e)

    finally:
        # Close the socket and terminate the ZeroMQ context
        socket.close()
        context.term()

if __name__ == '__main__':
    # logging.basicConfig(filename='./logs/app.log', level=logging.INFO)  # Configures logging to save logs in 'app.log' file and sets log level to INFO
    # Start the zmq_client in a separate thread
    print("Before starting Flask app")
    zmq_thread = threading.Thread(target=zmq_client, daemon=True)
    print("ZMQ starting")
    zmq_thread.start()

    app.run(debug=True,host='0.0.0.0',port=cst.port)
