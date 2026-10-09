"""Run from the repo root: python -m pytest app"""
import alerts
import lotsize


def test_lot_size_cases_from_the_course():
    assert lotsize.lots(10, 20, 10.0)[0] == 0.05   # EURUSD, $100 account, 10%, 20 pips
    assert lotsize.lots(20, 25, 10.0)[0] == 0.08   # GBPUSD, $20 risk, 25 pips


def test_yen_pair_uses_the_yen_conversion():
    pip_value = 1000 / 147                         # one pip of 1 lot = 1000 JPY, in USD at 147
    assert lotsize.lots(50, 30, pip_value)[0] == 0.24  # rounded down from 0.245


def test_lot_is_rounded_down_and_never_below_the_minimum():
    assert lotsize.lots(10, 33, 10.0)[0] == 0.03   # raw 0.0303
    lot, raw = lotsize.lots(1, 50, 10.0)           # raw 0.002
    assert lot == 0.01 and raw < 0.01


def test_pip_size():
    assert lotsize.pip_size("JPY") == 0.01 and lotsize.pip_size("USD") == 0.0001


def test_alert_fires_on_a_cross_only():
    assert alerts.crossed(1.30, 1.32, 1.31) and alerts.crossed(1.32, 1.30, 1.31)
    assert alerts.crossed(1.30, 1.31, 1.31)        # lands exactly on the level
    assert not alerts.crossed(1.32, 1.33, 1.31)    # already past it
    assert not alerts.crossed(None, 1.31, 1.31)    # first reading never fires
