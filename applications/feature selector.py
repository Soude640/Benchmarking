import logging

from pyspark.ml.feature import RFormula
from pyspark.sql import SparkSession


def do(path: str, spark: SparkSession):
    df = spark.read.csv(path, header=True)
    logging.info(f"data frame: {df.head(2)}")
    formula = RFormula(
        formula="clicked ~ country_code1 + hour",
        featuresCol="features",
        labelCol="label"
    )
    output = formula.fit(df).transform(df)
    sample = output.select("features", "label").head(5)
    return sample
