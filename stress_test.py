import pandas as pd


def run_stress_test(result, price_change, cost_change):

    stress = result.copy()

    stress["Revenue"] = stress["Revenue"] * (1 + price_change / 100)

    stress["Construction Cost"] = stress["Construction Cost"] * (1 + cost_change / 100)

    NOI = stress["Revenue"] - stress["Construction Cost"]

    stress["DSCR"] = NOI / stress["Annual Debt Payment"]

    return stress