import os
import time

from pathlib2 import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
# from utility.utils import get_logger
# logging = get_logger()
from utility import logging

# DELAY = 1

def since_created(fd):
    t = time.time() - os.fstat(fd).st_mtime
    logging.info("seconds since file was last modified: {}".format(t))
    return t

class MessageReadHandler(FileSystemEventHandler):
    def __init__(self, msg_reader, multiprocess_shared_queue):
        self.msg_reader = msg_reader
        self.name = self.__class__.__name__
        self.process_shared_memory_queue = multiprocess_shared_queue

    def on_created(self, event):
        self.on_modified(event)

    def on_modified(self, event):
        modified_file_path = Path(event.src_path)
        self.process_file(modified_file_path)

    def process(self, created_file_path):
        self.msg_reader.read(created_file_path,  self.process_shared_memory_queue)

    @property
    def accepted_filenames(self):
        return self.msg_reader.accepted_filenames

    def process_file(self, created_file_path):
        try:
            # Opening a file descriptor so that we can refer to it even if it's removed
            fd = os.open(str(created_file_path), os.O_RDONLY)
        except OSError as e:
            logging.exception("Unable to open the file", e)
            return
        if created_file_path.suffix not in self.accepted_filenames:
            logging.warn("{} does not accept '{}' files. Ignoring...".format(self.name, created_file_path.suffix))
        else:
            # while since_created(fd) < DELAY:
            #     time.sleep(DELAY)
            self.process(created_file_path)