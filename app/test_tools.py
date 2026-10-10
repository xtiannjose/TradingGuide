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


def test_backtest_simulate_stop_target_and_same_candle_loss():
    import backtest
    import pandas as pd
    ny = "America/New_York"

    def m15(rows):
        df = pd.DataFrame(rows, columns=["open", "high", "low", "close"])
        df["ny"] = pd.date_range("2026-01-05 02:00", periods=len(df), freq="15min", tz=ny)
        return df
    plan = {"stop": 1.0950, "target": 1.1100}
    after = pd.Timestamp("2026-01-05 02:00").to_pydatetime()
    assert backtest.simulate(plan, "buy", after, m15([(1.1000, 1.1010, 1.0990, 1.1005), (1.1005, 1.1105, 1.1000, 1.1100)]))[0] == "win"
    assert backtest.simulate(plan, "buy", after, m15([(1.1000, 1.1010, 1.0940, 1.0960)]))[:2] == ("loss", -1.0)
    assert backtest.simulate(plan, "buy", after, m15([(1.1000, 1.1110, 1.0940, 1.1000)]))[:2] == ("loss", -1.0)  # both: loss
    assert backtest.simulate(plan, "buy", after, m15([(1.1000, 1.1010, 1.0990, 1.1005)]))[0] == "open"


def test_params_merge_keeps_defaults_and_overrides():
    import params
    base = {"a": {"x": 1, "y": 2}, "b": 3}
    assert params.merge(base, {"a": {"y": 9}, "c": 4}) == {"a": {"x": 1, "y": 9}, "b": 3, "c": 4}
    cfg = params.load(user=False)
    assert cfg["aoi"]["cluster_pips"] == 35 and cfg["time"]["days"] == [0, 1, 2]


def test_telegram_is_off_unless_configured(monkeypatch):
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    monkeypatch.delenv("TG_CHAT_ID", raising=False)
    assert alerts.telegram("x") is False   # nothing set: nothing is sent


def test_alert_fires_on_a_cross_only():
    assert alerts.crossed(1.30, 1.32, 1.31) and alerts.crossed(1.32, 1.30, 1.31)
    assert alerts.crossed(1.30, 1.31, 1.31)        # lands exactly on the level
    assert not alerts.crossed(1.32, 1.33, 1.31)    # already past it
    assert not alerts.crossed(None, 1.31, 1.31)    # first reading never fires
