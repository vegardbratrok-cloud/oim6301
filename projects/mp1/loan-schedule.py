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
    # Your inputs.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work

    Add as many cells as you need. Try each step yourself before you ask your agent, and commit as you go.
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer

    *A table of your results in the cell below, printed with `print` and f-strings, then one sentence here that answers the question in section 1, with the number in it.*
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right

    *At least one check that reaches a result a second, independent way. Name what you compared and what came out.*
    """)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent

    *Pick one piece of AI output you did not accept as-is. What did it give you, what did you change, and how did you know? Point to the commit or the cell.*

    *If the agent got it right the first time: what did you do to verify that?*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Going Further

    *Take at least one step past the main task, in any direction, and use your agent as much as you like. It does not have to work. State what you tried, what you found, and where it is in this notebook.*
    """)
    return


if __name__ == "__main__":
    app.run()
