"""Lot size calculator (docs/ANALYSIS-SPEC.md section 8.2). Analysis aid only: places no orders.

python app/lotsize.py EURUSD --stop 25 [--risk 1.0] [--balance 1000]

The balance defaults to the logged-in MT5 account and is never saved. Without --risk it prints
a small table of risk levels to choose from. The pip value comes from the broker's own
conversion, so a yen or cross pair is converted to the account currency correctly.
"""
import argparse
import math

import candles


def pip_size(quote_ccy):
    return 0.01 if quote_ccy == "JPY" else 0.0001


def lots(risk_amount, stop_pips, pip_value, step=0.01, vmin=0.01, vmax=100.0):
    """Lots that risk `risk_amount` over `stop_pips`, rounded down to the broker's step.

    pip_value = value of one pip for one lot, in the account currency.
    Returns (lots, raw). raw is the unrounded size; lots is vmin when raw is below it.
    """
    raw = risk_amount / (stop_pips * pip_value)
    n = math.floor(raw / step + 1e-9)
    return round(min(max(n * step, vmin), vmax), 8), raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("symbol")
    ap.add_argument("--stop", type=float, required=True, help="stop distance in pips")
    ap.add_argument("--risk", type=float, help="percent of balance to risk; omit for a table")
    ap.add_argument("--balance", type=float, help="account balance; default is the MT5 account")
    a = ap.parse_args()

    cfg = candles.settings()
    sym = a.symbol + cfg["data"]["symbol_suffix"]
    mt5 = candles.connect()
    try:
        mt5.symbol_select(sym, True)
        info, acc = mt5.symbol_info(sym), mt5.account_info()
        if info is None or not info.trade_tick_value:
            raise SystemExit(f"No price data for {sym} yet (market closed and never opened?).")
        balance = a.balance if a.balance is not None else acc.balance
        ccy = acc.currency
    finally:
        mt5.shutdown()

    pip_value = info.trade_tick_value * pip_size(info.currency_profit) / info.trade_tick_size
    risks = [a.risk] if a.risk else [0.25, 0.5, 1.0, 2.0]
    print(f"{sym}, stop {a.stop:g} pips, balance {balance:,.2f} {ccy}, one pip = {pip_value:.2f} {ccy} per lot")
    print(f"{'risk %':>7} {'risk amount':>13} {'lots':>7}   account after 5 / 10 stops in a row")
    for r in risks:
        amount = balance * r / 100
        n, raw = lots(amount, a.stop, pip_value, info.volume_step, info.volume_min, info.volume_max)
        note = "  <- smallest lot already risks more" if raw < info.volume_min else ""
        print(f"{r:>7g} {amount:>9,.2f} {ccy} {n:>7.2f}   "
              f"{(1 - r / 100) ** 5:.1%} / {(1 - r / 100) ** 10:.1%} of balance{note}")
    print("Break-even win rate at 1:2 reward to risk is 33%; at 1:3 it is 25% (before costs).")


if __name__ == "__main__":
    main()
