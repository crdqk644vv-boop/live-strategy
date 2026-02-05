import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import time

print("VERSION: FIX-MULTIINDEX", flush=True)

# -----------------------
# CONFIG
# -----------------------
SYMBOL = "BTC-USD"
START = "2017-01-01"

# -----------------------
# FETCH DATA
# -----------------------
time.sleep(5)
df = yf.download(
    SYMBOL,
    start=START,
    interval="1d",
    auto_adjust=True,
    progress=False
)

# 🔴 VIKTIG FIX: platta till kolumner
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.dropna().reset_index()

# -----------------------
# INDICATORS
# -----------------------
df["fast_ma"] = df["Close"].rolling(50).mean()
df["slow_ma"] = df["Close"].rolling(200).mean()
df["don_high"] = df["High"].rolling(20).max()

df = df.dropna().reset_index(drop=True)

# -----------------------
# REGIME
# -----------------------
df["regime"] = np.where(
    df["Close"].to_numpy() > df["slow_ma"].to_numpy(),
    "BULL",
    "BEAR"
)

# -----------------------
# SIGNALS
# -----------------------
df["signal"] = "HOLD"

df.loc[
    (df["regime"] == "BULL") &
    (df["Close"] > df["don_high"].shift(1)),
    "signal"
] = "ENTER"

df.loc[
    (df["Close"] < df["fast_ma"]) |
    (df["regime"] == "BEAR"),
    "signal"
] = "EXIT"

# -----------------------
# POSITION STATE
# -----------------------
position = 0
positions = []

for sig in df["signal"]:
    if position == 0 and sig == "ENTER":
        position = 1
    elif position == 1 and sig == "EXIT":
        position = 0
    positions.append(position)

df["position"] = positions

# -----------------------
# OUTPUT (LIVE)
# -----------------------
last = df.iloc[-1]

print("===== LIVE STRATEGY =====")
print("DATE:", last["Date"].date())
print("PRICE:", round(last["Close"], 2))
print("REGIME:", last["regime"])
print("SIGNAL:", last["signal"])
print("POSITION:", "LONG" if last["position"] == 1 else "FLAT")
print("=========================")
