import gurobipy as gb
import pandas as pd
import os

# Question 1.2
data = pd.read_csv("data/flights-1.csv",  encoding='latin-1')

# Fix of the issue with different decodings.
encoding_issues = {"ZÃ¼rich": "Zurich",
                   "DÃ¼sseldorf": "Dusseldorf", "MÃ¡laga": "Malaga"}
for key, value in encoding_issues.items():
    data.loc[data["departureCity"] == key, "departureCity"] = value
    data.loc[data["arrivalCity"] == key, "arrivalCity"] = value

# Create necessary dictionaries.
capacity = {"small": 50, "medium": 100, "large": 300}
cost_per_mile = {"small": 4.5, "medium": 8, "large": 20}
charge = 0.1

distances = data.set_index(['departureCity', 'arrivalCity'])[
    'Distance'].to_dict()
demands = data.set_index(['departureCity', 'arrivalCity'])['Demand'].to_dict()

route_list = list(distances.keys())

# Question 1.3
model_Q1 = gb.Model()

small = model_Q1.addVars(distances, name="small", vtype=gb.GRB.INTEGER, lb=0)
medium = model_Q1.addVars(distances, name="medium", vtype=gb.GRB.INTEGER, lb=0)
large = model_Q1.addVars(distances, name="large", vtype=gb.GRB.INTEGER, lb=0)
num_of_passengers = model_Q1.addVars(
    distances, name="Num_of_pass_", vtype=gb.GRB.INTEGER, lb=0)

# Profit it the Objective of this model.
model_Q1.setObjective(gb.quicksum(charge*distances[route]*num_of_passengers[route] - distances[route]*(cost_per_mile["small"]*small[route] + cost_per_mile["medium"] * medium[route] + cost_per_mile["large"] * large[route])
                                  for route in route_list), gb.GRB.MAXIMIZE)

# The number of customers per route should be lower or equal to the demand.
model_Q1.addConstrs(num_of_passengers[route] <= demands[route]
                    for route in route_list)

# Number of customers per route should be equal or lower than each plane's full capacity by number of those planes.
model_Q1.addConstrs(num_of_passengers[route] <= capacity["small"] * small[route] + capacity["medium"] * medium[route] + capacity["large"] * large[route]
                    for route in route_list)

model_Q1.optimize()
model_Q1.ObjVal
all_vars = model_Q1.getVars()

# For the further analysis it was decided to move the variables and their values into a data frame format.
gurobi_variables = model_Q1.getAttr("X", all_vars)
names = model_Q1.getAttr("VarName", all_vars)

gurobi_result = pd.DataFrame({"names": names, "values": gurobi_variables})

# Question 1.4

# (a)
daily_profit = model_Q1.ObjVal

# (b)
small_result = gurobi_result[gurobi_result["names"].str.startswith(
    "small")]["values"].sum()
medium_result = gurobi_result[gurobi_result["names"].str.startswith(
    "medium")]["values"].sum()
large_result = gurobi_result[gurobi_result["names"].str.startswith(
    "large")]["values"].sum()

# (c)
# It was decided to create a united data frame with routes, distances, demand,
# Num of each plane type, and total amount of passengers. It is needed since we can't really
# see the revenue, costs and other proportions directly.


distances_df = pd.DataFrame(list(distances.items()), columns=["Route", "dist"])
demand_df = pd.DataFrame(list(demands.items()), columns=["Route", "demand"])
distance_and_demand_df = distances_df.merge(
    demand_df, on=["Route"], how="left")

# This for loop reshapes the data from long to wide.
# I create columns with the types of planes and num of passengers.
gurobi_variables = ["small", "medium", "large", "Num_of_pass_"]
gurobi_output_wide = pd.DataFrame()

for variable in gurobi_variables:
    resulting_df = gurobi_result[gurobi_result["names"].str.startswith(
        variable)]

    # The next rows just make sure that the Route columns are the same - Series of tuples.
    resulting_df = resulting_df.rename(
        columns={"values": f"{variable}_values"})
    resulting_df["Route"] = '(' + \
        resulting_df['names'].str.extract(rf'{variable}\[(.*?)\]') + ')'
    resulting_df.drop(columns=['names'], inplace=True)
    if gurobi_output_wide.empty:
        gurobi_output_wide = resulting_df
    else:
        gurobi_output_wide = gurobi_output_wide.merge(
            resulting_df, on=["Route"], how="left")

gurobi_output_wide["Route"] = gurobi_output_wide["Route"].str.strip(
    '()').str.split(',').apply(tuple)

# We merged them.
demand_distance_and_gurobi_wide = distance_and_demand_df.merge(
    gurobi_output_wide, on=["Route"], how="left")

revenue_raw = demand_distance_and_gurobi_wide["dist"] * \
    demand_distance_and_gurobi_wide["Num_of_pass__values"]*0.1
revenue = revenue_raw.sum()

costs_raw = demand_distance_and_gurobi_wide["dist"]*(4.5 * demand_distance_and_gurobi_wide["small_values"] + 8 *
                                                     demand_distance_and_gurobi_wide["medium_values"] + 20 * demand_distance_and_gurobi_wide["large_values"])
costs = costs_raw.sum()

# (d)
profit_margin = daily_profit/revenue

# (e)

daily_number_of_passengers = demand_distance_and_gurobi_wide["Num_of_pass__values"].sum(
)

# (f)
full_capacity = (50 * demand_distance_and_gurobi_wide["small_values"] + 100 *
                 demand_distance_and_gurobi_wide["medium_values"] +
                 300 * demand_distance_and_gurobi_wide["large_values"]).sum()
utilization = 1 - \
    (full_capacity -
     demand_distance_and_gurobi_wide["Num_of_pass__values"].sum()) / full_capacity

# (g)

# WE calculate what is the share of missed demand w.r.t the whole demand
lost_demand = (demand_distance_and_gurobi_wide["demand"].sum(
) - demand_distance_and_gurobi_wide["Num_of_pass__values"].sum())/demand_distance_and_gurobi_wide["demand"].sum()


# Summary table
summary = pd.DataFrame({"result": [
    "Daily profit", "small", "medium", "large", "revenue", "costs", "profit margin", "total num of passenger", "capacity utilization", "lost demand"],
    "values": [
    daily_profit, small_result, medium_result, large_result, revenue, costs, profit_margin, daily_number_of_passengers, utilization, lost_demand]})
"""
num_of_files = len(os.listdir("output")) + 1
with pd.ExcelWriter(f"output/Ver{num_of_files}_Outcome.xlsx") as writer:
    gurobi_result.to_excel(writer, sheet_name="raw_outcome", index=False)
    demand_distance_and_gurobi_wide.to_excel(
        writer, sheet_name="final_table", index=False)
    summary.to_excel(writer, sheet_name="summary", index=False)
"""
