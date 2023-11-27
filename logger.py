import csv
import time

class RealTimeLogger:
    def __init__(self, filename='log12.csv'):
        self.filename = filename
        self.file_opened = False
        self.file = None

    def open_file(self):
        self.file = open(self.filename, 'a', newline='')
        self.csv_writer = csv.writer(self.file)

        # If the file is empty, write the header
        if self.file.tell() == 0:
            header = ["Time", "BallX", "BallY", "VelX", "VelY", "Pitch", "Roll", "TargetX", "TargetY"]
            self.csv_writer.writerow(header)

        self.file_opened = True

    def close_file(self):
        if self.file_opened:
            self.file.close()
            self.file_opened = False

    def log_data(self, time_stamp, ball_x, ball_y, vel_x, vel_y, pitch, roll, target_x, target_y):
        if not self.file_opened:
            self.open_file()

        data = [time_stamp, ball_x, ball_y, vel_x, vel_y, pitch, roll, target_x, target_y]
        self.csv_writer.writerow(data)
        self.file.flush()  # Flush to disk to ensure data is written immediately


