import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import duckdb
    import polars as pl
    import altair as alt

    return alt, duckdb, mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # BabsonAI Labs · Questions

    Every question asks `database.duckdb`, which `build.py` builds from the
    CSV files in `data/`. Every "last 90 days" counts back from the as_of
    date below: the 90 days ending on that date.
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
    ## Q1. How much of its budget has each project spent?
    """)
    return


@app.cell
def _(ask):
    q1 = ask("""
        SELECT p.name AS project,
               p.budget,
               coalesce(sum(e.amount), 0) AS spent,
               round(100 * coalesce(sum(e.amount), 0) / p.budget, 1) AS pct_of_budget
        FROM projects AS p
        LEFT JOIN expenses AS e ON e.project_id = p.project_id
        GROUP BY p.project_id, p.name, p.budget
        ORDER BY pct_of_budget DESC
    """)
    q1
    return (q1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Eval Harness has spent the largest share of its budget, 119.5%
    ($17,928.59 of $15,000), so it is over budget, while the two planned
    projects have spent 0%; I counted every expense up to the as_of date.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q2. Which tasks are past their due date and still not done, and who has them?
    """)
    return


@app.cell
def _(as_of, ask):
    ask(f"""
        SELECT t.task_id,
               pr.name AS project,
               t.description,
               t.due_date,
               coalesce(pe.first_name || ' ' || pe.last_name, '(unassigned)') AS assigned_to
        FROM tasks AS t
        JOIN projects AS pr ON pr.project_id = t.project_id
        LEFT JOIN people AS pe ON pe.person_id = t.assignee_id
        WHERE t.completed_date IS NULL
          AND t.due_date < DATE '{as_of}'
        ORDER BY t.due_date
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    33 tasks were due before 2026-10-31 and are still not completed; I count
    a task due on the as_of date itself as not yet late, and I keep the 2
    overdue tasks that nobody is assigned to, shown as "(unassigned)".
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q3. How many hours a week does each person have on active projects, and who is above 40?

    This uses the view `active_hours` from `build.py`.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT first_name || ' ' || last_name AS person,
               hours_per_week,
               hours_per_week > 40 AS above_40
        FROM active_hours
        ORDER BY hours_per_week DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Of the 22 people on active projects, 5 commit more than 40 hours a week:
    Mateo Rossi at 65, Zara Hussain, Ethan Brooks and Lucas Moreau at 50,
    and Nora Quinn at 43; people on no active project are left out rather
    than shown with 0 hours.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q4. In the last 90 days, which expense categories cost more than the average category?
    """)
    return


@app.cell
def _(as_of, ask):
    ask(f"""
        SELECT category,
               sum(amount) AS total
        FROM expenses
        WHERE expense_date BETWEEN CAST(DATE '{as_of}' - INTERVAL 89 DAY AS DATE)
                               AND DATE '{as_of}'
        GROUP BY category
        HAVING sum(amount) > (
            SELECT avg(category_total)
            FROM (
                SELECT sum(amount) AS category_total
                FROM expenses
                WHERE expense_date BETWEEN CAST(DATE '{as_of}' - INTERVAL 89 DAY AS DATE)
                                       AND DATE '{as_of}'
                GROUP BY category
            )
        )
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In the 90 days from 2026-08-03 to 2026-10-31, only GPU cloud
    ($62,237.53) cost more than the average category total of $23,660.93.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q5. Which projects have no expenses at all?
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT p.name AS project, p.status
        FROM projects AS p
        LEFT JOIN expenses AS e ON e.project_id = p.project_id
        WHERE e.expense_id IS NULL
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    2 of the 14 projects have no expenses: Contract Q&A and Onboarding Wiki,
    both still planned.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q6. How many tasks and how much spending does each project have?

    Tasks and expenses are counted separately before they are joined to
    projects, because joining both at once would pair every task with every
    expense. The last three columns count each one again on its own.
    """)
    return


@app.cell
def _(ask):
    ask("""
        WITH task_counts AS (
            SELECT project_id, count(*) AS tasks
            FROM tasks GROUP BY project_id
        ),
        expense_totals AS (
            SELECT project_id, sum(amount) AS expenses
            FROM expenses GROUP BY project_id
        ),
        combined AS (
            SELECT p.project_id,
                   p.name AS project,
                   coalesce(tc.tasks, 0) AS tasks,
                   coalesce(et.expenses, 0) AS expenses
            FROM projects AS p
            LEFT JOIN task_counts AS tc ON tc.project_id = p.project_id
            LEFT JOIN expense_totals AS et ON et.project_id = p.project_id
        ),
        checked AS (
            SELECT c.*,
                   (SELECT count(*) FROM tasks AS t
                    WHERE t.project_id = c.project_id) AS tasks_alone,
                   (SELECT coalesce(sum(amount), 0) FROM expenses AS e
                    WHERE e.project_id = c.project_id) AS expenses_alone
            FROM combined AS c
        )
        SELECT project, tasks, expenses, tasks_alone, expenses_alone,
               tasks = tasks_alone AND expenses = expenses_alone AS matches
        FROM checked
        ORDER BY tasks DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Inventory Sync has the most tasks, 37, with $31,794.21 in expenses, and
    every one of the 14 rows matches counting its tasks and expenses on
    their own.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q7. Is any task assigned to somebody who does not work on its project?
    """)
    return


@app.cell
def _(ask):
    q7 = ask("""
        SELECT t.task_id,
               pr.name AS project,
               pe.first_name || ' ' || pe.last_name AS assigned_to
        FROM tasks AS t
        JOIN projects AS pr ON pr.project_id = t.project_id
        JOIN people AS pe ON pe.person_id = t.assignee_id
        LEFT JOIN assignments AS a
               ON a.person_id = t.assignee_id
              AND a.project_id = t.project_id
        WHERE a.person_id IS NULL
    """)
    q7
    return (q7,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    2 tasks break the rule, the two broken on purpose in Part A: task 67,
    assigned to Hannah Okafor, and task 79, assigned to Emily Carter, both
    on Inventory Sync, a project neither of them works on.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q8. How many people report to each manager, and how many hours a week have those people committed?
    """)
    return


@app.cell
def _(ask):
    q8 = ask("""
        SELECT m.first_name || ' ' || m.last_name AS manager,
               count(DISTINCT r.person_id) AS direct_reports,
               coalesce(sum(a.hours_per_week), 0) AS reports_hours_per_week
        FROM people AS m
        JOIN people AS r ON r.manager_id = m.person_id
        LEFT JOIN assignments AS a ON a.person_id = r.person_id
        GROUP BY m.person_id, m.first_name, m.last_name
        ORDER BY direct_reports DESC, reports_hours_per_week DESC
    """)
    q8
    return (q8,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    6 people manage somebody: Lucas Moreau's 5 direct reports have committed
    the most, 213 hours a week across all projects, and Omar Haddad's 2
    reports the least, 25; I counted all projects, whatever their status.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q9 (my own). Which projects finish their tasks on time most often?

    Of each project's completed tasks, the share finished on or before
    the due date.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT pr.name AS project,
               count(*) AS completed_tasks,
               count(*) FILTER (WHERE t.completed_date <= t.due_date) AS on_time,
               round(100.0 * count(*) FILTER (WHERE t.completed_date <= t.due_date)
                     / count(*), 1) AS pct_on_time
        FROM tasks AS t
        JOIN projects AS pr ON pr.project_id = t.project_id
        WHERE t.completed_date IS NOT NULL
        GROUP BY pr.project_id, pr.name
        ORDER BY pct_on_time DESC, completed_tasks DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Lead Scorer finished all 10 of its completed tasks on time (100%), and
    Hiring Tracker the fewest, 14 of 30 (46.7%); Contract Q&A's 100% rests on
    a single task, and projects with no completed tasks are left out.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Q10 (my own). Which kind of project takes longest to finish a task?

    The average number of days from a task's creation to its completion,
    for each project category, counting completed tasks only.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT pr.category,
               count(*) AS completed_tasks,
               round(avg(date_diff('day', t.created_date, t.completed_date)), 1)
                   AS avg_days_to_complete
        FROM tasks AS t
        JOIN projects AS pr ON pr.project_id = t.project_id
        WHERE t.completed_date IS NOT NULL
        GROUP BY pr.category
        ORDER BY avg_days_to_complete DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Internal tools take the longest, 18.1 days on average to finish a task,
    against 14.7 days for LLM apps and 14.0 days for data pipelines.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. How I Know These Numbers Are Right

    Three answers reached a second way. Each check shows both numbers and
    stops with an error if they disagree. Question 6 also checks every row
    against counting it on its own, in its last three columns.
    """)
    return


@app.cell
def _(ask, mo, q1):
    # Q1's spending, added up over the projects, against all expenses at once
    _from_q1 = round(float(q1["spent"].sum()), 2)
    _direct = round(float(ask("SELECT sum(amount) FROM expenses").item()), 2)
    _out = mo.md(f"**Check 1, Q1:** sum of the projects' spending = **{_from_q1:,.2f}**; "
                 f"all expenses added up directly = **{_direct:,.2f}**")
    assert _from_q1 == _direct, "Q1 does not add up to the total of all expenses"
    _out
    return


@app.cell
def _(ask, mo, q8):
    # Q8's direct reports and hours, against counting them straight from the tables
    _reports_q8 = int(q8["direct_reports"].sum())
    _reports_direct = int(ask(
        "SELECT count(*) FROM people WHERE manager_id IS NOT NULL").item())
    _hours_q8 = int(q8["reports_hours_per_week"].sum())
    _hours_direct = int(ask("""
        SELECT sum(a.hours_per_week)
        FROM assignments AS a
        JOIN people AS p ON p.person_id = a.person_id
        WHERE p.manager_id IS NOT NULL
    """).item())
    _out = mo.md(
        f"**Check 2, Q8:** direct reports in Q8 = **{_reports_q8}**; people who have "
        f"a manager = **{_reports_direct}**. Hours in Q8 = **{_hours_q8}**; hours of "
        f"everybody who has a manager = **{_hours_direct}**."
    )
    assert _reports_q8 == _reports_direct, "Q8 counts the direct reports wrong"
    assert _hours_q8 == _hours_direct, "Q8 adds up the hours wrong"
    _out
    return


@app.cell
def _(mo, q7):
    # Q7 against the two rows make_data.py broke on purpose in Part A
    _found = sorted(q7["task_id"].to_list())
    _broken_in_part_a = [67, 79]
    _out = mo.md(f"**Check 3, Q7:** tasks found = **{_found}**; "
                 f"tasks broken on purpose in Part A = **{_broken_in_part_a}**")
    assert _found == _broken_in_part_a, "Q7 does not find exactly the two broken tasks"
    _out
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Working With the Agent

    The agent’s first version of make_data.py left tasks unassigned
    if they were created before anyone joined the project, and those tasks were never completed.
    This did not break any written rules, but Q2 showed that 43 of the 74 overdue tasks were unassigned,
    which seemed unrealistic. I changed the script so tasks are only created after someone joins the
    project and rebuilt the data. Q2 then showed 33 overdue tasks, with only 2 unassigned.
    The two tasks with intentional rule violations changed to tasks 67 and 79, so I updated
    “The Data” in build.py. The assignments stayed the same, so my join prediction still holds.
    These changes are in make_data.py, under the comment "nobody creates a
    task before anybody works on the project".
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Reading It Back

    **The question:** For each manager, how many people report to them
    directly, and the hours a week those people have committed across all
    projects (question 8).

    **My prediction, committed as `db: prediction` before answering any question:**
    I expect **59** rows. Each report joins to exactly one manager, so that
    join adds no rows, but each report appears once for every project they
    work on. So the result has one row for every assignment held by someone
    who has a manager: the 66 assignments minus the 7 held by the two
    founders.

    **The joins alone, before any grouping:**
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT count(*) AS rows_before_grouping
        FROM people AS m
        JOIN people AS r ON r.manager_id = m.person_id
        LEFT JOIN assignments AS a ON a.person_id = r.person_id
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Did it match?** Yes, the joins produced 59 rows, as I predicted.
    Each report matched exactly one manager, so that join added no rows, and
    every report works on at least one project, so the left join to assignments
    neither lost nor added anybody: one row per assignment of someone with a manager.

    **What one row of the final result means:**
    One row represents one manager, how many people report directly to them,
    and those people’s combined weekly hours across all projects.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Going Further

    Four steps past the ten questions, all in this section: Q1 as a chart,
    a dropdown that answers questions about any project without editing
    code, what goes wrong if Q6 joins everything at once, and a check of
    the half of the Q7 rule that Q7 leaves out.

    **Q1 as a chart.** Each project's share of its budget spent, with a red
    line at 100%. Eval Harness is the only bar past the line.
    """)
    return


@app.cell
def _(alt, pl, q1):
    _bars = (
        alt.Chart(q1.with_columns(pl.col("budget", "spent", "pct_of_budget").cast(pl.Float64)))
        .mark_bar()
        .encode(
            x=alt.X("pct_of_budget:Q", title="Share of budget spent (%)"),
            y=alt.Y("project:N", sort="-x", title="Project"),
            tooltip=["project", "budget", "spent", "pct_of_budget"],
        )
    )
    _full_budget = (
        alt.Chart(pl.DataFrame({"pct": [100]}))
        .mark_rule(color="red")
        .encode(x="pct:Q")
    )
    (_bars + _full_budget).properties(
        title="Q1: share of budget spent, as of 2026-10-31", width=500
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Ask about any project without editing code.** Pick a project, and the
    table below shows its status, budget, spending, tasks, overdue tasks and
    team.
    """)
    return


@app.cell
def _(ask, mo):
    project_picker = mo.ui.dropdown(
        options=ask("SELECT name FROM projects ORDER BY name")["name"].to_list(),
        value="Eval Harness",
        label="Project",
    )
    project_picker
    return (project_picker,)


@app.cell
def _(as_of, ask, project_picker):
    _name = project_picker.value.replace("'", "''")
    ask(f"""
        SELECT p.name AS project,
               p.status,
               p.budget,
               (SELECT coalesce(sum(amount), 0) FROM expenses AS e
                WHERE e.project_id = p.project_id) AS spent,
               (SELECT count(*) FROM tasks AS t
                WHERE t.project_id = p.project_id) AS tasks,
               (SELECT count(*) FROM tasks AS t
                WHERE t.project_id = p.project_id
                  AND t.completed_date IS NULL
                  AND t.due_date < DATE '{as_of}') AS overdue_tasks,
               (SELECT count(*) FROM assignments AS a
                WHERE a.project_id = p.project_id) AS team_size,
               (SELECT coalesce(sum(hours_per_week), 0) FROM assignments AS a
                WHERE a.project_id = p.project_id) AS team_hours_per_week
        FROM projects AS p
        WHERE p.name = '{_name}'
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **What happens if Q6 joins tasks and expenses in one go?** Joining
    projects to both tasks and expenses at once pairs every task of a
    project with every expense of the same project. The query below does
    that on purpose: Inventory Sync turns into 851 rows (37 tasks × 23
    expenses), and its spending looks like $1,176,385.77 instead of
    $31,794.21. That is why Q6 totals tasks and expenses separately first.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT pr.name AS project,
               count(*) AS joined_rows,
               sum(e.amount) AS inflated_expenses
        FROM projects AS pr
        JOIN tasks AS t ON t.project_id = pr.project_id
        JOIN expenses AS e ON e.project_id = pr.project_id
        GROUP BY pr.project_id, pr.name
        ORDER BY joined_rows DESC
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The other half of the Q7 rule.** The scenario also says a task is
    never assigned before the assignee's start date. Q7 does not check
    that, so this query does: it finds no tasks, so that half of the rule
    holds in every row.
    """)
    return


@app.cell
def _(ask):
    ask("""
        SELECT t.task_id, t.created_date, p.first_name, p.last_name, p.start_date
        FROM tasks AS t
        JOIN people AS p ON p.person_id = t.assignee_id
        WHERE t.created_date < p.start_date
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Time Spent

    About 3.5 hours.
    """)
    return


if __name__ == "__main__":
    app.run()
