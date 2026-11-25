from pathlib import Path

import pandas as pd


class DatasetRepository:
    def __init__(self, csv_path: str | Path):
        self.csv_path = Path(csv_path)

    def load(self) -> pd.DataFrame:
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Dataset não encontrado: {self.csv_path}")
        return pd.read_csv(self.csv_path)
