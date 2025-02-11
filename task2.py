# Task 2: Data analysis and building a trading strategy

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_excel("analysis_task_data.xlsx")


# print(df.head())
print(df.columns)

# Task 2.1: 
# How much Wind/PV Power was forecasted to produced in German in 2021 [in MWh] on Day Ahead (da) and on Intraday (id).

df["Wind Day Ahead Forecast [in MWh]"] = df["Wind Day Ahead Forecast [in MW]"] * 0.25
df["PV Day Ahead Forecast [in MWh]"] = df["PV Day Ahead Forecast [in MW]"] * 0.25
df["Wind Intraday Forecast [in MWh]"] = df["Wind Intraday Forecast [in MW]"] * 0.25
df["PV Intraday Forecast [in MWh]"] = df["PV Intraday Forecast [in MW]"] * 0.25

# as the data runs from 2021-01-01 to 2021-12-31, we can just sum the MWh columns
wind_da_total = df["Wind Day Ahead Forecast [in MWh]"].sum()
wind_id_total = df["Wind Intraday Forecast [in MWh]"].sum()
pv_da_total = df["PV Day Ahead Forecast [in MWh]"].sum()
pv_id_total = df["PV Intraday Forecast [in MWh]"].sum()


print("Total Wind forcasteded Day Ahead: ", wind_da_total)
print("Total Wind forcasteded Intraday: ", wind_id_total)
print("Wind da - id: ", wind_da_total - wind_id_total)
print("Total PV forcasteded Day Ahead: ", pv_da_total)
print("Total PV forcasteded Intraday: ", pv_id_total)
print("PV da - id: ", pv_da_total - pv_id_total)

# Task 2.2: Show the average Wind/Solar production for 2021 over a 24h period for Intraday and Day Ahead (4 lines in one graph).

# average wind and pv production per hour
avg_wind_da_per_hour = df.groupby("hour")["Wind Day Ahead Forecast [in MWh]"].mean()
avg_pv_da_per_hour = df.groupby("hour")["PV Day Ahead Forecast [in MWh]"].mean()
avg_wind_id_per_hour = df.groupby("hour")["Wind Intraday Forecast [in MWh]"].mean()
avg_pv_id_per_hour = df.groupby("hour")["PV Intraday Forecast [in MWh]"].mean()

plt.figure(figsize=(12, 6))
plt.plot(avg_wind_da_per_hour, label="Wind Day Ahead Forecast [in MWh]")
plt.plot(avg_pv_da_per_hour, label="PV Day Ahead Forecast [in MWh]")
plt.plot(avg_wind_id_per_hour, label="Wind Intraday Forecast [in MWh]")
plt.plot(avg_pv_id_per_hour, label="PV Intraday Forecast [in MWh]")
plt.xlabel("Hour of the Day")
plt.ylabel("Average Forecast [in MWh]")
plt.title("Average Wind/PV Forecast for 2021 Over a 24h Period")
plt.legend()
plt.show()
plt.savefig("pics/average_forecast.png")

# Task 2.3: What was the average value [in EUR/MWh] for Wind/Solar Power in 2021 using the da forecast and using da h prices? Is the average value of Wind and PV higher or lower than the average da price? Why could it be higher/lower?

df["Wind Revenue [in EUR]"] = df["Wind Day Ahead Forecast [in MWh]"] * df["Day Ahead Price hourly [in EUR/MWh]"]
df["PV Revenue [in EUR]"] = df["PV Day Ahead Forecast [in MWh]"] * df["Day Ahead Price hourly [in EUR/MWh]"]

# Calculate the total value and total forecasted production
total_wind_revenue = df["Wind Revenue [in EUR]"].sum()
total_pv_revenue = df["PV Revenue [in EUR]"].sum()


# Calculate the average value in EUR/MWh
avg_wind_value_per_mwh = total_wind_revenue / wind_da_total
avg_pv_value_per_mwh = total_pv_revenue / pv_da_total

# Calculate the average day ahead price
avg_da_price = df["Day Ahead Price hourly [in EUR/MWh]"].mean()

print("Average Wind Value [in EUR/MWh]: ", avg_wind_value_per_mwh)
print("Average PV Value [in EUR/MWh]: ", avg_pv_value_per_mwh)
print("Average Day Ahead Price [in EUR/MWh]: ", avg_da_price)

print("The average value of Wind and PV is lower than the average day ahead price. I can think of some reasons for this: 1. there might be forcasting inaccuracies, that affect the price 2. the average day ahead price is calculated over all hours, while the average value of Wind and PV is calculated over the forecasted production (being a volume weighted average) 3. there might be issues with oversupply during certain hours. To asses these closer, I would need to look at the data in more detail.")

# Task 2.4: Find the Day with the highest renewable energy production and with the lowest renewable energy production in 2021. What was the average Day Ahead Price levels on these days? How do you explain the difference in prices?

# Calculate the total renewable energy production per day
df["Total Renewable Forecast [in MWh]"] = df["Wind Day Ahead Forecast [in MWh]"] + df["PV Day Ahead Forecast [in MWh]"]

daily_df = df.groupby(df["time"].dt.date).agg(
    total_renewable=("Total Renewable Forecast [in MWh]", "sum"),
    avg_da_price=("Day Ahead Price hourly [in EUR/MWh]", "mean"),
).reset_index()

# Find the day with the highest and lowest renewable energy production
max_day = daily_df[daily_df["total_renewable"] == daily_df["total_renewable"].max()]
min_day = daily_df[daily_df["total_renewable"] == daily_df["total_renewable"].min()]

print("Day with the highest renewable energy production: ", max_day["time"].values[0])
print("Total Renewable Energy Production on this day: ", max_day["total_renewable"].values[0])
print("Average Day Ahead Price on this day: ", max_day["avg_da_price"].values[0])

print("Day with the lowest renewable energy production: ", min_day["time"].values[0])
print("Total Renewable Energy Production on this day: ", min_day["total_renewable"].values[0])
print("Average Day Ahead Price on this day: ", min_day["avg_da_price"].values[0])

print("On the day with the highest renewable energy production, the da price is low, as the supply of energy is high. On the other hand, if there is low production (or forcasted prodcution), the price of energy tends to be high.")

# Task 2.5: What is the average hourly da price during week days vs during weekends. Why do you think average prices may differ?
daily_df = df.groupby(df["time"].dt.date).agg(
    avg_da_price=("Day Ahead Price hourly [in EUR/MWh]", "mean")
).reset_index()

daily_df["day_type"] = daily_df["time"].apply(lambda x: "weekend" if x.weekday() in [5, 6] else "weekday")

weekday_df = daily_df[daily_df["day_type"] == "weekday"]
weekend_df = daily_df[daily_df["day_type"] == "weekend"]

weekday_avg_price = weekday_df["avg_da_price"].mean()
weekend_avg_price = weekend_df["avg_da_price"].mean()

print("Average Day Ahead Price during Weekdays: ", weekday_avg_price)
print("Average Day Ahead Price during Weekends: ", weekend_avg_price)
print("The average price during the weekdays is higher than during the weekends. This could be due to the fact that the demand for energy is higher during the weekdays, as people are at work and the industrial production (for example) is using more energy.")

# Task 2.6: How much revenue would you generate with a battery with a capacity of 1 MWh which you can fully charge and fully discharge (1 Cycle) every day in 2021?
# the easiest strategy I would come up with, is charging the energy to a low price and selling it for a high one
# for this we take fidn the average lowest intraday price and the average highest intraday price
# we look at the quartlerhourly intraday markets assuming that we can charge and discharge the battery quickly

# Extract hour and minute from the time column
df["minute"] = df["time"].dt.minute

# Group by hour and minute
hour_minute_df = df.groupby(["hour", "minute"]).agg(
    avg_price=("Intraday Price Price Quarter Hourly  [in EUR/MWh]", "mean"),
).reset_index()

print(hour_minute_df.head())

# Find the lowest and highest average prices per quarter-hour
lowest_price_row = hour_minute_df.loc[hour_minute_df["avg_price"].idxmin()]
highest_price_row = hour_minute_df.loc[hour_minute_df["avg_price"].idxmax()]

lowest_price = lowest_price_row["avg_price"]
highest_price = highest_price_row["avg_price"]

print("Lowest average price per quarter-hour: ", lowest_price, " at hour: ", lowest_price_row["hour"], " and minute: ", lowest_price_row["minute"])
print("Highest average price per quarter-hour: ", highest_price, " at hour: ", highest_price_row["hour"], " and minute: ", highest_price_row["minute"])

print("We try out the strategy of buying our energy at 4 o'clock and selling it at 20 o'clock")

# Calculate the revenue generated by the battery for each day
df["date"] = df["time"].dt.date
daily_revenue = df.groupby("date").apply(
    lambda x: x[(x["hour"] == 20) & (x["minute"] == 0)]["Intraday Price Price Quarter Hourly  [in EUR/MWh]"].values[0] -
              x[(x["hour"] == 4) & (x["minute"] == 0)]["Intraday Price Price Quarter Hourly  [in EUR/MWh]"].values[0]
).sum()

print("Total revenue generated by the battery in 2021: ", daily_revenue)

# Task 2.7: Come up with a trading strategy that makes money between the day ahead hourly prices and the intraday hourly prices.

df["difference da - id"] = df["Day Ahead Price hourly [in EUR/MWh]"] - df["Intraday Price Hourly  [in EUR/MWh]"]

# Select relevant columns for correlation matrix
correlation_columns = [
    "difference da - id",
    "Day Ahead Price hourly [in EUR/MWh]",
    "Intraday Price Hourly  [in EUR/MWh]",
    "PV Day Ahead Forecast [in MWh]",
    "Wind Day Ahead Forecast [in MWh]",
    "PV Intraday Forecast [in MWh]",
    "Wind Intraday Forecast [in MWh]"
]

# Calculate correlation matrix
correlation_matrix = df[correlation_columns].corr()

print(correlation_matrix)

# Plot correlation matrix
plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Correlation Matrix")
plt.savefig("pics/correlation_matrix.png", bbox_inches="tight")
plt.show()


# Plot the difference between Day Ahead and Intraday prices over time
plt.figure(figsize=(12, 6))
plt.plot(df["time"], df["difference da - id"], label="Difference DA - ID [in EUR/MWh]")
plt.xlabel("Time")
plt.ylabel("Difference [in EUR/MWh]")
plt.title("Difference between Day Ahead and Intraday Prices Over Time")
plt.legend()
plt.savefig("pics/difference_da_id_over_time.png", bbox_inches="tight")
plt.show()

df["weekday"] = df["time"].dt.weekday
df["weekend"] = df["time"].dt.weekday.isin([5, 6])
df["month"] = df["time"].dt.month

avg_spread_by_hour = df.groupby("hour")["difference da - id"].mean()
avg_spread_by_weekday = df.groupby("weekday")["difference da - id"].mean()

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
avg_spread_by_hour.plot(kind="bar", title="Average Spread by Hour of Day", xlabel="Hour", ylabel="Spread [EUR/MWh]")
plt.subplot(1, 2, 2)
avg_spread_by_weekday.plot(kind="bar", title="Average Spread by Weekday", xlabel="Weekday", ylabel="Spread [EUR/MWh]")
plt.tight_layout()
plt.show()
plt.savefig("pics/average_spread.png", bbox_inches="tight")

# Calculate the average spread per hour for each month
avg_spread_by_hour_month = df.groupby(["month", "hour"])["difference da - id"].mean().unstack()

# Plot the average spread per hour for each month
plt.figure(figsize=(15, 10))
sns.heatmap(avg_spread_by_hour_month, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Average Spread by Hour for Each Month")
plt.xlabel("Hour of the Day")
plt.ylabel("Month")
plt.savefig("pics/average_spread_by_hour_month.png", bbox_inches="tight")
plt.show()

# calculate the average spread per hour for each weekday
avg_spread_by_hour_weekday = df.groupby(["weekday", "hour"])["difference da - id"].mean().unstack()

# plot the average spread per hour for each weekday
plt.figure(figsize=(15, 10))
sns.heatmap(avg_spread_by_hour_weekday, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
plt.title("Average Spread by Hour for Each weekday")
plt.xlabel("Hour of the Day")
plt.ylabel("weekday")
plt.savefig("pics/average_spread_by_hour_weekday.png", bbox_inches="tight")
plt.show()

# Calculate correlation between day ahead forecasted PV/Wind and the spread
correlation_pv_spread = df["PV Day Ahead Forecast [in MWh]"].corr(df["difference da - id"])
correlation_wind_spread = df["Wind Day Ahead Forecast [in MWh]"].corr(df["difference da - id"])

print("Correlation between PV Day Ahead Forecast and Spread: ", correlation_pv_spread)
print("Correlation between Wind Day Ahead Forecast and Spread: ", correlation_wind_spread)

# Calculate correlation between day ahead forecast of PV and Wind against the Intraday values
df["difference PV da - id"] = df["PV Day Ahead Forecast [in MWh]"] - df["PV Intraday Forecast [in MWh]"]
df["difference Wind da - id"] = df["Wind Day Ahead Forecast [in MWh]"] - df["Wind Intraday Forecast [in MWh]"]

correlation_dif_pv_spread = df["difference PV da - id"].corr(df["difference da - id"])
correlation_dif_wind_spread = df["difference Wind da - id"].corr(df["difference da - id"])

print("Correlation between difference in PV da - id and Spread: ", correlation_dif_pv_spread)
print("Correlation between difference in Wind da - id and Spread: ", correlation_dif_wind_spread)

# Calculate the cumulative sum of the strategy (price day ahead - intraday price) for 18 and 19 o'clock
strategy_df = df[(df["hour"] == 17) | (df["hour"] == 18)]
strategy_df["strategy_profit"] = (strategy_df["Day Ahead Price hourly [in EUR/MWh]"] - strategy_df["Intraday Price Hourly  [in EUR/MWh]"]) * 100
strategy_df["cumulative_strategy_1_profit"] = strategy_df["strategy_profit"].cumsum()

print(strategy_df.tail())

# Plot the cumulative sum of the strategy
plt.figure(figsize=(12, 6))
plt.plot(strategy_df["time"], strategy_df["cumulative_strategy_1_profit"], label="Cumulative Strategy Profit [in EUR]")
plt.xlabel("Time")
plt.ylabel("Cumulative Profit [in EUR]")
plt.title("Cumulative Sum of Strategy 1 (DA Price - ID Price) for 17 and 18 o\'clock")
plt.legend()
plt.savefig("pics/cumulative_strategy_1_profit.png", bbox_inches="tight")
plt.show()

# Calculate the cumulative sum of the strategy (price day ahead - intraday price) for 15-21 o'clock on friday, saturday and sunday
strategy_2_df = df[((df["hour"] >= 15) & (df["hour"] <= 21)) & (df["weekday"].isin([4, 5, 6]))]
strategy_2_df["strategy_profit"] = (strategy_2_df["Day Ahead Price hourly [in EUR/MWh]"] - strategy_2_df["Intraday Price Hourly  [in EUR/MWh]"]) * 100
strategy_2_df["cumulative_strategy_2_profit"] = strategy_2_df["strategy_profit"].cumsum()

print(strategy_2_df.tail())

# Plot the cumulative sum of the strategy
plt.figure(figsize=(12, 6))
plt.plot(strategy_2_df["time"], strategy_2_df["cumulative_strategy_2_profit"], label="Cumulative Strategy Profit [in EUR]")
plt.xlabel("Time")
plt.ylabel("Cumulative Profit [in EUR]")
plt.title("Cumulative Sum of Strategy 2 (DA Price - ID Price) for 15-21 o\'clock on Friday, Saturday and Sunday")
plt.legend()
plt.savefig("pics/cumulative_strategy_2_profit.png", bbox_inches="tight")
plt.show()