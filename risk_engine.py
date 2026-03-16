import pandas as pd

def calculate_risk_score(result_df):

    min_dscr = result_df["DSCR"].min()

    revenue = result_df["Revenue"].sum()
    cost = result_df["Construction Cost"].sum()
    loan = result_df["Loan Amount"].sum()

    profit_margin = (revenue - cost) / revenue
    ltv = loan / cost

    score = 100

    score -= ltv * 40
    score -= max(0, (1.5 - min_dscr)) * 25
    score -= max(0, (0.25 - profit_margin)) * 40

    score = max(0, min(100, score))

    if score > 70:
        level = "Low Risk"
    elif score > 50:
        level = "Moderate Risk"
    else:
        level = "High Risk"

    return score, level, profit_margin, ltv


def detect_risk_drivers(min_dscr, profit_margin, ltv):

    drivers = []

    if min_dscr < 1.2:
        drivers.append("Weak debt service coverage")
    else:
        drivers.append("Strong debt service coverage")

    if profit_margin < 0.15:
        drivers.append("Low development profit margin")
    else:
        drivers.append("Healthy project margin")

    if ltv > 0.75:
        drivers.append("High leverage risk")
    else:
        drivers.append("Moderate leverage")

    return drivers


def generate_recommendation(min_dscr, profit_margin, ltv):

    if min_dscr > 1.3 and profit_margin > 0.2 and ltv < 0.75:
        return "APPROVE"

    elif min_dscr > 1.1:
        return "WATCHLIST"

    else:
        return "REJECT"