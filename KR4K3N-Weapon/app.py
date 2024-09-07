from flask import Flask, render_template, request, jsonify
import math

import config_standards
import config_standards as cst
import utils
import logging
import logger as log

app = Flask(__name__)
datalogger = logging.getLogger(__name__)
datalogger.addHandler(log.get_filehandler())

# Initial missile state (unarmed by default)
missile_color = '#00FF00'  # Green color for unarmed missile
missile_status = 'Unarmed'
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
        missile_status = "Armed"
        datalogger.warning('{} | {} | {} | Missile armed successfully'.format(cst.weapons_tag, cst.get_arm_status(), cst.success))
        return jsonify({'message': 'Missile armed successfully','status':'Armed'})
    else:
        datalogger.warning('{} | {} | {} | No More Rounds Remaining'.format(cst.weapons_tag, cst.get_arm_status(), cst.error))
        return jsonify({'message': 'No More Rounds Remaining','status':'Error'})

# API route to unarm the missile
@app.route('/unarm', methods=['POST'])
def unarm_missile():
    datalogger.debug("/unarm info: {}".format(request))
    global missile_color
    missile_color = '#00FF00'  # Green color for unarmed missile
    global missile_status
    missile_status = "UnArmed"
    datalogger.warning('{} | {} | {} | Missile unarmed successfully'.format(cst.weapons_tag, cst.get_unarm_status(), cst.success))
    return jsonify({'message': 'Missile unarmed successfully','status':'Unarmed'})

# API route to fire the missile
@app.route('/fire', methods=['POST'])
def fire_missile():
    datalogger.debug("/fire info: {}".format(request))
    global missile_status
    if checkNumberOfRemainingRounds():
        if 'Armed' in missile_status:
            global missile_color
            missile_color = '#000000'  # Green color for unarmed missile
            missile_status = "Fired"
            global missile_fire_time
            missile_fire_time = utils.get_current_time()
            global fired_rounds
            fired_rounds = fired_rounds + 1
            global in_range
            if in_range:
                datalogger.warning('{} | {} | {} | Missile fired successfully'.format(cst.weapons_tag, cst.get_fire_status(), cst.success))
                return jsonify({'message': 'Missile fired successfully','status':'fired'})
            else:
                datalogger.warning('{} | {} | {} | Missile Missed'.format(cst.weapons_tag, cst.get_fire_status(), cst.fail))
                return jsonify({'message': 'Missile Missile Missed','status':'fail'})
        else:
            datalogger.warning('{} | {} | {} | Missile is not Loaded'.format(cst.weapons_tag, cst.get_fire_status(), cst.error))
            return jsonify({'message': 'Missile is not Loaded','status':'Error'})
    else:
        datalogger.warning('{} | {} | {} | No More Rounds Remaining'.format(cst.weapons_tag, cst.get_fire_status(), cst.error))
        return jsonify({'message': 'No More Rounds Remaining','status':'Error'})

# API route to reload the missile
@app.route('/reload', methods=['POST'])
def reload_missile():
    datalogger.debug("/reload info: {}".format(request))
    if checkNumberOfRemainingRounds():
        if checkTimeElapsed():
            global missile_color
            missile_color = '#FF0000'  # Green color for unarmed missile
            global missile_status
            missile_status = "Armed"
            datalogger.warning('{} | {} | {} | Missile Reloaded successfully'.format(cst.weapons_tag, cst.get_arm_status(), cst.success))
            return jsonify({'message': 'Missile Reloaded successfully','status':'Reloaded'})
        else:
            datalogger.warning('{} | {} | {} | Please wait sometime before reloading'.format(cst.weapons_tag, cst.get_reload_status(), cst.error))
            return jsonify({'message': 'Please wait sometime before reloading','status':'Error'})
    else:
        datalogger.warning('{} | {} | {} | No More Rounds Remaining'.format(cst.weapons_tag, cst.get_reload_status(), cst.error))
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
        config_standards.update_coordinates_list(request.form)
        return jsonify({'success': True})
    except Exception as e:
        datalogger.error(f"Error in /getData: {str(e)}")
        return jsonify({'error': 'Internal Server Error'}), 500

def checkIfTargetInRange():
    try:
        if len(config_standards.get_coordinates()) > 0:
            data = config_standards.get_last_coordinate()
            if len(data) > 0:
                shipX = float(data.get('shipX'))
                shipY = float(data.get('shipY'))
                targetX = float(data.get('targetX'))
                targetY = float(data.get('targetY'))
                distance = math.sqrt((shipX - targetX)**2 + (shipY - targetY)**2)
                global in_range
                if cst.get_weapons_range() < distance:
                    in_range = False
                    datalogger.warning('{} | {} | {} | Out of Range'.format(cst.weapons_range_tag, cst.off_range, cst.fail))
                    return  False
                else:
                    in_range = True
                    datalogger.warning('{} | {} | {} | In Range'.format(cst.weapons_range_tag, cst.in_range, cst.success))
                    return True
            else:
                datalogger.warning('{} | {} | {} | No Coordinate data'.format(cst.weapons_range_tag, cst.fail, cst.fail))
                return 'NA'
        else:
            datalogger.warning('{} | {} | {} | No Coordinate data'.format(cst.weapons_range_tag, cst.fail, cst.fail))
            return 'NA'
    except Exception as e:
        datalogger.error(e)
    
@app.route('/get_missile_color', methods=['GET'])
def get_missile_color():
    global missile_color
    global missile_status
    global total_rounds
    global fired_rounds
    return jsonify({'color': missile_color, 'status': missile_status, 'rounds': total_rounds-fired_rounds, 'range_status': checkIfTargetInRange()})

if __name__ == '__main__':
    # logging.basicConfig(filename='./logs/app.log', level=logging.INFO)  # Configures logging to save logs in 'app.log' file and sets log level to INFO
    app.run(debug=True)
