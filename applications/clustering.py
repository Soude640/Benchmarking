

import findspark
import pandas as pd
findspark.init()
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName('pyspark-ml').getOrCreate()
import pandas as pd
from sklearn.datasets import load_iris
from pyspark.sql import SparkSession
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.feature import PCA as PCAml

def do(path: str, spark: SparkSession):
    # load data file.
   df = spark.read.csv(path, header=True, inferSchema=True) 
   df_iris = load_iris(as_frame=True)

  pd_df_iris = pd.DataFrame(df_iris.data, columns = df_iris.feature_names)
  pd_df_iris['target'] = pd.Series(df_iris.target)

  spark_df_iris = spark.createDataFrame(pd_df_iris)
  spark_df_iris = spark_df_iris.drop("target")


  assemble=VectorAssembler(inputCols=[
  'sepal length (cm)',
   'sepal width (cm)',
   'petal length (cm)',
   'petal width (cm)'],outputCol = 'iris_features')

  assembled_data=assemble.transform(spark_df_iris)



 silhouette_scores=[]
 evaluator = ClusteringEvaluator(featuresCol='iris_features', \
 metricName='silhouette', distanceMeasure='squaredEuclidean')

 for K in range(2,11):

      KMeans_=KMeans(featuresCol='iris_features', k=K)

      KMeans_fit=KMeans_.fit(assembled_data)

      KMeans_transform=KMeans_fit.transform(assembled_data) 

     evaluation_score=evaluator.evaluate(KMeans_transform)

     silhouette_scores.append(evaluation_score)


   KMeans_=KMeans(featuresCol='iris_features', k=3) 
   KMeans_Model=KMeans_.fit(assembled_data)
   KMeans_Assignments=KMeans_Model.transform(assembled_data)


   pca = PCAml(k=2, inputCol="iris_features", outputCol="pca")
   pca_model = pca.fit(assembled_data)
   pca_transformed = pca_model.transform(assembled_data)

   import numpy as np
   x_pca = np.array(pca_transformed.rdd.map(lambda row: row.pca).collect())

   cluster_assignment = np.array(KMeans_Assignments.rdd.map(lambda row: row.prediction).collect()).reshape(-1,1)

   import seaborn as sns
   import matplotlib.pyplot as plt

   pca_data = np.hstack((x_pca,cluster_assignment))

  pca_df = pd.DataFrame(data=pca_data, columns=("1st_principal", "2nd_principal","cluster_assignment"))
  sns.FacetGrid(pca_df,hue="cluster_assignment", height=6).map(plt.scatter, '1st_principal', '2nd_principal' ).add_legend()
  return KMeans

