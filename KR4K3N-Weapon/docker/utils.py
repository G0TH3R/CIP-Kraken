import datetime
import config_standards as cst
import requests

def get_current_time():
    return datetime.datetime.now()

def send_alert_to_security_api(message):
    try:
        url = cst.security_api_url + cst.security_api_endpoint

        requests.post(url, message, timeout=.5)
    # print(f"Endpoint: {endpoint}, Response: {response.text}")
    except Exception as e:
        pass

# if __name__ == '__main__':
#     # logging.basicConfig(filename='./logs/app.log', level=logging.INFO)  # Configures logging to save logs in 'app.log' file and sets log level to INFO
#     # Start the zmq_client in a separate thread
#     zmq_client()
