import logging, os
from logging import FileHandler
import csv

log_location = os.path.abspath(os.path.join(".", "logs", "logfile.csv"))
FORMAT = '%(asctime)s, %(levelname)s, %(name)s, %(message)s'
# FORMAT = '%(asctime)s : %(levelname)s : %(name)s : %(message)s'

if not os.path.exists('./logs'):
    os.mkdir('./logs/')

if not os.path.exists(log_location):
    with open(log_location, 'w') as csvfile:
        # Write a header if needed
        fieldnames = ['Timestamp', 'Level', 'LoggerName', 'Message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

if os.path.exists(log_location):
    # If the file does not exist, create it
    with open(log_location, 'a', newline='') as csvfile:
        fieldnames = ['Timestamp', 'Level', 'LoggerName', 'Message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

# def get_csv_handler():
#     csv_handler = StreamHandler()
#     csv_handler.setFormatter(logging.Formatter(FORMAT))
#
#     return csv_handler
#
def get_filehandler():
    file_handler = FileHandler(log_location)
    file_handler.setFormatter(logging.Formatter(FORMAT))
    file_handler.setLevel(logging.DEBUG)
    return file_handler

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    log.addHandler(get_filehandler())

    # Example log entries
    log.info("This is an info message.")
    log.warning("This is a warning message.")
