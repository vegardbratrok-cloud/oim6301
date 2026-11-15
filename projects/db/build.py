import marimo

__generated_with = "0.24.2"
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
    # BabsonAI Labs · Building the Database

    This notebook builds `database.duckdb` from nothing every time it runs:
    it deletes the old file, creates the tables, loads the CSV files in
    `data/`, and creates the view. Every other cell reads the database
    through `ask()`, which opens the file, runs one query and closes it again.
    """)
    return


@app.cell
def _(duckdb, mo):
    database = mo.notebook_dir() / "database.duckdb"
    data_dir = mo.notebook_dir() / "data"

    def ask(sql):
        with duckdb.connect(database, read_only=True) as _con:
            return _con.sql(sql).pl()

    return ask, data_dir, database


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Tables

    One table for each table in the ERD. Every primary key and foreign key
    is declared, and the scenario's rules that fit inside one row are CHECKs:
    a budget and an expense are above zero, a commitment is 1 to 40 hours,
    a status and a category are one of the listed values, and a task is
    never completed before it was created. `work_email` is UNIQUE but not
    the key, because emails change when somebody changes title.
    """)
    return


@app.cell
def _():
    tables_sql = """
    CREATE TABLE people (
        person_id   INTEGER PRIMARY KEY,
        first_name  VARCHAR NOT NULL,
        last_name   VARCHAR NOT NULL,
        work_email  VARCHAR NOT NULL UNIQUE,
        title       VARCHAR NOT NULL,
        start_date  DATE NOT NULL,
        manager_id  INTEGER,                     -- empty for the two founders
        FOREIGN KEY (manager_id) REFERENCES people (person_id),
        CHECK (manager_id <> person_id)          -- nobody reports to themselves
    );

    CREATE TABLE projects (
        project_id  INTEGER PRIMARY KEY,
        name        VARCHAR NOT NULL UNIQUE,
        client_name VARCHAR,                     -- empty for internal projects
        category    VARCHAR NOT NULL
                    CHECK (category IN ('LLM app', 'data pipeline', 'internal tool')),
        budget      DECIMAL(12, 2) NOT NULL CHECK (budget > 0),
        start_date  DATE NOT NULL,
        status      VARCHAR NOT NULL DEFAULT 'planned'
                    CHECK (status IN ('planned', 'active', 'paused', 'done'))
    );

    CREATE TABLE assignments (
        person_id      INTEGER NOT NULL,
        project_id     INTEGER NOT NULL,
        role           VARCHAR NOT NULL,
        hours_per_week INTEGER NOT NULL CHECK (hours_per_week BETWEEN 1 AND 40),
        joined_date    DATE NOT NULL,
        PRIMARY KEY (person_id, project_id),     -- one row per person per project
        FOREIGN KEY (person_id) REFERENCES people (person_id),
        FOREIGN KEY (project_id) REFERENCES projects (project_id)
    );

    CREATE TABLE tasks (
        task_id        INTEGER PRIMARY KEY,
        project_id     INTEGER NOT NULL,         -- exactly one project
        description    VARCHAR NOT NULL,
        created_date   DATE NOT NULL,
        assignee_id    INTEGER,                  -- empty while unassigned
        due_date       DATE NOT NULL,
        completed_date DATE,                     -- empty until it is done
        FOREIGN KEY (project_id) REFERENCES projects (project_id),
        FOREIGN KEY (assignee_id) REFERENCES people (person_id),
        CHECK (completed_date IS NULL OR completed_date >= created_date)
    );

    CREATE TABLE expenses (
        expense_id   INTEGER PRIMARY KEY,
        project_id   INTEGER NOT NULL,
        expense_date DATE NOT NULL,
        amount       DECIMAL(10, 2) NOT NULL CHECK (amount > 0),
        category     VARCHAR NOT NULL
                     CHECK (category IN ('GPU cloud', 'data labeling', 'software', 'travel')),
        note         VARCHAR,
        FOREIGN KEY (project_id) REFERENCES projects (project_id)
    );
    """
    return (tables_sql,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The Data

    `make_data.py` writes one CSV file per table into `data/`, covering the
    12 months up to the **as_of date, 2026-10-31**. It uses a fixed random
    seed, so it writes the same files every time.

    The data obeys every rule except one, broken on purpose for question 7:
    **tasks 67 and 79** are assigned to somebody who does not work on the
    task's project. The tables accept these two rows, because the rule
    compares a task with the assignments table, and a CHECK only sees one
    row. Question 7 in Part B finds them with a query.

    Some rows have nothing attached on purpose: the two planned projects,
    Contract Q&A and Onboarding Wiki, have no expenses yet.

    People are loaded one row at a time, in `person_id` order, because
    `manager_id` points at `people` itself and every manager has a lower id
    than the people who report to them.
    """)
    return


@app.cell
def _(data_dir, database, duckdb, mo, tables_sql, view_sql):
    # start from nothing: delete the old database file
    database.unlink(missing_ok=True)
    database.with_name(database.name + ".wal").unlink(missing_ok=True)

    def _csv(table):
        return f"read_csv('{(data_dir / f'{table}.csv').as_posix()}')"

    with duckdb.connect(database) as _con:
        _con.execute(tables_sql)

        # people one row at a time, each manager before their reports
        _people = _con.execute(f"SELECT * FROM {_csv('people')} ORDER BY person_id").fetchall()
        for _row in _people:
            _con.execute("INSERT INTO people VALUES (?, ?, ?, ?, ?, ?, ?)", list(_row))

        for _table in ["projects", "assignments", "tasks", "expenses"]:
            _con.execute(f"INSERT INTO {_table} SELECT * FROM {_csv(_table)}")

        _con.execute(view_sql)

    built = True
    mo.md(f"Built `{database.name}` from the five CSV files.")
    return (built,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Look at the Data

    Tasks created each month, read straight from `tasks.csv` with polars.

    **TODO: This looks realistic for a growing startup: tasks start in December,
    when the first people join projects, rise to a peak in May as the team grows,
    dip over the summer, and climb again in the fall as new projects start..**
    """)
    return


@app.cell
def _(data_dir, pl):
    tasks_by_month = (
        pl.read_csv(data_dir / "tasks.csv", try_parse_dates=True)
        .with_columns(pl.col("created_date").dt.strftime("%Y-%m").alias("month"))
        .group_by("month")
        .len(name="tasks")
        .sort("month")
    )
    tasks_by_month.plot.bar(x="month", y="tasks")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Row Counts
    """)
    return


@app.cell
def _(ask, built):
    built  # rerun this cell whenever the database is rebuilt
    ask("""
        SELECT 'people' AS table_name, count(*) AS rows FROM people
        UNION ALL SELECT 'projects', count(*) FROM projects
        UNION ALL SELECT 'assignments', count(*) FROM assignments
        UNION ALL SELECT 'tasks', count(*) FROM tasks
        UNION ALL SELECT 'expenses', count(*) FROM expenses
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A Row It Refuses

    The rule: nobody commits more than 40 hours a week to a single project.
    This tries to put the CEO on Menu Chat for 45 hours a week.
    """)
    return


@app.cell
def _(built, database, duckdb, mo):
    built  # run after the database is built
    try:
        with duckdb.connect(database) as _con:
            _con.execute(
                "INSERT INTO assignments VALUES (1, 2, 'engineer', 45, DATE '2026-10-01')"
            )
        _message = "The database accepted the row, which it should not have."
    except duckdb.Error as _error:
        _message = f"Refused: {_error}"
    mo.md(f"`{_message}`")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Answers You Already Knew
    """)
    return


@app.cell
def _(ask, built, mo):
    built
    mo.vstack([
        mo.md("**1. How many people report to nobody?** Expected: **2**, the two founders."),
        ask("SELECT count(*) AS founders FROM people WHERE manager_id IS NULL"),
    ])
    return


@app.cell
def _(ask, built, mo):
    built
    mo.vstack([
        mo.md("**2. Which projects have no expenses?** Expected: the two planned "
              "projects, **Contract Q&A** and **Onboarding Wiki**."),
        ask("""
            SELECT name, status FROM projects
            WHERE project_id NOT IN (SELECT project_id FROM expenses)
        """),
    ])
    return


@app.cell
def _(ask, built, mo):
    built
    mo.vstack([
        mo.md("**3. What is the largest weekly commitment to a single project?** "
              "Expected: **25 hours**, the most make_data.py ever gives."),
        ask("SELECT max(hours_per_week) AS largest_commitment FROM assignments"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A View

    Every week the founders ask who is overloaded. `active_hours` gives each
    person's hours a week across all active projects. It is created in the
    cell that builds the database, so it always shows the current rows.
    Question 3 in Part B uses it.
    """)
    return


@app.cell
def _():
    view_sql = """
    CREATE VIEW active_hours AS
    SELECT p.person_id,
           p.first_name,
           p.last_name,
           sum(a.hours_per_week) AS hours_per_week
    FROM people AS p
    JOIN assignments AS a ON a.person_id = p.person_id
    JOIN projects AS pr ON pr.project_id = a.project_id
    WHERE pr.status = 'active'
    GROUP BY p.person_id, p.first_name, p.last_name
    """
    return (view_sql,)


@app.cell
def _(ask, built):
    built
    ask("SELECT * FROM active_hours ORDER BY hours_per_week DESC")
    return


if __name__ == "__main__":
    app.run()
