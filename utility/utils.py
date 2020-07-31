import logging

import threading

class LogSingletonDoubleChecked(object):

    # resources shared by each and every
    # instance

    __singleton_lock = threading.Lock()
    __singleton_instance = None

    # define the classmethod
    @classmethod
    def instance(cls, *args, **kwargs):

        # check for the singleton instance
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls(*args, **kwargs)

        # return the singleton instance
        return cls.__singleton_instance

    def __init__(self, *args, **kwargs):
        log_level = kwargs.get('log_level')
        name = kwargs.get('name')
        log = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.setLevel(log_level)
        self.__log = log

    def get_logger(self):
        return self.__log

# def get_logger(log_level=logging.DEBUG):
#     log = logging.getLogger(' VitalSignMonitoringService')
#     handler = logging.StreamHandler()
#     formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
#     handler.setFormatter(formatter)
#     log.addHandler(handler)
#     log.setLevel(log_level)
#     return log

logger = LogSingletonDoubleChecked.instance(log_level=logging.DEBUG, name='VitalSignMonitoringService')
log = logger.get_logger()