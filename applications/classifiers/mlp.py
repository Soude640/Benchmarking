




from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


def do(path: str, spark: SparkSession):
    # load data file.
    df = spark.read.csv(path, header=True, inferSchema=True)
    vectorAssembler = VectorAssembler(inputCols=['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'],
                                      outputCol='features')
    v_iris_df = vectorAssembler.transform(df)

    indexer = StringIndexer(inputCol='Species', outputCol='label')
    i_v_iris_df = indexer.fit(v_iris_df).transform(v_iris_df)

    i_v_iris_df.select('Species', 'label').groupBy('Species', 'label').count().show()
    splits = i_v_iris_df.randomSplit([0.6, 0.4], 1)
    train_df = splits[0]
    test_df = splits[1]

    layers = [4, 5, 5, 3]
    mlp = MultilayerPerceptronClassifier(layers=layers, seed=1)
    mlp_model = mlp.fit(train_df)
    pred_df = mlp_model.transform(test_df)

    evaluator = MulticlassClassificationEvaluator(labelCol='label', predictionCol='prediction', metricName='accuracy')
    mlpacc = evaluator.evaluate(pred_df)
    return mlpacc
