import re
from os.path import getsize

import pandas as pd
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
import numpy as np

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


def fix_size(input_path: str, output_path: str, size: str):
    # May raise OSError if file is inaccessible.
    file_size_bytes = getsize(input_path)

    desired_size = convert_size_to_bytes(size)
    df = pd.read_csv(input_path)

    for type_ in df.dtypes:
        if type_ not in (np.int32, np.int64, np.float64):
            print(f"bad data type {type_}. only support int and float")
            return

    while file_size_bytes < desired_size - 1000:
        y = df.iloc[:, -1:]
        X = df.iloc[:, :-1]

        # split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)

        # apply SMOTE to the training set
        smote = SMOTE(random_state=42)
        X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

        # combine the original training set and the new samples generated by SMOTE
        X_train_combined = np.vstack((X_train, X_train_smote))
        y_train_combined = np.concatenate((y_train, y_train_smote))

        combined_array = np.column_stack((X_train_combined, y_train_combined))

        # combine two arrays into a dataframe and print it out
        result = pd.DataFrame(combined_array, columns=list(df.columns))

        result.to_csv(output_path, index=False)
        df = pd.read_csv(output_path)
        file_size_bytes = getsize(output_path)

        print(f'file size become {file_size_bytes}')

    sampling_file(output_path, output_path, file_size_bytes, desired_size)


def main():
    fix_size("sample.csv", "out.csv", "2Mb")


if __name__ == '__main__':
    main()
