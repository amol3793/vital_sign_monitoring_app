import time
from watchdog.observers import Observer
from pathlib2 import Path
import logging
from message_listner.event import MessageReader
from message_listner.event_handler import MessageReadHandler
import os
from utility import logging

def define_incoming_data_listner(simulators, multiprocess_shared_queue):

    observer = Observer()
    for simulator in simulators:
        event = MessageReader(simulator)
        event_handler = event.get_event_handler(multiprocess_shared_queue)
        user_id=simulator.get_user_id()
        observer.schedule(event_handler, str(event.base_path), recursive=False)
        logging.info("MessageReadHandler is watching '{path}' for data produced by simulator_{user_id}".format(
            path=str(simulator.get_path_to_watch().absolute())+"/"+str(user_id),
            user_id=user_id
        ))
        return observer

def run_incoming_data_listner(simulators, multiprocess_shared_queue):
    """
    Starting Filewatcher observer, this will act as a LISTNER.
    This listner will be stopped when simulator will stop producing data.
    """
    simulator = simulators[-1]
    simulator_run_time = simulator.get_run_time()
    observer = define_incoming_data_listner(simulators, multiprocess_shared_queue)
    observer.start()
    try:
        for _ in range(int(simulator_run_time)):
            time.sleep(1)
            assert observer.is_alive(), "The watcher died unexpectedly"
    except KeyboardInterrupt:
        observer.stop()
