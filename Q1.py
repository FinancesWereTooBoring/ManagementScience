import gurobipy as gb
import pandas as pd
import os

# Question 1.2, Data preparation
data = pd.read_csv("data/flights-1.csv",  encoding='latin-1')

# Fix of the issue with different decodings
issues = {"ZÃ¼rich": "Zurich",
          "DÃ¼sseldorf": "Dusseldorf", "MÃ¡laga": "Malaga"}
for key, value in issues.items():
    data.loc[data["departureCity"] == key, "departureCity"] = value
    data.loc[data["arrivalCity"] == key, "arrivalCity"] = value

capacity = {"small": 50, "medium": 100, "large": 300}
cost_per_mile = {"small": 4.5, "medium": 8, "large": 20}
charge = 0.1

distances = data.set_index(['departureCity', 'arrivalCity'])[
    'Distance'].to_dict()
demands = data.set_index(['departureCity', 'arrivalCity'])['Demand'].to_dict()

route_list = list(distances.keys())
# Question 1.3, I am trying to figure out
model_Q1 = gb.Model()

small = model_Q1.addVars(distances, name="small", vtype=gb.GRB.INTEGER, lb=0)
medium = model_Q1.addVars(distances, name="medium", vtype=gb.GRB.INTEGER, lb=0)
large = model_Q1.addVars(distances, name="large", vtype=gb.GRB.INTEGER, lb=0)
num_of_passengers = model_Q1.addVars(
    distances, name="Num_of_pass_", vtype=gb.GRB.INTEGER, lb=0)

# That's how I calculate the profit
model_Q1.setObjective(gb.quicksum(0.1*distances[route]*num_of_passengers[route] - distances[route]*(4*small[route] + 8 * medium[route] + 20 * large[route])
                                  for route in route_list), gb.GRB.MAXIMIZE)

# the number of customers should be lower or equal to the demand
model_Q1.addConstrs(num_of_passengers[route] <= demands[route]
                    for route in route_list)

# number of customers per route should be equal to each plane's full capacity by number of those planes
model_Q1.addConstrs(num_of_passengers[route] <= 50 * small[route] + 100 * medium[route] + 300 * large[route]
                    for route in route_list)
model_Q1.optimize()
model_Q1.ObjVal
vals = model_Q1.printAttr(["X", "Obj"])
all_vars = model_Q1.getVars()

# Since there are a lot of variables, I decided to move them into a dataframe format
values = model_Q1.getAttr("X", all_vars)
names = model_Q1.getAttr("VarName", all_vars)

res = pd.DataFrame({"names": names, "values": values})

# Question 1.4 I am tired, but I am still standing

# (a)
daily_profit = model_Q1.ObjVal

# (b)
# Basically, we just find a sum of the flights by the type of planes.
small_res = res[res["names"].str.startswith("small")]["values"].sum()
medium_res = res[res["names"].str.startswith("medium")]["values"].sum()
large_res = res[res["names"].str.startswith("large")]["values"].sum()

# (c)
# This one was tough. I decided to create a data frame with routes, distances, demand,
# Num of each plane type, and total amount of passengers. It is needed since we can't really
# see the revenue, costs and missed demand otherwise (well, or for me doing this was easier than
# checking 6k rows of Gurobi output)


distances_df = pd.DataFrame(list(distances.items()), columns=["Route", "dist"])
demand_df = pd.DataFrame(list(demands.items()), columns=["Route", "demand"])
dis_dem = distances_df.merge(demand_df, on=["Route"], how="left")

# This for loop just reshapes the data from long to more wide.
# I create columns with the types of planes and num of passengers.
# Why? Because, that's how I figured out to merge it with distance and demand
values = ["small", "medium", "large", "Num_of_pass_"]
output = pd.DataFrame()

for val in values:
    res_df = res[res["names"].str.startswith(val)]

    # The next rows just make sure that the Route columns are the same - Series of tuples.
    res_df = res_df.rename(columns={"values": f"{val}_values"})
    res_df["Route"] = '(' + \
        res_df['names'].str.extract(rf'{val}\[(.*?)\]') + ')'
    res_df.drop(columns=['names'], inplace=True)
    if output.empty:
        output = res_df
    else:
        output = output.merge(res_df, on=["Route"], how="left")

output["Route"] = output["Route"].str.strip('()').str.split(',').apply(tuple)

# Hooray, we merged them. Check out how pretty the data is after that.
hopefully_last_output = dis_dem.merge(output, on=["Route"], how="left")


# Here, I finally answer 1.4(c)
rev_raw = hopefully_last_output["dist"]*(5 * hopefully_last_output["small_values"] + 10 *
                                         hopefully_last_output["medium_values"] + 30 * hopefully_last_output["large_values"])
revenue = rev_raw.sum()

costs_raw = hopefully_last_output["dist"]*(4.5 * hopefully_last_output["small_values"] + 8 *
                                           hopefully_last_output["medium_values"] + 10 * hopefully_last_output["large_values"])
costs = costs_raw.sum()

# (d)
profit_margin = daily_profit/revenue

# (e)

daily_number_of_passengers = hopefully_last_output["Num_of_pass__values"].sum()

# (f)

# Since I assumed that the airplane goes only if it's full, the utilization is 100%

# (g)

# WE calculate what is the share of missed demand w.r.t the whole demand
lost_demand = (hopefully_last_output["demand"].sum(
) - hopefully_last_output["Num_of_pass__values"].sum())/hopefully_last_output["demand"].sum()


# Summary table
summary = pd.DataFrame({"result": [
    "Daily profit", "small", "medium", "large", "revenue", "costs", "profit margin", "total num of passenger", "lost demand"],
    "values": [
    daily_profit, small_res, medium_res, large_res, revenue, costs, profit_margin, daily_number_of_passengers, lost_demand]})

num_of_files = len(os.listdir("output")) + 1
with pd.ExcelWriter(f"output/Ver{num_of_files}_Outcome.xlsx") as writer:
    res.to_excel(writer, sheet_name="raw_outcome", index=False)
    hopefully_last_output.to_excel(
        writer, sheet_name="final_table", index=False)
    summary.to_excel(writer, sheet_name="summary", index=False)
