import logging.config
import logging.handlers
import os
import time

from do import do
from flask import Flask, request
from pyspark.ml.feature import RFormula
from pyspark.sql import SparkSession

logging.config.fileConfig("log_config.ini")
logging.info('Starting app')

# logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
# logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)

WORKER_MEMORY_AMOUNTS = os.getenv("WORKER_MEMORY_AMOUNTS")
print(os.getenv("WORKER_MEMORY_AMOUNTS"))
print(os.getenv("WORKER_CPU_COUNTS"))
WORKER_CPU_COUNTS = os.getenv("WORKER_CPU_COUNTS")


def get_spark_session():
    return SparkSession. \
        builder. \
        master("spark://spark-master:7077"). \
        config("spark.executor.memory", WORKER_MEMORY_AMOUNTS). \
        config("spark.executor.cores", WORKER_CPU_COUNTS). \
        getOrCreate()


app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/get/', methods=['GET'])
def spark_test():
    args = request.args
    logging.info(
        f'is_need_spark_session_stop: {args},'
        f' {args.get("is_need_spark_session_stop")} {type(args.get("is_need_spark_session_stop"))}'
    )
    spark = get_spark_session()
    if args.get('is_need_spark_session_stop') == "True":
        spark.stop()
        time.sleep(5)
        spark = get_spark_session()
        time.sleep(10)
    logging.info(f'spark:  {spark}')
    file_name = args.get("file_name")
    try:
        path = f"/opt/workspace/data/{file_name}"
        logging.info(f'path {path} exists: {os.path.exists(path)}')
        response = do(path, spark)
        return f"<h1>Sample</h1><p>{response}</p>"
    except Exception as e:
        return f"Some Exception Throwed: {e}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
