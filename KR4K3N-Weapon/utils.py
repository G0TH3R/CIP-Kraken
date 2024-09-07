import datetime
# import zmq
import config_standards

def get_current_time():
    return datetime.datetime.now()

# def zmq_client():
#     socket = None
#     context = None
#     try:
#         # Create a ZeroMQ context
#         context = zmq.Context()
#
#         # Create a REQ (request) socket
#         socket = context.socket(zmq.SUB)
#
#         # Connect to the server
#         server_address = "tcp://{}:{}".format(config_standards.navigators_ip, config_standards.navigators_port)  # Replace with the actual server address
#         socket.connect(server_address)
#
#         # Subscribe to all messages
#         socket.setsockopt_string(zmq.SUBSCRIBE, "")
#
#         while True:
#             message = socket.recv_string()
#             config_standards.update_coordinates_list(message)
#             # Do something with the received message
#
#     except KeyboardInterrupt:
#         print("Client stopped.")
#
#     finally:
#         # Close the socket and terminate the ZeroMQ context
#         socket.close()
#         context.term()
