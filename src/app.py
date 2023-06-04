import logging.config
import logging.handlers

logging.config.fileConfig("log_config.ini")
logging.info('Starting app')
# logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
# logging.getLogger("apscheduler.scheduler").setLevel(logging.WARNING)

import findspark
from pyspark.ml.feature import RFormula

findspark.init()

import flask
from pyspark.sql import SparkSession

import itertools

cont = itertools.count()


def get_spark_session():
    global cont
    return SparkSession. \
        builder. \
        master("spark://spark-master:7077"). \
        appName(str(int(next(cont)) % 4)). \
        config("spark.executor.memory", "14g"). \
        config("spark.executor.cores", "4"). \
        getOrCreate()


app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/get/', methods=['GET'])
def spark_test():
    global registry, fail_response_count, success_response_count, process_time_summary
    spark = get_spark_session()
    sample = None
    try:
        path = f"/opt/workspace/data/g2.csv"
        df = spark.read.csv(path, header=True)

        formula = RFormula(
            formula="clicked ~ country_code1 + hour",
            featuresCol="features",
            labelCol="label"
        )
        output = formula.fit(df).transform(df)
        sample = output.select("features", "label").head(5)
        return f"<h1>Sample</h1><p>{sample}</p>"
    except Exception as e:
        return f"Some Exception Throwed : {sample} {e}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
