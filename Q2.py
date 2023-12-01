import gurobipy as gb
import pandas as pd

indirect_revenue_per_customer = dict()
cities = data['arrivalCity'].unique()

for first in cities:
    for second in cities:
        for third in cities:
            if first != second and first != third and second != third:
                if (first, second) in distances and (second, third) in distances:
                    if distances[(first, third)] * 1.3 >= distances[(first, second)] + distances[(second, third)]:
                        indirect_revenue_per_customer[(first, second, third)] = 0.08 * distances[(first, third)]

charge_indirect = 0.08

model2 = gb.Model()

cities = data['departureCity'].unique()

# Variables for direct and indirect flights
small_direct = model2.addVars(cities, cities, name="small_direct", vtype=gb.GRB.INTEGER, lb=0)
medium_direct = model2.addVars(cities, cities, name="medium_direct", vtype=gb.GRB.INTEGER, lb=0)
large_direct = model2.addVars(cities, cities, name="large_direct", vtype=gb.GRB.INTEGER, lb=0)

small_indirect = model2.addVars(indirect_revenue_per_customer.keys(), name="small_indirect", vtype=gb.GRB.INTEGER, lb=0)
medium_indirect = model2.addVars(indirect_revenue_per_customer.keys(), name="medium_indirect", vtype=gb.GRB.INTEGER, lb=0)
large_indirect = model2.addVars(indirect_revenue_per_customer.keys(), name="large_indirect", vtype=gb.GRB.INTEGER, lb=0)

num_of_passengers_direct = model2.addVars(cities, cities, name="Num_direct", vtype=gb.GRB.INTEGER, lb=0)
num_of_passengers_indirect = model2.addVars(indirect_revenue_per_customer.keys(), name="Num_indirect", vtype=gb.GRB.INTEGER, lb=0)

hub = model2.addVars(cities, name="hub", vtype=gb.GRB.BINARY, lb=0)

M = 1000000000

# Constraints for direct flights
model2.addConstrs(num_of_passengers_direct[(i, j)] <= demands[(i, j)] 
                 for i in cities for j in cities if i != j)

model2.addConstrs(num_of_passengers_direct[(i, j)] <= 
                 capacity["small"] * small_direct[(i, j)] + capacity["medium"] * medium_direct[(i, j)] + capacity["large"] * large_direct[(i, j)]
                 for i in cities for j in cities if i != j)

# Constraints for indirect flights
model2.addConstrs(num_of_passengers_indirect[(i, k, j)] <= demands[(i, j)] 
                 for (i, k, j) in indirect_revenue_per_customer)

model2.addConstrs(num_of_passengers_indirect[(i, k, j)] <= 
                 capacity["small"] * small_indirect[(i, k, j)] + capacity["medium"] * medium_indirect[(i, k, j)] + capacity["large"] * large_indirect[(i, k, j)]
                 for (i, k, j) in indirect_revenue_per_customer)

# Binary variables for direct routes
y_direct = model2.addVars(cities, cities, name="direct_used", vtype=gb.GRB.BINARY, lb=0)

# Binary variables for indirect routes
y_indirect = model2.addVars(indirect_revenue_per_customer.keys(), name="indirect_used", vtype=gb.GRB.BINARY, lb=0)


# not sure if we need such a constraint:

# model2.addConstrs(y_direct.sum(i, j) + y_indirect.sum(i, '*', j) <= 1
                 # for i in cities
                 # for j in cities
                 # for k in cities
                 # if i != j and i != k and j != k)

#Only 1 hub

model2.addConstr(gb.quicksum(hub[k] for k in cities) == 1)

# Hub constraints

model2.addConstrs(y_indirect.sum('*', k, '*') <= hub[k] * M for k in cities for (i, k, j) in indirect_revenue_per_customer)

# Modified objective function with both direct and indirect flights
model2.setObjective(gb.quicksum(y_direct[i, j] * (charge * distances[(i, j)] * num_of_passengers_direct[(i, j)] - 
                                                  cost_per_mile["small"] * small_direct[(i, j)] - 
                                                  cost_per_mile["medium"] * medium_direct[(i, j)] - 
                                                  cost_per_mile["large"] * large_direct[(i, j)])
                               for i in cities for j in cities if i != j) +
                   gb.quicksum(y_indirect[i, k, j] * (charge_indirect * distances[(i, j)] * num_of_passengers_indirect[(i, k, j)] - 
                                                       cost_per_mile["small"] * small_indirect[(i, k, j)] - 
                                                       cost_per_mile["medium"] * medium_indirect[(i, k, j)] - 
                                                       cost_per_mile["large"] * large_indirect[(i, k, j)])
                               for (i, k, j) in indirect_revenue_per_customer),
                   gb.GRB.MAXIMIZE)

model2.optimize()


print("Optimal Objective Value 2:", model2.ObjVal)

# Assuming the optimization is successful
if model2.status == gb.GRB.OPTIMAL:
    selected_hub = None
    for (i, k, j) in indirect_revenue_per_customer:
        if round(y_indirect[i, k, j].x) == 1:
            selected_hub = k
            break

    if selected_hub is not None:
        print(f"The selected hub is: {selected_hub}")
    else:
        print("No hub is selected.")
else:
    print("Optimization was not successful.")

