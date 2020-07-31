Logging ISSUE: The listner (Watcher) will produce repeated logs (number of repeated info  = actual number * number of simulator)
example: for 3 simulator 3 times same data will be displayed on log because I am not handling log sharing between the process.
This can be resolved using https://pypi.org/project/multiprocessing-logging/