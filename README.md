# Overview
![Image of Overiview](https://github.com/amol3793/vital_sign_monitoring_app/blob/master/docs/overview.png)


# DEMO (GIF)

The below demo is showing how to set the different simulator and report information  and start the app.

### run application

```python
python app.py
```

On  successfull run logs will start appearing.

Initial logs will be just  the basic function call logs like below.
![Image of log1](https://github.com/amol3793/vital_sign_monitoring_app/blob/master/docs/initial_log.png)

After that all  the incomming  messages by the listner start appearing along with  updated dataframe in real time, as shown below in the  demo gif.

![DEMO ](http://g.recordit.co/D2COyLpyc1.gif)

Finally all the  Service out-put  Information will be appeared on the  screen as  shown below, 

![DEMO ](http://g.recordit.co/4k0OogH2dP.gif)


### Example 1: Current datetime (say 2020-07-31 01:57:40+00:00) is not in between start_time  and end_time
So, report 2 will be empty

#### INPUT
```
 simulator_report_info = {
        "number_of_simulator": 3,
        "runtime": 200,  #in sec
        "simulation_frequency":1, #in sec
        'report_info': {
            "report2_tz_str": "Asia/Kolkata",
            "start_time": "31-07-2020-11:59",
            "end_time": "31-07-2020-13:00",
        }
```

#### OUTPUT
![OUTPUT ](http://g.recordit.co/G05XjYWPXo.gif)[http://g.recordit.co/G05XjYWPXo.gif]


# DESIGN
![](https://github.com/amol3793/vital_sign_monitoring_app/blob/master/docs/desing.png)

### Logging ISSUE
Since the  single app.py starts different many process in  parallel so there is issue  in logging  such as:
 *  Repeatition of logs
 *  Missing  some data point in log  (but it  will be there  in  the storage)
example: for 3 simulator 3 times same data will be displayed on log because I am not handling log sharing between the process.

This can be resolved using https://pypi.org/project/multiprocessing-logging/
