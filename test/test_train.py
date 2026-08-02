from src.train import evaluate_row


def test_elite_customer():
    row = {
        "Auto Renew": "Yes",
        "Subscription Count": 30,
        "Subscription Term": "Monthly"
    }

    assert evaluate_row(row) == "Elite"


def test_normal_customer():
    row = {
        "Auto Renew": "No",
        "Subscription Count": 5,
        "Subscription Term": "Monthly"
    }

    assert evaluate_row(row) == "Normal"