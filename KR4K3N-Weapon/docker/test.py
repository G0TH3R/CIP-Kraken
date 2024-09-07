import requests
import random
import time
import concurrent.futures

BASE_URL = "http://127.0.0.1:5000"  # Update with the actual address where your Flask app is running

# ENDPOINTS = ['/arm', '/unarm', '/reload', '/fire', '/getData']
ENDPOINTS = ['/getData']
def send_random_post_request(endpoint, data=None):
    url = BASE_URL + endpoint

    response = requests.post(url, data=data)
    print(f"Endpoint: {endpoint}, Response: {response.text}")

def generate_coordinates():
    max_distance = 500
    shipX = random.uniform(0, max_distance)
    shipY = random.uniform(0, max_distance)
    targetX = random.uniform(0, max_distance)
    targetY = random.uniform(0, max_distance)

    return {'shipX': shipX, 'shipY': shipY, 'targetX': targetX, 'targetY': targetY}

if __name__ == "__main__":
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            while True:
                endpoint = random.choice(ENDPOINTS)

                if endpoint == '/getData':
                    data = generate_coordinates()
                else:
                    data = None

                executor.submit(send_random_post_request, endpoint, data)
                time.sleep(.1)  # Adjust the sleep time according to your needs

    except KeyboardInterrupt:
        print("Script terminated.")
