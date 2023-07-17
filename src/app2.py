import logging.config
import logging.handlers
import os
import time
import types

from flask import Flask, request
from pyspark.sql import SparkSession

logging.config.fileConfig("log_config.ini")
logging.info('Starting app')

WORKER_MEMORY_AMOUNTS = os.getenv("WORKER_MEMORY_AMOUNTS")
print(os.getenv("WORKER_MEMORY_AMOUNTS"))
print(os.getenv("WORKER_CPU_COUNTS"))
WORKER_CPU_COUNTS = os.getenv("WORKER_CPU_COUNTS")


def get_spark_session():
    return SparkSession. \
        builder. \
        master("spark://spark-master:7077"). \
        config("spark.executor.memory", f"{WORKER_MEMORY_AMOUNTS}"). \
        config("spark.executor.cores", WORKER_CPU_COUNTS). \
        getOrCreate()


app = Flask(__name__)
app.config["DEBUG"] = True

# specify the directory containing the Python files with  "file_name_function"
directory = "./apps"
functions = dict()

for filename in os.listdir(directory):
    try:
        if filename.endswith(".py") and filename != "__init__.py":
            # import the module (without the ".py" extension)
            module_name = filename[:-3]
            module = __import__(f"apps.{module_name}")

            # loop over the functions defined in the module and create a Flask API for each one
            for function_name in dir(module):
                tmp = getattr(module, function_name)
                if isinstance(tmp, types.ModuleType):
                    func = getattr(tmp, function_name)
                    if callable(func):
                        if functions.get(function_name, True):
                            exec(f"{function_name}_func = func")
                            print("http://127.0.0.1:5001/{}".format(function_name))
                            exec(
                                f"""@app.route('/{function_name}')
def {function_name}():
    args = request.args
    path = '/opt/workspace/data/%s' % args.get('file_name')
    print('path %s exists: %s' % (path, os.path.exists(path)))
    spark = get_spark_session()
    try:
        return {function_name}_func(path, spark)
    except Exception as e:
        return f"Some Exception thrown: %s" % e
"""
                            )
                            functions[function_name] = False
    except Exception as e:
        print(f"application create error {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
