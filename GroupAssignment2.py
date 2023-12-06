from create_workers import create_workers
import numpy as np
import gurobipy as gb
import seaborn as sn
import matplotlib.pyplot as plt
# Set up dictionaries
costs = {5: 16000, 4: 12000, 3: 10000, 2: 7000}


# idk if we need it, but here it is


def likelihood_of_accepting(q, b):
    result = 1/(1 + np.exp(-6.5 - 2*q + 0.0005*b))
    outcome = np.random.choice([0, 1], p=[1-result, result])
    return outcome


# Strategy 1
n = 50
num_of_projects_per_month = np.random.poisson(4, size=n)
employees_scenario_1 = create_workers()


def monthly_behaviour(num_of_proj,  bid):
    # We find the sum of costs of all workers who are currently engaged in project
    monthly_costs = 0
    # [costs(values["level"]) for values in employees_scenario_1.values() if values["when_will_be_available"] != 0].sum()
    for key in employees_scenario_1.keys():
        if employees_scenario_1[key]["when_will_be_available"] != 0:
            monthly_costs += costs[employees_scenario_1[key]["level"]]
            # we reduce amount of "busy" periods
            employees_scenario_1[key]["when_will_be_available"] -= 1
    monthly_revenue = 0
    missed_projects = 0
    taken_projects = 0
    for project in range(num_of_proj):
        scope_of_project = np.random.choice([3, 6], p=[0.5, 0.5])
        workers_requirement = np.random.choice(
            [3, 4, 5, 6], p=[0.2, 0.3, 0.3, 0.2])
        people = []
        for worker, values in employees_scenario_1.items():
            # I just assume for now that better workers are checked first
            if len(people) < workers_requirement:
                if values["when_will_be_available"] == 0:
                    people.append(worker)
        # Check if we managed to form a team
        if len(people) == workers_requirement:
            # Please optimize me
            potential_quality = np.mean(
                [employees_scenario_1[worker]["level"] for worker in people])
            is_accepted = likelihood_of_accepting(q=potential_quality, b=bid)
            # I am not sure if we have to calculate it like this, or just take expected values.
            if is_accepted:
                # If our project is actually accepted
                # I also assume that they start working on project from the next month. That's why the calc of costs is done on the beginning of the each month.
                for person in people:
                    employees_scenario_1[person]["when_will_be_available"] = scope_of_project
                monthly_revenue += bid * workers_requirement * scope_of_project
                taken_projects += 1
            else:
                people = []
        elif len(people) < workers_requirement:
            # if we didn't manage to form a team
            people = []
            missed_projects += 1
        else:
            # if we formed a team with more people in a team than needed - error
            print("More people in a team than needed")
            break
    return monthly_costs, monthly_revenue, missed_projects, taken_projects


total_costs, total_revenue, total_missed_projects, total_taken_projects = [], [], 0, 0
for monthly_proj in num_of_projects_per_month:
    monthly_costs, monthly_revenue, missed_projects, taken_projects = monthly_behaviour(
        monthly_proj, 20000)
    total_costs.append(monthly_costs)
    total_revenue.append(monthly_revenue)
    total_missed_projects += missed_projects
    total_taken_projects += taken_projects

total_profit = [a - b for a, b in zip(total_revenue, total_costs)]

ax = sn.histplot(total_revenue, kde=True, bins=50)
ax.set(xlabel="Revenue", ylabel="Probability")
plt.show()

a2 = sn.histplot(total_profit, kde=True, bins=50)
a2.set(xlabel="Profit", ylabel="Probability")
plt.show()

proportion_of_missed_proj = total_missed_projects / \
    (total_taken_projects + total_missed_projects)
