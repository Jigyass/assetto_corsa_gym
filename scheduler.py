
from comm import *

class Scheduler:
    def __init__(self):

        # sub-optimal model (will probably go off track)
        self.sub_optimal = subprocess.Popen(["python", "train.py", "--test", "--load_path", "C:\\Users\\adori\\Desktop\\backup\\assettoCorsaGym\\data_sets\\monza\\bmw_z4_gt3\\20241108_SAC\\model\\checkpoints\\step_05400000"]).pid
        # self.sub_optimal = subprocess.Popen(["python", "train.py", "--test"]).pid
        # off track (best model)
        self.off_track = subprocess.Popen(["python", "train.py", "--test", "--load_path", "C:\\Users\\adori\\Documents\\Github\\dataset\\model_base"]).pid
        print(f"sub-optimal PID: {self.sub_optimal}\noff track PID: {self.off_track}")

    def start(self):
        serv = SchedServer()
        ego = EgoClient()
        serv.start(ego)
        # ego.start(serv)
        while True:
            # print(serv.current_client)
            if serv.current_client:
                ego.setup_server_connection(serv, self.schedule)
                break
            else:
                continue

    def schedule(self, clients: list[Client], data: str):
        tires = eval(data)["numberOfTyresOut"]
        if tires >= 3:
            # print("OFF TRACK MODEL")
            result = next((c for c in clients if c.pid == self.off_track), None)
        else:
            # print("SUB-OPTIMAL MODEL")
            result = next((c for c in clients if c.pid == self.sub_optimal), None)
        # print(result)
        return result


if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.start()
