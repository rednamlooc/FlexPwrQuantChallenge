# Task 2: Data analysis and building a trading strategy

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load data
df = pd.read_excel("analysis_task_data.xlsx")


# print(df.head())
# print(df.columns)

## Task 2.1: 
### How much Wind/PV Power was forecasted to produced in German in 2021 [in MWh] on Day Ahead (da) and on Intraday (id).

df['Wind Day Ahead Forecast [in MWh]'] = df['Wind Day Ahead Forecast [in MW]'] * 0.25
df['PV Day Ahead Forecast [in MWh]'] = df['PV Day Ahead Forecast [in MW]'] * 0.25
df['Wind Intraday Forecast [in MWh]'] = df['Wind Intraday Forecast [in MW]'] * 0.25
df['PV Intraday Forecast [in MWh]'] = df['PV Intraday Forecast [in MW]'] * 0.25

# as the data runs from 2021-01-01 to 2021-12-31, we can just sum the MWh columns
wind_da_total = df['Wind Day Ahead Forecast [in MWh]'].sum()
wind_id_total = df['Wind Intraday Forecast [in MWh]'].sum()
pv_da_total = df['PV Day Ahead Forecast [in MWh]'].sum()
pv_id_total = df['PV Intraday Forecast [in MWh]'].sum()


print("Total Wind forcasteded Day Ahead: ", wind_da_total)
print("Total Wind forcasteded Intraday: ", wind_id_total)
print("Wind da - id: ", wind_da_total - wind_id_total)
print("Total PV forcasteded Day Ahead: ", pv_da_total)
print("Total PV forcasteded Intraday: ", pv_id_total)
print("PV da - id: ", pv_da_total - pv_id_total)

## Task 2.2: Show the average Wind/Solar production for 2021 over a 24h period for Intraday and Day Ahead (4 lines in one graph).

# average wind and pv production per hour
avg_wind_da_per_hour = df.groupby('hour')['Wind Day Ahead Forecast [in MWh]'].mean()
avg_pv_da_per_hour = df.groupby('hour')['PV Day Ahead Forecast [in MWh]'].mean()
avg_wind_id_per_hour = df.groupby('hour')['Wind Intraday Forecast [in MWh]'].mean()
avg_pv_id_per_hour = df.groupby('hour')['PV Intraday Forecast [in MWh]'].mean()

plt.figure(figsize=(12, 6))
plt.plot(avg_wind_da_per_hour, label='Wind Day Ahead Forecast [in MWh]')
plt.plot(avg_pv_da_per_hour, label='PV Day Ahead Forecast [in MWh]')
plt.plot(avg_wind_id_per_hour, label='Wind Intraday Forecast [in MWh]')
plt.plot(avg_pv_id_per_hour, label='PV Intraday Forecast [in MWh]')
plt.xlabel('Hour of the Day')
plt.ylabel('Average Forecast [in MWh]')
plt.title('Average Wind/PV Forecast for 2021 Over a 24h Period')
plt.legend()
plt.show()
plt.savefig('average_forecast.png')

# Task 2.3: What was the average value [in EUR/MWh] for Wind/Solar Power in 2021 using the da forecast and using da h prices? Is the average value of Wind and PV higher or lower than the average da price? Why could it be higher/lower?

df['Wind Revenue [in EUR]'] = df['Wind Day Ahead Forecast [in MWh]'] * df['Day Ahead Price hourly [in EUR/MWh]']
df['PV Revenue [in EUR]'] = df['PV Day Ahead Forecast [in MWh]'] * df['Day Ahead Price hourly [in EUR/MWh]']

# Calculate the total value and total forecasted production
total_wind_revenue = df['Wind Revenue [in EUR]'].sum()
total_pv_revenue = df['PV Revenue [in EUR]'].sum()


# Calculate the average value in EUR/MWh
avg_wind_value_per_mwh = total_wind_revenue / wind_da_total
avg_pv_value_per_mwh = total_pv_revenue / pv_da_total

# Calculate the average day ahead price
avg_da_price = df['Day Ahead Price hourly [in EUR/MWh]'].mean()

print("Average Wind Value [in EUR/MWh]: ", avg_wind_value_per_mwh)
print("Average PV Value [in EUR/MWh]: ", avg_pv_value_per_mwh)
print("Average Day Ahead Price [in EUR/MWh]: ", avg_da_price)

print("The average value of Wind and PV is lower than the average day ahead price. I can think of some reasons for this: 1. there might be forcasting inaccuracies, that affect the price 2. the average day ahead price is calculated over all hours, while the average value of Wind and PV is calculated over the forecasted production (being a volume weighted average) 3. there might be issues with oversupply during certain hours. To asses these closer, I would need to look at the data in more detail.")

# Task 2.4: Find the Day with the highest renewable energy production and with the lowest renewable energy production in 2021. What was the average Day Ahead Price levels on these days? How do you explain the difference in prices?

# Calculate the total renewable energy production per day
df['Total Renewable Forecast [in MWh]'] = df['Wind Day Ahead Forecast [in MWh]'] + df['PV Day Ahead Forecast [in MWh]']

# As we are forecasting the procution for the day ahead, we need to time shift by one day to find the correct date
df["forecasted_day"] = df["time"] + pd.Timedelta(days=1)

daily_df = df.groupby(df["forecasted_day"].dt.date).agg(
    total_renewable=("Total Renewable Forecast [in MWh]", "sum"),
    avg_da_price=("Day Ahead Price hourly [in EUR/MWh]", "mean"),
).reset_index()

# Find the day with the highest and lowest renewable energy production
max_day = daily_df[daily_df["total_renewable"] == daily_df["total_renewable"].max()]
min_day = daily_df[daily_df["total_renewable"] == daily_df["total_renewable"].min()]

print("Day with the highest renewable energy production: ", max_day["forecasted_day"].values[0])
print("Total Renewable Energy Production on this day: ", max_day["total_renewable"].values[0])
print("Average Day Ahead Price on this day: ", max_day["avg_da_price"].values[0])

print("Day with the lowest renewable energy production: ", min_day["forecasted_day"].values[0])
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

# Task 2.6: 