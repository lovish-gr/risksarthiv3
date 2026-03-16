import pandas as pd

def run_financial_engine(project_data, loan_terms):

    interest_rate = loan_terms.loc[loan_terms['Parameter']=="Interest Rate",'Value'].values[0]
    tenure = int(loan_terms.loc[loan_terms['Parameter']=="Tenure Years",'Value'].values[0])
    ltc = loan_terms.loc[loan_terms['Parameter']=="Loan To Cost",'Value'].values[0]

    monthly_rate = interest_rate/100/12
    num_payments = tenure*12

    results = []

    for _, row in project_data.iterrows():

        revenue = row["Units Sold"] * row["Price Per Unit"]
        cost = row["Construction Cost"]

        NOI = revenue - cost

        loan_amount = cost * ltc

        emi = (loan_amount * monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

        annual_payment = emi * 12

        dscr = NOI / annual_payment if annual_payment != 0 else 0

        cash_flow_after_debt = NOI - annual_payment

        profit = revenue - cost - annual_payment

        profit_margin = profit / revenue if revenue != 0 else 0

        LTV = loan_amount / revenue if revenue != 0 else 0

        ICR = NOI / annual_payment if annual_payment != 0 else 0

        results.append({
            "Project": row["Project"],
            "Units Sold": row["Units Sold"],
            "Price Per Unit": row["Price Per Unit"],
            "Construction Cost": cost,
            "Revenue": revenue,
            "NOI": NOI,
            "Loan Amount": loan_amount,
            "Annual Debt Payment": annual_payment,
            "DSCR": dscr,
            "Cash Flow After Debt": cash_flow_after_debt,
            "Profit": profit,
            "Profit Margin": profit_margin,
            "LTV": LTV,
            "ICR": ICR
        })

    result_df = pd.DataFrame(results)

    min_dscr = result_df["DSCR"].min()

    return result_df, min_dscr