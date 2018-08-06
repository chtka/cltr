import pandas as pd

class ClinicalTrialsPostProcessor:
    def process_and_load_df(self, filepath_or_buffer):
        df = pd.read_json(filepath_or_buffer, orient='records', lines=True)

        