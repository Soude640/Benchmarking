SPARK_WORKERS_COUNTS_FIELD = "Field spark worker count must be in format <number>,<number>,... like 1,5,2,7" \
                             " This means that initially the number of spark workers is 1," \
                             " but later on, it increases to five, and ..."
WORK_LOAD_USER_COUNTS_FIELD = "Field workload users count must be in format <number>,<number>,... like 10,5,8,12" \
                              " This means that initially the number of users is 10" \
                              " but later on, it increases to five. ..."
WORK_LOAD_USER_DURATION = "Field workload user duration must be in format <seconds>,<seconds>,... " \
                          "like 300,500,300,700 This means that initially number of seconds that users " \
                          "is using your application is 300, but later on, it increase to five hundred. ..."
WORK_LOAD_DATA_SIZES_FIELD = "Field workload data sizes must be in format <data_file_name>,<data_file_name>,... " \
                             " This means size of data processed, which should be in CSV format accompany with" \
                             " its name like like mlp_8KB.csv or feature_selection_100MB.csv"
WORK_LOAD_USER_THINK_TIME = "Field workload user think time must be in format <seconds>,<seconds>,... like 30,50" \
                            "This means after a request is processed by the system, " \
                            "the corresponding client will wait for some time before sending the next request"
SAME_STEP_ERROR = "Fields work_load_user_think_time, work_load_user_duration, " \
                  "work_load_users_count and app_spark_workers_count. " \
                  "The steps of all of this fields must have the same. " \
                  "In other words, if work_load_users_count has 2 steps, such as 10 and 6, " \
                  "then app_spark_workers_count should have 2 steps as well like 3,4."
TOTAL_TIME_OF_EXPERIMENT_FIELD = "Field workload user think time must be in format <seconds>,<seconds>,... like 3200" \
                                 " It represents the elapsed time between the beginning and end of the experimental process."
WORKER_CPU_COUNTS = "Field cpu must be a number like (1 or 2 or 3 or ....)"
WORKER_MEMORY_AMOUNT = "Field memory must be in format <number>g like (10g or 2g or 12g)"
SERVER_COUNT_FIELD = "server count must be 1 or 2"
API_DOC = """
# Configuration
The JSON information you need to enter should have two main sections:  "server_config" and "workload_config" . "server_config" section defines server-related parameters, while the "workload_config" section includes details about the workload, such as the number of users, activeness of the user, and specific application configurations with associated size of data . Let's break down each field and explain its purpose and expected format:  
  
## 1- “server_config”:  
- **"server_counts"**: Specifies the number of servers in the configuration.  
   > <sup>Format: Integer value representing the count of servers.</sup>
- **"spark_worker_counts"**: Indicates the number of Spark workers for distributed processing.  
   >  <sup>Format: Integer value representing the count of spark workers.           			
- **"cpu_of_every_worker"**: Specifies the number of CPUs allocated to each Spark worker.  
   >  <sup>Format: Integer value representing the count of CPUs per worker.  
- **"memory_of_every_worker"**: Indicates the amount of memory allocated to each Spark worker.  
   >  <sup>Format: Integer value representing the memory size in units such as GB or MB or KB.  
## 2- "workload_config":  
-  **"users_count"**: Specifies the total number of users or clients generating the workload.  
>  <sup>Format: Integer value representing the count of users.
-  **"time_in_second"**: Indicates the duration of the workload in seconds.
>  <sup>Format: Integer value representing the duration in seconds.</sup>
- **"apps"**: Specifies an array of application configurations within the workload.  Each application configuration includes
 the following fields:
	-  **"app_name"**: Indicates the name of the application.
	>   <sup>Format: String value representing the applicationname.</sup>  
	- **"user_percentage"**: Specifies the percentage of users assigned to this application within the workload.  
	>  <sup>Format: Integer value representing thepercentage.</sup>  
	- **"data_files"**: Specifies an array of data files associated with the application.  
	>  <sup>Format: Array of strings representing the filenames.</sup>  
	- **"data_file_percentage"**: Indicates the percentage distribution of data files for this application.  
	>  <sup>Format: Array of integer float values representing the percentage for each data file.</sup>  
	- **"think_time_in_second"**: This means after a request is processed by the system, the corresponding client will wait for some time before sending the next request  
	>  <sup>Format: Integer value representing the duration in seconds.</sup>
"""
