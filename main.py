import re
from os.path import getsize

import pandas as pd
from sklearn.preprocessing import LabelEncoder

from model import WeightedRandomModel, SmoteModel, RandomModel

convert_map = {
    "b": 1,
    "kb": 1024,
    "mb": 1024 * 1024,
    "gi": 1024 * 1024 * 1024,
}


def convert_size_to_bytes(desired_size: str) -> float:
    split = re.split("(kb|Kb|KB|mb|Mb|MB|gi|Gi|GI|b|B)", desired_size)
    number, unit = float(split[0]), str(split[1]).lower()

    if unit not in convert_map:
        raise Exception(f"bad format desired size. {unit} not known")

    return number * convert_map[unit]


def sampling_file(file_path: str, output_path: str, file_size: float, desired_size: float):
    df = pd.read_csv(file_path)
    sample_percent = desired_size / file_size

    sampled = df.sample(frac=sample_percent, ignore_index=True)

    print(f'sampling frac: {sample_percent}, {len(df)} becomes {len(sampled)}')

    sampled.to_csv(output_path, index=False)


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

        print(f'file size become {file_size_bytes}')

    sampling_file(output_path, output_path, file_size_bytes, desired_size)


def main():
    fix_size("Iris.csv", "out.csv", "5Mb", label_encode=True)


if __name__ == '__main__':
    main()
