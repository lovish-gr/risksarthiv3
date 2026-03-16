import pandas as pd
import io

def generate_template():

    template_data = {
        "ProjectData": pd.DataFrame({
            "Project":["Project A","Project B","Project C"],
            "Units Sold":[50,30,40],
            "Price Per Unit":[250000,300000,280000],
            "Construction Cost":[6000000,5000000,5500000]
        }),
        "LoanTerms": pd.DataFrame({
            "Parameter":["Interest Rate","Tenure Years","Loan To Cost"],
            "Value":[8,5,0.7]
        })
    }

    output = io.BytesIO()

    with pd.ExcelWriter(output,engine="xlsxwriter") as writer:

        template_data["ProjectData"].to_excel(writer,sheet_name="ProjectData",index=False)

        template_data["LoanTerms"].to_excel(writer,sheet_name="LoanTerms",index=False)

    return output