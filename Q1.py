import gurobipy as gb
import pandas as pd

# Question 1.2, Data preparation
data = pd.read_csv("data/flights-1.csv",  encoding='latin-1')

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

model_Q1.setObjective(gb.quicksum(distances[route]*(0.5 * small[route] + 2 * medium[route] + 10 * large[route])
                                  for route in route_list), gb.GRB.MAXIMIZE)

model_Q1.addConstrs(num_of_passengers[route] <= demands[route]
                    for route in route_list)
model_Q1.addConstrs(num_of_passengers[route] == 50 * small[route] + 100 * medium[route] + 300 * large[route]
                    for route in route_list)
model_Q1.optimize()
model_Q1.ObjVal
vals = model_Q1.printAttr(["X", "Obj"])
all_vars = model_Q1.getVars()

values = model_Q1.getAttr("X", all_vars)
names = model_Q1.getAttr("VarName", all_vars)

res = pd.DataFrame({"names": names, "values": values})

res[res["names"].str.startswith("large")]["values"].sum()
small_res = res[res["names"].str.startswith("small")]["values"].sum()
medium_res = res[res["names"].str.startswith("medium")]["values"].sum()
large_res = res[res["names"].str.startswith("large")]["values"].sum()
objective_value = model_Q1.ObjVal
summary = pd.DataFrame({"result": ["small", "medium", "large", "objective_value"], "values": [
                       small_res, medium_res, large_res, objective_value]})

"""
with pd.ExcelWriter("Ver1_Outcome.xlsx") as writer:
    res.to_excel(writer, sheet_name="raw_outcome", index=False)
    summary.to_excel(writer, sheet_name="summary", index=False)
"""
