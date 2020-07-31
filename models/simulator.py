import random
from models.vital_sign_data import VitalSignData
from models.pateint import  Patient
from datetime import datetime, timedelta
from pathlib import Path
import json
import os
import time


class Simulator():

    def __init__(self, simulation_frequency=1, runtime=3600):
        # In seconds
        self.__simulation_frequency = simulation_frequency
        # simulation runtime (In Seconds)
        self.__runtime = runtime

    def start(self):
        time_now = datetime.utcnow().replace(microsecond=0)
        end_time = time_now + timedelta(seconds=self.__runtime)

        while end_time > time_now:
            self.perform_simulation(time_now)
            time_now += timedelta(seconds=1)
            time.sleep(self.__simulation_frequency)

        # for sec in range(0, (end_time - time_now).seconds, self.__simulation_frequency):
        #     self.perform_simulation(time_now)
        #     time_now += timedelta(seconds=sec)

    def perform_simulation(self, date_time):
        record_json = self.create_simulation_data(date_time)
        self.post_data(record_json)

    def create_simulation_data(self, date_time):
        """
            Create random data set simulated at every interval i.e per simulation frequency data
        """
        raise NotImplementedError

    def post_data(self, data):
        """
            Ways to post the real time data:
               1. Kafka
               2. Celery
               3. Filesystem (updating all the records into a file based on user_id)
        """
        raise NotImplementedError

    def  get_run_time(self):
        return self.__runtime

    def is_fast_mode(self):
        return self.__fast_mode

class VitalSignMonitor(Simulator):

    def __init__(self, simulation_frequency, runtime):
        super().__init__(simulation_frequency, runtime)
        self.__user = Patient()
        self.__basepath = Path('/tmp/vsm-service-demo/message-communication/')
        self.__basepath.mkdir(parents=True, exist_ok=True)
        self.__filestore = self.__basepath / str(str(self.__user.get_patient_id()) + '.json')
        self.__simulation_data_class = VitalSignData

    def create_simulation_data(self, date_time):
        uid = self.__user.get_patient_id()
        hr = random.randint(0, 300)
        rr = random.randint(0, 100)
        act = random.randrange(0, 20)
        data_obj = VitalSignData(hr, rr, act)
        record_json = data_obj.to_json()
        record_json.update({
            "timestamp": date_time.timestamp(),
            "user_id": str(uid)
        })
        return record_json

    def post_data(self, data):
        """
            Ways to post the real time data:
               1. Kafka
               2. Celery
               3. Filesystem (updating all the records into a file based on user_id)

            Using Filesystem here for simplicity and saving time
        """
        self.get_path_to_watch().mkdir(exist_ok=True)
        with open(self.__filestore, 'a+') as f:
            f.write(json.dumps(data) + os.linesep)

    def get_path_to_watch(self):
        return self.__filestore.parent

    def get_user_id(self):
        return self.__user.get_patient_id()

    def get_user(self):
        return self.__user

    def get_file_storage(self):
        return self.__filestore

