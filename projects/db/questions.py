import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    return duckdb, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # BabsonAI Labs · Questions

    Every question asks `database.duckdb`, which `build.py` builds from the
    CSV files in `data/`. Every "last 30 days", "last 90 days" or
    "last month" counts back from the as_of date below.
    """)
    return


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()
    return (ask,)


@app.cell
def _():
    as_of = "2026-10-31"
    return (as_of,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. How I Know These Numbers Are Right
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Working With the Agent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Reading It Back

    **The question:** For each manager, how many people report to them
    directly, and the hours a week those people have committed across all
    projects (question 8).

    **My prediction, before answering any question:**
    TODO: I expect 59 rows. Each report joins to exactly one manager, 
    so that join adds no rows, but each report appears once for every project they work on. 
    So the result has one row for every assignment held by someone who has a manager: 
    the 66 assignments minus the 7 held by the two founders.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Going Further
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Time Spent
    """)
    return


if __name__ == "__main__":
    app.run()
