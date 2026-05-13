import pandas as pd
from library.src.artifact_types import Data, Model, Configuration, Report, Status, Documentation

class DataTabular(Data):
    def __init__(self, filepath, platform: str, product_name: str):
        super().__init__(filepath, platform, product_name)
    
    def load_dataset(self):
        return pd.read_csv(self.filepath)
    
    def log_dataset(self, dataset):
        if self.filetype == "csv":
            dataset.to_csv(self.filepath, index=False)
        elif self.filetype == "json":
            dataset.to_json(self.filepath)
        else:
            dataset.to_parquet(self.filepath)

