
from comm import *

class Scheduler:
    def __init__(self):
        # start subprocess
        # self.c1 = subprocess.Popen(["python", "client.py"])

        self.best_effort = subprocess.Popen(["python", "train.py", "--test", "--load_path", "C:\\Users\\adori\\Documents\\Github\\dataset\\model_base", "AssettoCorsa.track=monza", "AssettoCorsa.car=bmw_z4_gt3"])
        # self.back_on_track = subprocess.Popen(["python", "train.py", "AssettoCorsa.track=monza", "AssettoCorsa.car=bmw_z4_gt3"])

        serv = SchedServer()
        ego = EgoClient()
        serv.start(ego)
        while True:
            if serv.current_client:
                ego.setup_server_connection(serv)
                break
            else:
                continue
    

if __name__ == "__main__":
    scheduler = Scheduler()

