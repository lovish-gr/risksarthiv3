import streamlit as st
import pandas as pd
import plotly.express as px

from financial_enigne import run_financial_engine
from portfolio_enigne import portfolio_metrics
from stress_test import run_stress_test
from utils.excel_template import generate_template
from genrate_ai_summary import generate_ai_summary
from risk_engine import calculate_risk_score, detect_risk_drivers, generate_recommendation

st.set_page_config(
    page_title="Risk Sarthi V3.0",
    page_icon="🏗️",
    layout="wide"
)

st.title("Risk Sarthi V3.0 - AI Real Estate Underwriting")
st.caption("Upload your project Excel and get instant financial risk analysis")

menu = st.sidebar.radio(
    "Navigation",
    [
        "Upload Data",
        "Project Analysis",
        "Portfolio Dashboard",
        "Stress Testing",
        "AI Insights Panel",
        "Deal Intelligence",
        "Reports"
    ]
)

# ---------------- SESSION STATE ----------------

if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False


# ---------------- UPLOAD PAGE ----------------

if menu == "Upload Data":

    # Generate and provide template download
    st.subheader("Download Excel Template")
    template_file = generate_template()
    st.download_button(
        "Download Template",
        template_file,
        "project_template.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.subheader("Upload Excel File")

    excel_file = st.file_uploader("Upload Project Excel", type=["xlsx"])

    if excel_file is not None:

        project_data = pd.read_excel(excel_file, sheet_name="ProjectData")
        loan_terms = pd.read_excel(excel_file, sheet_name="LoanTerms")

        st.success("File uploaded successfully")

        st.write("### Project Data")
        st.dataframe(project_data)

        st.write("### Loan Terms")
        st.dataframe(loan_terms)

        if st.button("Run Analysis"):

            result, min_dscr = run_financial_engine(project_data, loan_terms)

            st.session_state.project_result = result
            st.session_state.loan_terms = loan_terms
            st.session_state.min_dscr = min_dscr
            st.session_state.data_loaded = True

            st.success("Analysis Complete")


# ---------------- PROJECT ANALYSIS ----------------

elif menu == "Project Analysis":

    if not st.session_state.data_loaded:
        st.warning("Upload data first")
        st.stop()

    result = st.session_state.project_result

    score, risk_level, profit_margin, ltv = calculate_risk_score(result)

    drivers = detect_risk_drivers(
        st.session_state.min_dscr,
        profit_margin,
        ltv
    )

    recommendation = generate_recommendation(
        st.session_state.min_dscr,
        profit_margin,
        ltv
    )

    st.subheader("Financial Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric("Minimum DSCR", f"{result['DSCR'].min():.2f}")
    col2.metric("Total Revenue", f"{result['Revenue'].sum():,.0f}")
    col3.metric("Average Profit Margin", f"{result['Profit Margin'].mean():.2%}")

    st.divider()

    # button of different projects (horizontal) with their DSCR, clicking on which shows detailed analysis for that project
    for _, row in result.iterrows():
        with st.expander(f"{row['Project']} - DSCR: {row['DSCR']:.2f}"):
            st.write(f"**Revenue:** {row['Revenue']:.2f}")
            st.write(f"**Construction Cost:** {row['Construction Cost']:.2f}")
            st.write(f"**NOI:** {row['NOI']:.2f}")
            st.write(f"**Loan Amount:** {row['Loan Amount']:.2f}")
            st.write(f"**Annual Debt Payment:** {row['Annual Debt Payment']:.2f}")
            st.write(f"**Cash Flow After Debt:** {row['Cash Flow After Debt']:.2f}")
            st.write(f"**Profit:** {row['Profit']:.2f}")
            st.write(f"**Profit Margin:** {row['Profit Margin']:.2%}")
            st.write(f"**LTV:** {row['LTV']:.2%}")
            st.write(f"**ICR:** {row['ICR']:.2f}")


    # st.dataframe(result)

    # fig = px.bar(result, x="Project", y="DSCR", title="DSCR by Project")
    # st.plotly_chart(fig, use_container_width=True)

    # add sensitivity analysis table for revenue and cost
    st.subheader("Sensitivity Analysis")
    scenario_data = pd.DataFrame({
        "scenario": ["Base Case", "Revenue -10%", "Revenue +10%", "Cost +10%", "Cost -10%"],
        "DSCR": [
            result["DSCR"].mean(),
            run_stress_test(result, price_change=-10, cost_change=0)["DSCR"].mean(),
            run_stress_test(result, price_change=10, cost_change=0)["DSCR"].mean(),
            run_stress_test(result, price_change=0, cost_change=10)["DSCR"].mean(),
            run_stress_test(result, price_change=0, cost_change=-10)["DSCR"].mean()
        ]
    })
    st.table(scenario_data)


    # Breakeven analysis

    st.subheader("Breakeven Price")

    breakeven = result.copy()

    breakeven["Breakeven Price"] = (
        breakeven["Construction Cost"] + breakeven["Annual Debt Payment"]
    ) / breakeven["Units Sold"]

    st.dataframe(breakeven[["Project", "Breakeven Price"]])

    # Risk Classification
    st.subheader("Risk Classification")
    def classify_risk(dscr):
        if dscr >= 1.5:
            return "Low Risk"
        elif dscr >= 1.0:
            return "Medium Risk"
        else:
            return "High Risk"
    result["Risk Level"] = result["DSCR"].apply(classify_risk)
    st.dataframe(result[["Project", "DSCR", "Risk Level"]])

    # cash flow waterfall
    st.subheader("Cash Flow Waterfall")
    cash_flow = result[["Project", "Revenue", "Construction Cost", "Annual Debt Payment"]].copy()
    cash_flow["NOI"] = cash_flow["Revenue"] - cash_flow["Construction Cost"]
    cash_flow["Cash Flow After Debt"] = cash_flow["NOI"] - cash_flow["Annual Debt Payment"]
    cash_flow_melted = cash_flow.melt(id_vars="Project", value_vars=["Revenue", "Construction Cost", "Annual Debt Payment", "Cash Flow After Debt"], var_name="Component", value_name="Amount")
    fig = px.bar(cash_flow_melted, x="Project", y="Amount", color="Component", title="Cash Flow Waterfall")
    st.plotly_chart(fig, use_container_width=True) 


    # Revenue vs Cost scatter plot
    st.subheader("Revenue vs Cost")
    fig2 = px.line(result, x="Project", y=["Revenue", "Construction Cost"], title="Revenue vs Construction Cost")
    st.plotly_chart(fig2, use_container_width=True)



    


# ---------------- PORTFOLIO DASHBOARD ----------------

elif menu == "Portfolio Dashboard":

    if not st.session_state.data_loaded:
        st.warning("Upload data first")
        st.stop()

    result = st.session_state.project_result

    metrics, portfolio = portfolio_metrics(result)

    st.subheader("Portfolio Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Loan Exposure", f"{metrics['total_loan']:,.0f}")
    col2.metric("Average DSCR", f"{metrics['avg_dscr']:.2f}")
    col3.metric("Minimum DSCR", f"{metrics['min_dscr']:.2f}")
    col4.metric("High Risk Projects", metrics["high_risk"])

    st.subheader("DSCR Comparison")



    fig = px.bar(
        portfolio,
        x="Project",
        y="DSCR",
        color="Risk Level",
        title="Portfolio Risk Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Portfolio Table")

    # st.dataframe(portfolio)

    portfolio_display = portfolio[["Project", "DSCR", "LTV", "Risk Level", "Loan Amount"]].copy()
    portfolio_display["Loan Amount"] = portfolio_display["Loan Amount"].apply(lambda x: f"{x:,.0f}")
    st.dataframe(portfolio_display)

    #print average DSCR, weighted risk and worst project
    st.subheader("Key Portfolio Metrics")
    st.write(f"**Average DSCR:** {metrics['average_dscr']:.2f}")
    st.write(f"**Total Exposure:** {metrics['total_exposure']:,.0f}")
    st.write(f"**Weighted Risk Score:** {metrics['weighted_risk']}")
    st.write(f"**Worst Project:** {metrics['worst_project']} (DSCR: {metrics['worst_project_dscr']})")


# ---------------- STRESS TESTING ----------------

elif menu == "Stress Testing":

    if not st.session_state.data_loaded:
        st.warning("Upload data first")
        st.stop()

    st.subheader("Stress Testing")

    price_change = st.slider("Price Change %", -30, 30, 0)
    cost_change = st.slider("Cost Change %", -30, 30, 0)

    result = st.session_state.project_result

    stress_result = run_stress_test(result, price_change, cost_change)

    st.dataframe(stress_result)

    fig = px.bar(stress_result, x="Project", y="DSCR", title="DSCR Under Stress")

    st.plotly_chart(fig, use_container_width=True)


# ---------------- AI CREDIT MEMO ----------------

elif menu == "AI Insights Panel":

    if not st.session_state.data_loaded:
        st.warning("Upload data first")
        st.stop()

    project_data = st.session_state.project_result
    loan_terms = st.session_state.loan_terms
    profit_margin = project_data["Profit Margin"].mean()
    ltv = project_data["LTV"].mean()
    recommendation = generate_recommendation(
        st.session_state.min_dscr,
        profit_margin,
        ltv
    )

    summary = generate_ai_summary(
        st.session_state.min_dscr,
        profit_margin,
        ltv,
        recommendation
    )

    st.subheader("AI Underwriting Summary")
    st.write(summary)

        

# ---------------- DEAL INTELLIGENCE ----------------
elif menu == "Deal Intelligence":

    if not st.session_state.data_loaded:
        st.warning("Upload data first")
        st.stop()
    

    score, level, profit_margin, ltv = calculate_risk_score(st.session_state.project_result)
    print(score, profit_margin, ltv, level)
    drivers = detect_risk_drivers(
        st.session_state.min_dscr,
        profit_margin,
        ltv   
    )
    recommendation = generate_recommendation(
        st.session_state.min_dscr,
        profit_margin,
        ltv
    )
    risk_level = level

    
    st.subheader("Deal Intelligence Panel")

    col1, col2 = st.columns(2)

    col1.metric("Risk Score", f"{score:.0f}/100")
    col2.metric("Risk Level", risk_level)

    st.write("### Key Risk Drivers")

    for d in drivers:
        st.write(f"• {d}")

    st.write("### Investment Recommendation")

    if recommendation == "APPROVE":
        st.success("APPROVE")

    elif recommendation == "WATCHLIST":
        st.warning("WATCHLIST")

    else:
        st.error("REJECT")


# ---------------- REPORTS ----------------

elif menu == "Reports":

    if not st.session_state.data_loaded:
        st.warning("Upload data first")
        st.stop()

    result = st.session_state.project_result

    csv = result.to_csv(index=False).encode()

    st.download_button(
        "Download Report",
        csv,
        "portfolio_analysis.csv",
        "text/csv"
    )



# ----------feedback form----------
st.sidebar.markdown("---")
st.sidebar.subheader("💬 Give Feedback")

name = st.sidebar.text_input("Name")
email = st.sidebar.text_input("Email")
role = st.sidebar.text_input("Role (Analyst / Developer / Investor)")
feedback = st.sidebar.text_area(
    "Your Feedback",
    placeholder="What feature would you like? What was confusing?"
)

if st.sidebar.button("Submit Feedback"):

    if name and email and feedback:

        payload = {
            "name": name,
            "email": email,
            "role": role,
            "feedback": feedback
        }

        try:

            response = requests.post(
                "https://script.google.com/macros/s/AKfycbyNyQI2Eh9vaXF02bU5koCjaYSQmmaKRi-TsvUL9aelCPDPRyKqyw1AI2iBtVJkqSKM/exec",
                json=payload
            )

            if response.status_code == 200:
                st.sidebar.success("✅ Feedback submitted. Thank you!")

            else:
                st.sidebar.error("Something went wrong.")

        except:
            st.sidebar.error("Failed to send feedback.")

    else:
        st.sidebar.warning("Please fill required fields.")
