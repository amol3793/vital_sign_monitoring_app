#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from message_listner.event_handler import MessageReadHandler
import pandas as pd
from utility import logging
import json
import pprint

class MessageReader(object):
    """Read row data from a file """

    accepted_filenames = ['.json']

    LAST_DATA_READ = None

    def __init__(self, simulator):
        self.simulator = simulator
        self.base_path = simulator.get_path_to_watch()

    def read_last_line(self, input_file_path):
        with open(input_file_path) as file:
            data = file.readlines()[-1]
        return data

    def read(self, input_file_path, multiprocess_shared_queue):
        try:
            data = self.read_last_line(input_file_path)
            data = json.loads(data)
        except Exception as err:
            self.on_error(input_file_path, err)
        else:
            self.on_successful_read(data, multiprocess_shared_queue)

    def on_error(self, input_file_path, err):
        logging.exception(err)
        logging.error("{} failed to read '{}' (error message: {})".format(
            self.__class__.__name__,
            input_file_path,
            err.message
        ))
    def on_successful_read(self, data, multiprocess_shared_queue):
        msg = "Incoming data information for {user_type} with ID {id}: \n {data} \n".format(
                user_type=self.simulator.get_user().__class__.__name__,
                id=self.simulator.get_user().get_patient_id(),
                data = pprint.pprint(data)# if  data!="None" else "duplicate"
            )
        logging.info(msg)
        multiprocess_shared_queue.put(data)

    def get_event_handler(self, multiprocess_shared_queue):
        return MessageReadHandler(self, multiprocess_shared_queue)
