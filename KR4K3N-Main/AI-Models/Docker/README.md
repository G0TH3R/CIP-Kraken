
# AI_Flask_ ZeroMQ_Application

## Overview
This application is a Flask-based server designed to handle HTTP requests and interact with a ZeroMQ subscriber. It demonstrates basic capabilities of Flask for web API development and integration with ZeroMQ for message passing.

## Features
- Subscribes to ZeroMQ messages and processes data.
- Handles HTTP GET and POST requests.
- Stores and retrieves data via a simple in-memory storage mechanism.
- Dynamically reads keys for data extraction from a file.

## Getting Started

### Prerequisites
- Python 3.9 or later
- Flask
- ZeroMQ

### Installation
Clone the repository to your local machine:
```
git clone https://github.com/KR4K3N-CIP/KR4K3N-Main.git
```

### Running the Application
Navigate to the application directory and run the Python script:
```
python client_security-ai.py
```
#### Extract keys from the Battleship simulator
Ensure that your 'keys_to_extract.txt' file is in the same directory as the Dockerfile. Each key corresponds to a data field in the ZeroMQ messages that the battleship simulation is publishing in the docker network 'kr4k3n_net'.

##### Integration with the Application
###### **Loading Keys**
- When the application starts, it reads the 'keys_to_extract.txt' file.
- The keys read from the file are stored in a list, which is used throughout the application's runtime.

  
###### **Data Processing**
- During the processing of ZeroMQ messages, the application checks each message for the presence of the keys listed in 'keys_to_extract.txt'.
- If a key is found, the corresponding data is extracted and processed according to the application's logic.

  
###### **Customization**
- Users can customize which data fields to process by simply editing the 'keys_to_extract.txt' file and restarting the application.
- This approach eliminates the need for code changes when modifying data processing behavior.

### Using the Application
- Send POST requests to `/store_post_data` with JSON data to store key-value pairs.
- Send GET requests to `/get_post_data` with a key to retrieve the corresponding value.
- Access the ZeroMQ subscriber data via GET requests to `/get_prediction`.

### Dockerization
A Dockerfile is included for containerizing the application.

#### Building the Docker Image
```
docker build -t security_ai -f Dockerfile.security_ai .
```

#### Running the Docker Container
Consider the Docker Network 'kr4k3n_net' must be previously created in order to interact with the 'batlleship' container on port 5556.
```
docker run -d --name security_ai -e zmq-server=battleship --network kr4k3n_net -p 6010:6010 security_ai
```
### Application usage

In order to obtain the "prediction" from the application you can execute a **GET** request.
```
curl http://127.0.0.1:6010.get_prediction
```

In order to submit information to the Application you can store the information using a **POST** request to the application. 
```
curl -X POST http://127.0.0.1:6010/store_post_data -H "Content-Type: application/json" -d '{"key":"power","value":"66"}'
```

TO verify or view the previously stored key:value pair in the application you can make a **GET** request to the application. 
```
curl http://127.0.0.1:6010/get_post_data\?key\power
```

## License
This project is licensed under the MIT License - see the LICENSE.md file for details.

## Acknowledgments
- Flask for providing a lightweight web framework.
- ZeroMQ for efficient message passing.
