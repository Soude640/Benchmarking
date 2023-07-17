from pyspark.sql import SparkSession
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import GridSearchCV
from pyspark.sql import Window, SparkSession

from sklearn.model_selection import train_test_split
import xgboost as xgb



def do(path: str, spark: SparkSession):
    # load data file.
    iris = load_iris()
    X, y = iris.data, iris.target
    train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.3, random_state=1)
    parameters = {
        'max_depth': [5, 10, 15],
        'learning_rate': [0.01, 0.02],
        'n_estimators': [500, 1000],
    }
    xlf = xgb.XGBClassifier(max_depth=10,
                            learning_rate=0.01,
                            n_estimators=2000,
                            silent=True,
                            objective='multi:softmax',
                            num_class=3,
                            nthread=-1,
                            gamma=0,
                            min_child_weight=1,
                            max_delta_step=0,
                            subsample=0.85,
                            colsample_bytree=0.7,
                            colsample_bylevel=1,
                            reg_alpha=0,
                            reg_lambda=1,
                            scale_pos_weight=1,
                            seed=0,
                            missing=1)
    gs = GridSearchCV(xlf, param_grid=parameters, scoring='accuracy', cv=3)
    gs.fit(train_x, train_y)

    print("Best score: %0.3f" % gs.best_score_)
    print("Best parameters set: %s" % gs.best_params_)

    # make predictions for test data
    y_pred = gs.predict(test_x)
    predictions = [round(value) for value in y_pred]
    # evaluate predictions
    accuracy = accuracy_score(test_y, predictions)
    return "Accuracy: %.2f%%" % (accuracy * 100.0)
