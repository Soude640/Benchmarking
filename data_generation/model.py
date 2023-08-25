import random
from abc import ABC
from typing import List

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE



class AbstractModel(ABC):
    def __init__(self):
        self.trained = False

    def train(self, df: pd.DataFrame):
        self.trained = True

    def new_population(self) -> pd.DataFrame:
        if self.trained:
            return pd.DataFrame()

        raise RuntimeError('no dataset has been trained!')


class RandomModel(AbstractModel):
    """
    This model generates each row by choosing a random sample of all unique data in that column.
    """

    def __init__(self, count: int = None):
        super().__init__()
        self.uniq_vals: List[List] = list()
        self.cols: List[str] = list()
        self.count = count

    def train(self, df: pd.DataFrame):
        super().train(df)

        self._extract_cols(df)
        self._extract_uniq_col_values(df)
        self._extract_count(df)

    def new_population(self) -> pd.DataFrame:
        super(RandomModel, self).new_population()

        result = []
        for i in range(self.count):
            result.append([
                random.choice(col_uniq) for col_uniq in self.uniq_vals
            ])

        return pd.DataFrame(result, columns=self.cols)

    def _extract_cols(self, df: pd.DataFrame):
        self.cols = list(df.columns)

    def _extract_uniq_col_values(self, df: pd.DataFrame):
        for col in df:
            self.uniq_vals.append(list(df[col].unique()))

    def _extract_count(self, df: pd.DataFrame):
        if self.count is None:
            self.count = df.shape[0]


class WeightedRandomModel(AbstractModel):
    """
    This model generates each row by choosing a weighted random sample of all data in that column.
    """

    def __init__(self, count: int = None):
        super().__init__()
        self.cols: List[str] = list()
        self.count = count
        self.df = None

    def train(self, df: pd.DataFrame):
        super().train(df)

        self.df: pd.DataFrame = df
        self._extract_cols(df)
        self._extract_count(df)

    def new_population(self) -> pd.DataFrame:
        super(WeightedRandomModel, self).new_population()

        result = []
        for i in range(self.count):
            row = []
            for j in self.df:
                row.append(list(self.df[j].sample(n=1))[0])
            result.append(row)

        return pd.DataFrame(result, columns=self.cols)

    def _extract_cols(self, df: pd.DataFrame):
        self.cols = list(df.columns)

    def _extract_count(self, df: pd.DataFrame):
        if self.count is None:
            self.count = df.shape[0]


class SmoteModel(AbstractModel):
    """
    This model uses the SMOTE oversampling method of imblearn.
       used for imbalanced classes in classification tasks.
    """

    def __init__(self):
        super().__init__()
        self.cols: List[str] = list()
        self.model = None
        self.X = None
        self.Y = None

    def train(self, df: pd.DataFrame):
        super().train(df)

        self._check_types(df)
        self._extract_cols(df)
        self._create_model()
        self._extract_x_y(df)

    def new_population(self) -> pd.DataFrame:
        super().new_population()

        x_train_smote, y_train_smote = self.model.fit_resample(self.X, self.Y)
        combined_array = np.column_stack((x_train_smote, y_train_smote))
        result = pd.DataFrame(combined_array, columns=self.cols)

        return result

    def _extract_cols(self, df: pd.DataFrame):
        self.cols = list(df.columns)

    def _create_model(self):
        self.model = SMOTE(sampling_strategy='auto', random_state=42)

   
