import socket
import subprocess

class Scheduler:
    def __init__(self):
        self.best_effort = subprocess.Popen(["python", "train.py", "--test", "--load_path", "C:\\Users\\adori\\Documents\\Github\\dataset\\model_base", "AssettoCorsa.track=monza", "AssettoCorsa.car=bmw_z4_gt3"])
        self.back_on_track = subprocess.Popen(["python", "train.py", "AssettoCorsa.track=monza", "AssettoCorsa.car=bmw_z4_gt3"])
        self.socket = None

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(("0.0.0.0", 2345))

if __name__ == "__main__":
    scheduler = Scheduler()
