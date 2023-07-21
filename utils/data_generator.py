import logging

from celery import Task
from experiment.celery import app
from os.path import getsize

import pandas as pd
from sklearn.preprocessing import LabelEncoder

from lab.models import Data, convert_size_to_bytes
from utils.model import RandomModel


def sampling_file(file_path: str, output_path: str, file_size: float, desired_size: float):
    df = pd.read_csv(file_path)
    sample_percent = desired_size / file_size

    sampled = df.sample(frac=sample_percent, ignore_index=True)

    print(f'sampling frac: {sample_percent}, {len(df)} becomes {len(sampled)}')

    sampled.to_csv(output_path, index=False)
    data_obj = Data.objects.get(sample_data=file_path.split('/')[-1])
    data_obj.status = Data.GENERATED
    data_obj.save()


def fix_size(input_path: str, output_path: str, size: str, label_encode: bool = False):
    """
    :param input_path:
    :param output_path:
    :param size:
    :param label_encode: if true do not use smote model
    :return:
    """
    # May raise OSError if file is inaccessible.
    file_size_bytes = getsize(input_path)

    desired_size = convert_size_to_bytes(size)
    df = pd.read_csv(input_path)

    while file_size_bytes < desired_size - 10000:
        encoders = {}
        obj_list = df.select_dtypes(include="object").columns
        if label_encode:
            for feat in obj_list:
                le = LabelEncoder()
                le.fit(df[feat])
                encoders[feat] = le
                df[feat] = le.transform(df[feat].astype(str))

        model = RandomModel()

        model.train(df)
        result = pd.concat([df, model.new_population()], ignore_index=True)

        if label_encode:
            for feat in obj_list:
                le = encoders[feat]
                result[feat] = le.inverse_transform(result[feat])

        result.to_csv(output_path, index=False)
        df = pd.read_csv(output_path)
        file_size_bytes = getsize(output_path)
        data_obj = Data.objects.get(sample_data=input_path.split('/')[-1])
        data_obj.status = Data.PENDING
        data_obj.save()

        print(f'file size become {file_size_bytes}')

    sampling_file(output_path, output_path, file_size_bytes, desired_size)


class DataGenerator(Task):
    name = 'Data Generator'
    description = 'Data Generator'
    ignore_result = True

    def run(self, *args, **kwargs):
        try:
            desired_size = str(kwargs["desired_size"])
            sample_data = str(kwargs["file"])
            fix_size(sample_data, sample_data, desired_size, label_encode=False)
        except Exception as e:
            logging.error(e)


data_generator = DataGenerator()
app.register_task(data_generator)
