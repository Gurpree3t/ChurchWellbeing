import pandas as pd

from config import *


def church_statistics(df):

    total_steps = pd.to_numeric(
        df[COL_STEPS],
        errors="coerce"
    ).fillna(0).sum()

    total_members = (
        df[COL_NAME]
        .astype(str)
        .str.upper()
        .nunique()
    )

    return {
        "members": total_members,
        "steps": int(total_steps)
    }