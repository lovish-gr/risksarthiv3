#import run_financial_engine from financial_enigne.py
from financial_enigne import run_financial_engine


def generate_ai_summary(min_dscr, profit_margin, ltv, recommendation):

    summary = f"""
Financial Summary

Minimum DSCR: {min_dscr:.2f}
Profit Margin: {profit_margin:.2%}
Loan to Cost (LTV): {ltv:.2%}

Interpretation

The project shows {'strong' if min_dscr > 1.3 else 'moderate'} debt coverage.

Profitability appears {'healthy' if profit_margin > 0.2 else 'thin'}.

Leverage is {'within acceptable range' if ltv < 0.75 else 'relatively high'}.

Investment Recommendation: {recommendation}
"""

    return summary