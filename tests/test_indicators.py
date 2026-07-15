import pandas as pd

from app.modules.indicators import calculate_rsi


def test_rsi_stays_in_valid_range():
    frame = pd.DataFrame(
        {"Fechamento": [10, 11, 10, 12, 11, 13, 12, 14, 13, 15, 14, 16, 15, 17, 16]}
    )
    result = calculate_rsi(frame, period=5)
    assert "RSI" in result.columns
    assert result["RSI"].dropna().between(0, 100).all()


def test_rsi_preserves_input_rows():
    frame = pd.DataFrame({"Fechamento": [10, 11, 12, 11, 13, 12]})
    assert len(calculate_rsi(frame, period=3)) == len(frame)
