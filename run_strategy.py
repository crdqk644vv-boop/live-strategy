print("🔥 RUNNING NEW CODE VERSION 999 🔥")
import pandas as pd
import numpy as np
import yfinance as yf
import time

print("VERSION: FINAL-STABLE", flush=True)

# ------------------
# CONFIG
# ------------------
SYMBOL = "BTC-USD"
START = "2017-01-01"

# ------------------
# FETCH DATA
# ------------------
time.sleep(5)

df = yf.download(
    SYMBOL,
    start=START,
    interval="1d",
    auto_adjust=True,
    progress=False
)

# platta till kolumner (viktigt)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# säkerställ index + dropna
df = df.dropna().reset_index()

# ------------------
# EXTRAHERA SERIES (KRITISKT)
# ------------------
close = df["Close"].astype(float)
high  = df["High"].astype(float)

# ------------------
# INDIKATORER (SERIES)
# ------------------
fast_ma = close.rolling(50).mean()
slow_ma = close.rolling(200).mean()
don_high = high.rolling(20).max()

# kombinera till ny df (alla Series har samma index)
data = pd.DataFrame({
    "Date": df["Date"],
    "Close": close,
    "fast_ma": fast_ma,
    "slow_ma": slow_ma,
    "don_high": don_high
}).dropna().reset_index(drop=True)

# ------------------
# REGIME (NU OMÖJLIGT ATT FAILA)
# ------------------
data["regime"] = np.where(
    data["Close"].values > data["slow_ma"].values,
    "BULL",
    "BEAR"
)

# ------------------
# SIGNALER
# ------------------
close_vals = data["Close"].to_numpy()
don_vals   = data["don_high"].shift(1).to_numpy()
fast_vals  = data["fast_ma"].to_numpy()

signals = np.array(["HOLD"] * len(data), dtype=object)

for i in range(len(data)):
    if data.loc[i, "regime"] == "BULL" and close_vals[i] > don_vals[i]:
        signals[i] = "ENTER"
    elif close_vals[i] < fast_vals[i] or data.loc[i, "regime"] == "BEAR":
        signals[i] = "EXIT"

data["signal"] = signals

data.loc[
    (data["Close"] < data["fast_ma"]) |
    (data["regime"] == "BEAR"),
    "signal"
] = "EXIT"

# ------------------
# POSITION STATE
# ------------------
position = 0
positions = []

for sig in data["signal"]:
    if position == 0 and sig == "ENTER":
        position = 1
    elif position == 1 and sig == "EXIT":
        position = 0
    positions.append(position)

data["position"] = positions

# ------------------
# OUTPUT (LIVE)
# ------------------
last = data.iloc[-1]

print("===== LIVE STRATEGY =====")
print("DATE:", last["Date"].date())
print("PRICE:", round(last["Close"], 2))
print("REGIME:", last["regime"])
print("SIGNAL:", last["signal"])
print("POSITION:", "LONG" if last["position"] == 1 else "FLAT")
print("=========================")
