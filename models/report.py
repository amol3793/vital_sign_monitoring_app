
from multiprocessing import Process, Queue
import time
import pandas as pd
import json
import pprint
from tabulate import tabulate
import numpy as np
from datetime import timedelta

class Report():
    def __init__(self, multiprocess_queue, runtime, output_location, log, report_info):
        self.realtime_data_incoming_queue = multiprocess_queue
        self.__df = pd.DataFrame()
        self.log = log
        self.runtime = runtime
        self.__user_df_list = pd.DataFrame()
        self.__output_loc = output_location
        self.__report_info = report_info
        self.__report2_tz_str = report_info.get('report2_tz_str')
        self.__report2_start_time = report_info.get('start_time')
        self.__report2_end_time = report_info.get('end_time')

    def populate_dataframe_in_realtime(self):
        self.__shared_queue  = Queue()
        p = Process(target=self.populate_df, args=(self.__shared_queue, ))
        p.start()
        p.join()
        #populated df from  other process (interprocess-communication)
        self.__df = self.__shared_queue.get()

    def populate_df(self, shared_memory):
        self.log.info("started populating df in real-time")
        time.sleep(1)
        q = self.realtime_data_incoming_queue
        count = self.runtime
        while q.empty() is False:
            each_message_dict = q.get()
            df = pd.DataFrame(each_message_dict, index=[0])
            self.__df = self.__df.append(df)
            self.log_information(each_message_dict) #uncomment  to see the realtime updation of dataframe

            #If not running on fast mode
            #any way code has to wait till runtime as persecond data is getting produced
            #in self.runtime realtime_data_incoming_queue will be filled completly
            # so after runtime no need to sleep/wait just get all  the information from the queue without waiting
            if count >=0:
                time.sleep(1)
            count -= 1
        shared_memory.put(self.__df)

    def get_realtime_df(self):
        return self.__df

    def log_information(self, each_message):
        log = self.log
        msg = "Incoming Message Stream: \n {message} \n".format(
            message=pprint.pprint(each_message)
        )
        # log.info(msg)
        print ("\n")
        log.info(self.__df)
        print ("\n")


    def format_dataframe(self):
        # self.log.info(self.__df)
        df = self.__df
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)
        self.__df = df.tz_localize('UTC')

        #split data frame user by (grouping)
        self.__user_df_list = self.split_df_userby(self.__df)

    def display_generated_dataframe(self):
        print ("ACTUAL RAW DATAFRAME \n")
        print(tabulate(self.__df, headers='keys', tablefmt='psql'))


    def split_df_userby(self, df):
        df_list = []
        gk = df.groupby('user_id')
        user_id_list  = gk.first().index.to_list()
        for user_id in user_id_list:
            df = gk.get_group(user_id)
            df = df.assign(user_id=user_id)
            df_list.append((df, user_id))
        return df_list

    def generate_report1_for_all_user(self):
        self.__report1_df_list = []
        for df, user_id in self.__user_df_list:
            self.__report1_df_list.append((self.generate_report1(df, user_id), user_id))


    def generate_report1(self,  df, user_id):
        #resample 15min data with average value
        df_15min_avg = df.resample('15min').agg({'heart_rate':np.average, 'respiration_rate': np.average})
        df_15min_avg.columns = ['avg_hr', 'avg_rr']
        #resample 15min data with max value
        df_15min_max = df.resample('15min').agg({'heart_rate':np.max, 'respiration_rate': np.max})
        df_15min_max.columns = ['max_hr', 'max_rr']
        #resample 15min data with min value
        df_15min_min = df.resample('15min').agg({'heart_rate':np.min, 'respiration_rate': np.min})
        df_15min_min.columns = ['min_hr', 'min_rr']
        result_df  = pd.concat([df_15min_avg, df_15min_max, df_15min_min], axis=1)

        result_df.index.name = 'seg_start (UTC)'
        result_df.insert(0, 'seg_end (UTC)',  pd.to_datetime(result_df.index.values) + timedelta(minutes=15) ) 

        #create csv file
        out_loc = self.__output_loc / "report_1_{}.csv".format(user_id)
        result_df.to_csv(out_loc)


        #display
        print ("REPORT 1: 15min Sampled data for user_id:{}".format(user_id))
        print(tabulate(result_df, headers='keys', tablefmt='psql'))
        print("This report CSV file location: {} \n".format(out_loc))
        #Optional: store into  csv using .to_csv()
        return result_df

    def generate_report2_for_all_user(self):
        """
           Have to generate report 2 from report 1
           input: Timezone information in string
        """
        tz_str = self.__report2_tz_str
        start_time = self.__report2_start_time
        end_time = self.__report2_end_time
        self.__report2_df_list = []
        for df, user_id in self.__report1_df_list:
            self.__report2_df_list.append((self.generate_report_2(df, user_id,  tz_str, start_time, end_time), user_id))

    def generate_report_2(self, df, user_id,  tz_str, start_time, end_time):
        #covert index
        df = df.tz_convert(tz_str)

        #filter the data in the 15 min df between start_time and end_time
        df = df[start_time:end_time]

        #Do 1 hr resampling to the filter df
        hourly_resampled_df = df.resample('1H')
        df_max = hourly_resampled_df.max().filter(['max_hr','max_rr'])
        df_min = hourly_resampled_df.min().filter(['min_hr','min_rr'])
        df_mean = hourly_resampled_df.mean().filter(['avg_hr','avg_rr'])
        result_df  = pd.concat([df_mean, df_max, df_min], axis=1)

        result_df.index.name = "seg_start ({})".format(tz_str)
        result_df.rename(columns={"seg_end (UTC)": "seg_end ({})".format(tz_str)}, inplace=True)

        #create csv file
        out_loc = self.__output_loc / "report_2_{}.csv".format(user_id)
        result_df.to_csv(out_loc)

        #display
        print ("REPORT 2: Hourly Sampled data for user_id:{} from report 1".format(user_id))
        if result_df.empty:
            print ("REPORT 2 is empty as there is no data between start_time and end_time")
        print(tabulate(result_df, headers='keys', tablefmt='psql'))
        print("This report CSV file location: {} \n".format(out_loc))
        #Optional: store into  csv using .to_csv()
        return result_df

