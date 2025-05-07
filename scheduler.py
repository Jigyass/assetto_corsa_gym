
from comm import *

class Scheduler:
    def __init__(self):
        dataset_path = "C:\\Users\\adori\\Desktop\\backup\\assettoCorsaGym\\data_sets\\monza\\bmw_z4_gt3\\20241108_SAC"
        # under-trained model
        self.best_effort = subprocess.Popen(["python", "train.py", "--test", "--load_path", f"{dataset_path}\\model\\checkpoints\\step_00200000"]).pid
        # off track (best model)
        self.off_track = subprocess.Popen(["python", "train.py", "--test", "--load_path", "C:\\Users\\adori\\Documents\\GitHub\\dataset\\model_base"]).pid
        print(f"Best Effort PID: {self.best_effort}\nOff Track PID: {self.off_track}")

    def start(self):
        serv = SchedServer()
        ego = EgoClient()
        serv.start(ego)
        while True:
            # print(serv.current_client)
            if serv.current_client:
                ego.setup_server_connection(serv, self.schedule)
                break
            else:
                continue

    def schedule(self, clients: list[Client], data: str):
        if (len(clients) == 1):
            return clients[0]
        tires = eval(data)["numberOfTyresOut"]
        if tires >= 2:
            print("Off Track")
            result = next((c for c in clients if c.pid == self.off_track), None)
        else:
            print("Under-trained")
            result = next((c for c in clients if c.pid == self.best_effort), None)
        return result


if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.start()
