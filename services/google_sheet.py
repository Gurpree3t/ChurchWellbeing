import pandas as pd

from config import GOOGLE_SHEET_URL


def load_google_sheet():

    df = pd.read_csv(GOOGLE_SHEET_URL)

    return df