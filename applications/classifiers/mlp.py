

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

import xgboost as xgb

clf = xgb.XGBClassifier(
    n_estimators=5,
    max_depth=9,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    missing=-999,
    random_state=2000
)

from pyspark.ml.tuning import ParamGridBuilder, CrossValidator

from pyspark.ml.evaluation import MulticlassClassificationEvaluator



evaluator = MulticlassClassificationEvaluator(metricName="accuracy")

crossval = CrossValidator(estimator=xgb,
                          estimatorParamMaps=[10,5,20],
                          evaluator=evaluator,
                          numFolds=5)

from pyspark.ml import Pipeline



# Build the pipeline
pipeline = Pipeline(stages=[xgb])

model = pipeline.fit(train_df)



xgboost_model_doc = xgb(featuresCol="features", labelCol="label")

mlp_model = mlp.fit(train_df)

pred_df = mlp_model.transform(test_df)
pred_df.select('Id','features','label','rawPrediction','probability','prediction').show(5)

evaluator = MulticlassClassificationEvaluator(labelCol = 'label', predictionCol = 'prediction', metricName = 'accuracy')
mlpacc = evaluator.evaluate(pred_df)
mlpacc




