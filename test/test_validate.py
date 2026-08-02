import pandas as pd
from src.validate import validate_data


def test_validate_data_success():
    df = pd.DataFrame({
        "Auto Renew": ["Yes", "No"],
        "Subscription Count": [10, 20],
        "Subscription Term": ["Monthly", "Yearly"]
    })

    assert validate_data(df) is True