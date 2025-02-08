# Task 1: Minimal Reporting Tool
import sqlite3
import pandas as pd
from fastapi import FastAPI, HTTPException
from datetime import datetime
import pytz


## Import trades.sqlite
conn = sqlite3.connect("trades.sqlite")

df = pd.read_sql_query("SELECT id, quantity, price, side, strategy FROM epex_12_20_12_13", conn)

conn.close()

print(df)

## Task 1.1:
### Write a function that computes the total buy volume for flex power, another that computes the total sell volume.

def compute_total_buy_volume(*args, **kwargs) -> float:
    buy_volume = df[df["side"] == "buy"]["quantity"].sum()
    return buy_volume

def compute_total_sell_volume(*args, **kwargs) -> float:
    sell_volume = df[df["side"] == "sell"]["quantity"].sum()
    return sell_volume

print("Total buy volume: ", compute_total_buy_volume())
print("Total sell volume: ", compute_total_sell_volume())

## Task 1.2:
### Write a function that computes the PnL (profit and loss) of each strategy in euros. It's defined as the sum of the incomes realized with each trade.

def compute_pnl(strategy_id: str, *args, **kwargs) -> float:
    df_strat = df[df["strategy"] == strategy_id].copy()
    if df_strat.empty:
        return 0

    df_strat["value"] = df_strat["quantity"] * df_strat["price"]

    df_strat_income = df_strat[df_strat["side"] == "sell"]["value"].sum()
    df_strat_expense = df_strat[df_strat["side"] == "buy"]["value"].sum()
    pnl = df_strat_income - df_strat_expense
    return pnl

print("PnL for strategy 1: ", compute_pnl("strategy_1"))
print("PnL for strategy 2: ", compute_pnl("strategy_2"))
print("PnL for strategy 3: ", compute_pnl("strategy_3"))

## Task 1.3:
### Expose the function defined in the second task as an entrypoint of a web application. 

### To be honest, I have never done this kind of task (like exposing a function as an APi or working with APIs in general). I hope that this is vaguely what you are looking for...?

app = FastAPI(
    title="Energy Trading API",
    version="1.0.0",
    description="API to calculate the Profit and Loss (PnL) for energy trading strategies."
)

@app.get("/pnl/{strategy_id}", response_model=dict)
def get_pnl(strategy_id: str):
    """API endpoint to retrieve the PnL for a specific strategy."""
    pnl = compute_pnl(strategy_id)

    response = {
        "strategy": strategy_id,
        "value": round(pnl, 2),  # Round PnL to 2 decimal places
        "unit": "euro",
        "capture_time": datetime.now(pytz.timezone("Europe/Berlin")).isoformat() + "Z"  # ISO 8601 timestamp
    }

    return response

