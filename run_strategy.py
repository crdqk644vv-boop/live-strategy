import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

# =========================
# CONFIG
# =========================
SYMBOL = "BTC-USD"
START = "2017-01-01"
FAST_MA = 50
SLOW_MA = 200
DONCHIAN_N = 20

# =========================
# DATA
# =========================
df = yf.download(SYMBOL, start=START, interval="1d", auto_adjust=True)

df = df.dropna()
df["date"] = df.index

# =========================
# INDICATORS
# =========================
df["fast_ma"] = df["Close"].rolling(FAST_MA).mean()
df["slow_ma"] = df["Close"].rolling(SLOW_MA).mean()

df["don_high"] = df["High"].rolling(DONCHIAN_N).max()
df["don_low"] = df["Low"].rolling(DONCHIAN_N).min()

# =========================
# REGIME (BULL / BEAR)
# =========================
df["regime"] = np.where(df["Close"] > df["slow_ma"], "BULL", "BEAR")

# =========================
# SIGNAL LOGIC (BASE STRATEGY)
# =========================
df["signal"] = "HOLD"

# Entry: trend up + breakout
entry_cond = (
    (df["regime"] == "BULL") &
    (df["Close"] > df["don_high"].shift(1))
)

# Exit: trend broken
exit_cond = (
    (df["Close"] < df["fast_ma"]) |
    (df["regime"] == "BEAR")
)

df.loc[entry_cond, "signal"] = "ENTER"
df.loc[exit_cond, "signal"] = "EXIT"

# =========================
# POSITION STATE MACHINE
# =========================
position = 0
positions = []

for i in range(len(df)):
    sig = df.iloc[i]["signal"]

    if position == 0 and sig == "ENTER":
        position = 1
    elif position == 1 and sig == "EXIT":
        position = 0

    positions.append(position)

df["position"] = positions

# =========================
# LEVERAGE OVERLAY (OPTIONAL)
# =========================
def leverage_for_row(row):
    if row["regime"] == "BULL" and row["position"] == 1:
        return 2.0
    return 1.0

df["target_leverage"] = df.apply(leverage_for_row, axis=1)

# =========================
# LIVE OUTPUT (SENASTE DAGEN)
# =========================
last = df.iloc[-1]

print("===================================")
print("LIVE STRATEGY DECISION")
print("===================================")
print("As of date      :", last["date"].date())
print("Price           :", round(last["Close"], 2))
print("Regime          :", last["regime"])
print("Signal today    :", last["signal"])
print("Position        :", "LONG" if last["position"] == 1 else "FLAT")
print("Target leverage :", last["target_leverage"])
print("===================================")
