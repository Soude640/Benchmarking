import re
from os.path import getsize
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import numpy as np
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
    file_size_bytes = getsize(input_path)
    desired_size = convert_size_to_bytes(size)
    df = pd.read_csv(input_path)

    while file_size_bytes < desired_size - 10000:
        potential_target = None
        max_unique_values = 0
        max_correlation = 0.0

    
        
        target_type = df.iloc[:, -1].dtype
        feature_types = df.iloc[:, :-1].dtype
                
       if target_type=="object":
            # Use SmoteModel for categorical values
            model = SmoteModel()
        else:
            # Use RandomModel or WeightedRandomModel for int and float target values
            if target_type in [np.int32, np.int64, np.float64]:
                model = WeightedRandomModel()
            else:
                model = RandomModel()

        
        if potential_target is None:
            raise Exception("No suitable target column found in the dataset")

        feature_columns = [col for col in df.columns if col != potential_target]
        data = pd.concat([df[feature_columns], df[potential_target]], axis=1)
        
        target_type = df[potential_target].dtype
        if target_type == "object":
                model = SmoteModel()
            else:
                model = WeightedRandomModel()
        else:
            model = RandomModel()

        model.train(data)
        result = model.new_population()

        result.to_csv(output_path, index=False)
        df = pd.read_csv(output_path)
        file_size_bytes = getsize(output_path)

        print(f'file size become {file_size_bytes}')

    sampling_file(output_path, output_path, file_size_bytes, desired_size)

def main():
    fix_size("input.csv", "output.csv", "5Mb", label_encode=True)

if __name__ == '__main__':
    main()
