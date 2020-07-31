from models.simulator import VitalSignMonitor
from models.report import Report
from multiprocessing import Process, Queue
import asyncio
from message_listner.watcher import run_incoming_data_listner
from utility import logging as log
import time
from pathlib import Path
import json

class VitalSignMonitoringService():

    DEFAULT_SIMULATOR = VitalSignMonitor

    def __init__(self, using_simulator=False, **simulator_report_info):
        if using_simulator and not simulator_report_info:
            raise Exception("Simulator's Information is  required  on  using  simulator")

        if using_simulator:
            self.__using_simulator = using_simulator
            self.__simulators =  self.create_simulators(**simulator_report_info)
            self.__simulators_processes = self.create_simulations_process(self.__simulators)

        self.__multiprocess_queue = Queue()
        self.__output_folder = Path('/tmp/vsm-service-demo/output/')
        self.__output_folder.mkdir(parents=True, exist_ok=True)

        #TODO: report should not be a part of VitalSignMonitoringService class directly
        report_info = simulator_report_info.get('report_info')
        self.__report = Report(self.__multiprocess_queue, self.runtime, self.__output_folder, log, report_info)


    @property
    def runtime(self):
        s = self.__simulators[-1]
        return s.get_run_time()

    def is_simulation_source(self):
        return self.__using_simulator

    def get_all_simulator_process(self):
        return  self.__simulators_processes

    def get_all_simulator(self):
        return  self.__simulators

    def create_simulators(self, **simulator_report_info):
        if not self.is_simulation_source():
            return []
        simulator = simulator_report_info.get('simulator', VitalSignMonitoringService.DEFAULT_SIMULATOR)
        number_of_simulator = simulator_report_info.get('number_of_simulator')
        simulation_frequency = simulator_report_info.get('simulation_frequency')
        runtime = simulator_report_info.get('runtime')
        simulators = [simulator(simulation_frequency, runtime) for s in range(number_of_simulator)]
        return simulators

    def create_simulations_process(self, simulators):
        return [Process(target=s.start) for s in simulators]

    def listen_realtime_data(self):
        """
         - using fileventhandler for listning as used filesystem for communication
         - Using Filesystem for message communication for "data persistency" (permanent storage)
         - Other methods to implement here can be having a kafka consumer here etc.
        """
        return Process(target=run_incoming_data_listner, args=(self.__simulators, self.__multiprocess_queue))

    def get_all_simulated_data(self):
        return self.__multiprocess_queue

    def populate_dataframe_in_realtime(self):
        # log.info("started making dataframe from real time incoming data")
        self.__report.populate_dataframe_in_realtime()
        log.info("data frame populated at realtime")

    def analysis_and_make_all_report(self):

        print ("\n\n\n REPORTS INFORMATION \n")
        self.get_received_data_in_jsonfile()
        self.__report.format_dataframe()
        self.__report.display_generated_dataframe()
        self.__report.generate_report1_for_all_user()
        self.__report.generate_report2_for_all_user()

        # self.__report.generate_report2()
        # self.__report.generate_report3()

    def get_received_data_in_jsonfile(self):
        """
        Get all the received  data in the json file,
        Since the vitalSign data is getting stored in file (per user) hence
        the number of file this function will return is same as number of user(or simulator)

        Return: Print the location list of the output json file (user by)
        """
        display_message = "\n Loation of Json file with all the raw data: \n"
        for s in self.__simulators:
            file_storage = s.get_file_storage()
            out_file_path = self.make_file_storage_tojson_file(file_storage)
            display_message += "User with ID {user_id}: {out_file_path} \n".format(user_id=s.get_user_id(), out_file_path=out_file_path)

        print(display_message)

    def make_file_storage_tojson_file(self, file_storage):
        # read-data made json object
        with open(file_storage) as file:
            json_data = file.readlines()

        # write json data to output folder
        out_loc = self.__output_folder / file_storage.name
        with open(out_loc, 'w') as outfile:
            json.dump(json_data, outfile)

        return out_loc

    @classmethod
    def run(cls, using_simulator, **kwargs):
        # Initialize log
        log.info("VitalSignMonitoringService is started now")

        #Initialise  service
        vsm_service = VitalSignMonitoringService(using_simulator, **kwargs)

        #get all the simulator process
        simulator_process = vsm_service.get_all_simulator_process()

        #start listning incoming message
        listner_process = vsm_service.listen_realtime_data()
        listner_process.start()
        log.info("Listning service  started")

        #start all the simulator in separate  process for producing data
        for sp in simulator_process:
            sp.start()
        log.info("{number_of_simulators} simulator started".format(number_of_simulators=len(simulator_process)))

        vsm_service.populate_dataframe_in_realtime()

        for sp in simulator_process:
            sp.join()
        log.info("All the simulators  are stopped")


        listner_process.join()
        log.info("Listning is stopped now")

        # Generate all required report
        vsm_service.analysis_and_make_all_report()


        log.info("VitalSignMonitoringService is ended")



if __name__ == "__main__":

    # log.info("hello")

    using_simulator = True
    simulator_report_info = {
        # "simulator": VitalSignMonitoringService.DEFAULT_SIMULATOR,
        "number_of_simulator": 3,
        "runtime": 5,  #in sec
        "simulation_frequency":1, #in sec
        'report_info': {
            "report2_tz_str": "Asia/Kolkata",
            "start_time": "14-07-2020-15:00",
            "end_time": "14-07-2020-16:00",
        }
    }
    VitalSignMonitoringService.run(using_simulator, **simulator_report_info)
