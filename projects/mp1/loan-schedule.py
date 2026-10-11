# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
# ]
# ///
"""Mini Project 1.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mini Project 1

    Your choice of option, what each one asks for, the due date and how it is graded are on the Mini Project 1 page of the course site, linked from the calendar. This notebook is the shape to build it in. Keep the headings, and replace each line in italics with your own.

    Save it in your course repository as `projects/mp1/<your-tool>.py`, named for what it does, such as `loan-schedule.py`, and open it with `uv run marimo edit`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    Someone in the process of buying a home would use this to compare different mortgage options. It will help decide which loan is best for them, by comparing monthly payments, total interest costs and how much they could save by paying extra or refinancing at different times.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    I would start by entering the loan amount, annual interest rate, and number of years. Then, I would calculate the monthly payment using the loan formula, which takes the loan amount, interest rate, and number of payments into account.

    Next, I would create a table that shows what happens to the loan each month. First, I would calculate the interest by multiplying the remaining loan balance by the monthly interest rate (annual rate divided by 12). Then, I would subtract the interest from the monthly payment to find how much of the loan itself is being paid off. I would subtract this amount from the previous balance to get the new balance.

    I would repeat these calculations every month until the loan is fully paid off. The final payment might need to be adjusted slightly to bring the balance to exactly zero. I would then add up all the monthly interest payments to find the total interest paid over the loan. Finally, I would do the same for the 15-year loan and compare the two.

    **What does the loop carry from one step to the next?**

    The loop carries the remaining loan balance. Each month starts with the balance left from the previous month, which is used to calculate the next month's interest and remaining balance.

    **Which check will you use in section 6, and which two numbers should agree?**

    I would check that the total principal paid equals the original loan amount of $400,000. These two numbers should agree, and the remaining balance at the end should be zero.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs

    Every number the project starts from goes in the cell below, and nowhere else, so that changing one input changes every result after it.

    Copy in the default inputs for your option from the Mini Project 1 page. If you chose D, your own option, type your data in here, or ask your agent to generate it with `faker`. The required part reads no file.
    """)
    return


@app.cell
def _():
    loan_amount = 400000
    annual_rates = {30: 0.0703, 15: 0.0642}
    extra_payment = 200
    return annual_rates, extra_payment, loan_amount


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _(annual_rates, loan_amount):
    payments = {}
    total_interests = {}
    total_principals = {}
    for years, rate in annual_rates.items():
        monthly_rate = rate / 12
        months = years * 12
        payment = round((loan_amount * monthly_rate) / (1 - (1 + monthly_rate) ** -months),2)
        balance = loan_amount
        total_interest = 0
        total_principal = 0
        print(f"{years}-year loan, monthly payment {payment:,.2f}")
        print(f"{'Month':>5} {'Payment':>10} {'Interest':>10} {'Principal':>10} {'Balance':>12}")
        for month in range(1, months +1):
            interest = round(balance * monthly_rate, 2)
            total_interest = round(total_interest + interest, 2)
            if month == months:
                principal = balance
            else:
                principal = round(payment - interest, 2)
            this_payment = round(interest + principal, 2)
            total_principal = round(total_principal + principal, 2)
            balance = round(balance - principal, 2)
            print(f"{month:>5} {this_payment:>10,.2f} {interest:>10,.2f} {principal:>10,.2f} {balance:>12,.2f}")
        print(f"Total interest: {total_interest:,.2f}")
        payments[years] = payment
        total_principals[years] = total_principal
        total_interests[years] = total_interest
    return payments, total_interests, total_principals


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    The 15-year mortgage costs USD 797.59 more per month (USD 3,466.86 vs. USD 2,669.27) but saves USD 336,906.69 in total interest (USD 224,035.34 vs. USD 560,942.03), so if your friend can afford the higher monthly payment, the 15-year loan is the better choice.
    """)
    return


@app.cell
def _(annual_rates, loan_amount, payments, total_interests):
    print(f"{'Term':>6} {'Payment':>10} {'Total interest':>15} {'Total paid':>12}")
    for _years in annual_rates:
        _total_paid = loan_amount + total_interests[_years]
        print(f"{_years:>6} {payments[_years]:>10,.2f} {total_interests[_years]:>15,.2f} {_total_paid:>12,.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    I added the principal paid in every month, and compared it with the total loan amount, with both coming out to exactly $400,000. This is also consistent with the Excel-table I built before starting the project in marimo.
    """)
    return


@app.cell
def _(annual_rates, loan_amount, total_principals):
    for _years in annual_rates:
        _matches = total_principals[_years] == loan_amount
        print(f"{_years}-year loan: principal paid {total_principals[_years]:,.2f}, loan amount {loan_amount:,.2f}, equal: {_matches}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    I knew because marimo showed an error saying the cell redefines a variable from another cell, and after the change the table ran and matched my section 4 results. See the section 5 cell, commit “mp1: answer table and sentence”.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    I tried paying an extra USD 200 every month on each loan (input extra_payment in section 3, code in the section 8 cell). The 30-year loan is paid off in 291 months instead of 360, 69 months sooner, and saves USD 127,538.86 in interest. The 15-year loan is paid off in 165 months instead of 180, 15 months sooner, and saves USD 21,939.64. The extra payment saves far more on the 30-year loan, because that loan carries a large balance for much longer, so more interest is avoided.
    """)
    return


@app.cell
def _(extra_payment, mo):
    extra_slider = mo.ui.slider(0, 1000, step=50, value=extra_payment, label="Extra payment per month")
    extra_slider
    return


@app.cell
def _(annual_rates, extra_payment, loan_amount, payments, total_interests):
    for _years, _rate in annual_rates.items():
        _r = _rate / 12
        _balance = loan_amount
        _month = 0
        _interest_total = 0
        while _balance > 0:
            _month = _month + 1
            _interest = round(_balance * _r, 2)
            _principal = round(payments[_years] + extra_payment - _interest, 2)
            if _principal > _balance:
                _principal = _balance
            _interest_total = round(_interest_total + _interest, 2)
            _balance = round(_balance - _principal, 2)
        _months_saved = _years * 12 - _month
        _interest_saved = round(total_interests[_years] - _interest_total, 2)
        print(f"{_years}-year loan, {extra_payment:,} extra per month: paid off in {_month} months ({_months_saved} months sooner), total interest {_interest_total:,.2f}, saves {_interest_saved:,.2f}")
    return


if __name__ == "__main__":
    app.run()
