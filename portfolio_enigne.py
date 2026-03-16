import pandas as pd


def classify_risk(dscr):

    if dscr < 1:
        return "High Risk"

    elif dscr < 1.25:
        return "Moderate Risk"

    return "Low Risk"


def portfolio_metrics(result):

    portfolio = result.copy()

    # Portfolio Risk Score = average DSCR adjusted by leverage
    portfolio["Risk Score"] = portfolio["DSCR"] / (1 + portfolio["LTV"])

    portfolio["Total Exposure"] = portfolio["Loan Amount"]

    portfolio["Weighted Risk"] = portfolio["Risk Score"] * portfolio["Total Exposure"]

    portfolio["worst project"] = portfolio["DSCR"].idxmin()

    portfolio["Risk Level"] = portfolio["DSCR"].apply(classify_risk)

    portfolio["Average DSCR"] = portfolio["DSCR"].mean()

    portfolio = portfolio.sort_values("DSCR")

    metrics = {

        "total_loan": portfolio["Loan Amount"].sum(),

        "avg_dscr": portfolio["DSCR"].mean(),

        "min_dscr": portfolio["DSCR"].min(),

        "high_risk": (portfolio["DSCR"] < 1.2).sum(),

        "worst_project": portfolio.loc[portfolio["DSCR"].idxmin(), "Project"],

        "worst_project_dscr": portfolio["DSCR"].min(),

        "total_exposure": portfolio["Total Exposure"].sum(),

        "weighted_risk": portfolio["Weighted Risk"].sum() / portfolio["Total Exposure"].sum(),

        "average_dscr": portfolio["Average DSCR"].mean()

    }

    return metrics, portfolio