




import findspark
findspark.init()
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('pyspark-ml').getOrCreate()

iris_df = spark.read.csv('/content/sample_data/Iris.csv', header=True, inferSchema=True)
iris_df.show(5)

from pyspark.sql.functions import *
from pyspark.ml.feature import VectorAssembler, StringIndexer

vectorAssembler = VectorAssembler(inputCols = ['SepalLengthCm','SepalWidthCm','PetalLengthCm','PetalWidthCm'], outputCol = 'features')
v_iris_df = vectorAssembler.transform(iris_df)
v_iris_df.show(5)

indexer = StringIndexer(inputCol = 'Species', outputCol = 'label')
i_v_iris_df = indexer.fit(v_iris_df).transform(v_iris_df)
i_v_iris_df.show(5)

i_v_iris_df.select('Species','label').groupBy('Species','label').count().show()

splits = i_v_iris_df.randomSplit([0.6,0.4],1)
train_df = splits[0]
test_df = splits[1]
train_df.count(), test_df.count(), i_v_iris_df.count()

from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

layers = [4,5,5,3]

mlp = MultilayerPerceptronClassifier(layers = layers, seed = 1)

mlp_model = mlp.fit(train_df)

pred_df = mlp_model.transform(test_df)
pred_df.select('Id','features','label','rawPrediction','probability','prediction').show(5)

evaluator = MulticlassClassificationEvaluator(labelCol = 'label', predictionCol = 'prediction', metricName = 'accuracy')
mlpacc = evaluator.evaluate(pred_df)
mlpacc

