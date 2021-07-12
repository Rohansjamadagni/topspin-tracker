import pandas as pd

class VibrationCSV:
    def __init__(
        self,
        filename: str = None,
    ):
        self.filename = filename
        self.columns = ['start', 'stop']
        self.df = pd.DataFrame(self.columns)

        self.df.to_csv(filename)

    def write_list_to_csv(self, timestamp_list):
        temp_df = pd.DataFrame(timestamp_list, columns=self.columns)
        temp_df.to_csv(self.filename, mode='a', header=False)
