from datasets import load_dataset
import pandas as pd


class DatasetService:

    def load_hospice_dataset(self) -> pd.DataFrame:

        dataset = load_dataset(
            "csv",
            data_files="hf://datasets/HHS-Official/hospice-enrollments/data/dataset.csv",
            encoding="cp1252"
        )

        df = dataset["train"].to_pandas()

        df.columns = [
            column.strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
            for column in df.columns
        ]

        return df