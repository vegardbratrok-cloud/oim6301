import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Town Tax Finder
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. The Question

    This tool is for a couple looking to buy a single-family home in Middlesex County, Massachusetts, with a $700,000 budget and a goal of paying no more than $8,000 a year in property tax. It helps them decide which towns to focus their house search on by showing the towns that meet both criteria, sorted by lowest tax bill first. They can rerun it with a different county or budget.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. My Plan Before AI

    **Steps:**

    - Get every town in the county from the API, going through every page.
    - For each town, get its figures for fiscal year 2026.
    - Keep each town's average home value, residential tax rate, and average bill.
    - Remove towns with an average home value over $700,000.
    - Remove towns with an average tax bill over $8,000.
    - Sort the rest of the towns from lowest bill to highest bill.
    - Show them in a table, with a sentence answering the couple.

    **Functions:**
    - Towns: a county name goes in, and a list of towns with DOR codes comes out.
    - Figures: DOR codes and fiscal years goes in, and home value, tax rate and average bill comes out.
    - Filter and sort: Town figures, budget and tax limit goes in, and a sorted list with towns that pass through both filters comes out.

    **Addresses:**

    They will request these two addresses:
    - oim.zhili.dev/ma/towns?county=Middlesex

    - oim.zhili.dev/ma/towns/{dor_code}/history

    **How I will know I have every record:**

    I will check how many towns the API says there are and compare that with how many towns I collected. If I am missing any towns, I will get the rest from the next page.

    **Section 6 check:**
    For each town, compare the API’s average bill with ((home value × tax rate) ÷ 1,000). The two should be about equal. I’ll also check that my town count equals the pagination total.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Inputs
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Working With the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Reading It Back
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Going Further
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Time Spent
    """)
    return


if __name__ == "__main__":
    app.run()
