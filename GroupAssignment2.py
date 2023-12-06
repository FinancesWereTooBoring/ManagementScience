import numpy as np
import gurobipy as gb

# Set up dictionaries
employees = {"Highly_experienced": {"amount": 8, "monthly_cost": 16000},
             "Experienced": {"amount": 12, "monthly_cost": 12000},
             "Moderately_experienced": {"amount": 15, "monthly_cost": 10000},
             "Less_experienced": {"amount": 5, "monthly_cost": 7000}}

num_of_projects_per_month = np.random.poisson(4)
d = np.random.choice([3, 6], p=[0.5, 0.5])
n = np.random.choice([3, 4, 5, 6], p=[0.2, 0.3, 0.3, 0.2])
