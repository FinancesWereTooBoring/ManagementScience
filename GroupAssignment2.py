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


class Simulation:
    def __init__(self, bid=None, n=50, flow_bid=False):
        self.n = n
        self.num_of_projects_per_month = np.random.poisson(4, size=n)
        self.employees_scenario_1 = create_workers()
        self.bid = bid
        self.flow_bid = flow_bid
        self.intitalisation()

    def monthly_behaviour(self, num_of_proj):
        # We find the sum of costs of all workers who are currently engaged in project
        monthly_costs = 0
        # [costs(values["level"]) for values in employees_scenario_1.values() if values["when_will_be_available"] != 0].sum()
        for key in self.employees_scenario_1.keys():
            if self.employees_scenario_1[key]["when_will_be_available"] != 0:
                monthly_costs += costs[self.employees_scenario_1[key]["level"]]
                # we reduce amount of "busy" periods
                self.employees_scenario_1[key]["when_will_be_available"] -= 1
        monthly_revenue = 0
        missed_projects = 0
        taken_projects = 0
        man_months = 0
        for project in range(num_of_proj):
            scope_of_project = np.random.choice([3, 6], p=[0.5, 0.5])
            workers_requirement = np.random.choice(
                [3, 4, 5, 6], p=[0.2, 0.3, 0.3, 0.2])
            people = []
            for worker, values in self.employees_scenario_1.items():
                # I just assume for now that better workers are checked first
                if len(people) < workers_requirement:
                    if values["when_will_be_available"] == 0:
                        people.append(worker)
            # Check if we managed to form a team
            if len(people) == workers_requirement:
                # Please optimize me
                potential_quality = np.mean(
                    [self.employees_scenario_1[worker]["level"] for worker in people])
                if not self.bid:
                    self.bid = 2000 * (2 * potential_quality + 6.5)
                is_accepted = likelihood_of_accepting(
                    q=potential_quality, b=self.bid)
                # I am not sure if we have to calculate it like this, or just take expected values.
                if is_accepted:
                    # If our project is actually accepted
                    # I also assume that they start working on project from the next month. That's why the calc of costs is done on the beginning of the each month.
                    for person in people:
                        self.employees_scenario_1[person]["when_will_be_available"] = scope_of_project
                        # Add only the ones who are actually in the project
                        man_months += scope_of_project
                    monthly_revenue += self.bid * workers_requirement * scope_of_project
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

            if self.flow_bid:
                self.bid = None

        return monthly_costs, monthly_revenue, missed_projects, taken_projects, man_months

    def intitalisation(self):
        self.total_costs, self.total_revenue, self.total_missed_projects, self.total_taken_projects, self.total_man_months = [], [], 0, 0, 0
        for monthly_proj in self.num_of_projects_per_month:
            monthly_costs, monthly_revenue, missed_projects, taken_projects, man_months = self.monthly_behaviour(
                monthly_proj)
            self.total_costs.append(monthly_costs)
            self.total_revenue.append(monthly_revenue)
            self.total_missed_projects += missed_projects
            self.total_taken_projects += taken_projects
            self.total_man_months += man_months
        self.total_profit = [self.total_revenue[i] - self.total_costs[i]
                             for i in range(len(self.total_revenue))]
        # Missed proj/all the projs
        self.proportion_of_missed_proj = self.total_missed_projects / \
            (self.num_of_projects_per_month.sum())

        # Utilization of man-months
        self.utilization_man_months = self.total_man_months/(40 * 50)

    def revenue_plot(self):
        # Revenue plot
        ax = sn.histplot(self.total_revenue, kde=True, bins=50)
        ax.set(xlabel="Revenue", ylabel="Probability")
        plt.show()
        plt.close()

    def profit_plot(self):
        # Profit plot
        a2 = sn.histplot(self.total_profit, kde=True, bins=50)
        a2.set(xlabel="Profit", ylabel="Probability")
        plt.show()
        plt.close()


# Strategy 1:
scenario_1 = Simulation(bid=20000)
scenario_1.revenue_plot()
scenario_1.profit_plot()
scenario_1.proportion_of_missed_proj
scenario_1.utilization_man_months

# Strategy 2:
proposed_bids = np.random.randint(100, 50000, 100)
highest_exp_rev = 0
best_bid = 0
outcome = {}
for bid in proposed_bids:
    scenario = Simulation(bid)
    if np.mean(scenario.total_revenue) > highest_exp_rev:
        best_bid = bid
        highest_exp_rev = np.mean(scenario.total_revenue)
    outcome[bid] = np.mean(scenario.total_revenue)

# Strategy 3:

strategy_3 = Simulation(n=50, flow_bid=True)
strategy_3.revenue_plot()
strategy_3.profit_plot()
strategy_3.proportion_of_missed_proj
strategy_3.utilization_man_months
