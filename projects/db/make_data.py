"""Make fake data for BabsonAI Labs and write one CSV per table into data/.

Run from the root of the repository:

    uv run projects/db/make_data.py

The random seed is fixed, so every run writes exactly the same files.
Empty cells in the CSVs mean "no value" and load as NULL in DuckDB.
"""

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(6301)

AS_OF = date(2026, 10, 31)  # "today" in the data
FIRST_DAY = date(2025, 11, 1)  # the data covers the 12 months up to AS_OF
DATA_DIR = Path(__file__).parent / "data"


def rand_date(start, end):
    """A random date from start to end, both included."""
    return start + timedelta(days=random.randint(0, (end - start).days))


# ---------------------------------------------------------------- people
# Person 1 and 2 are the founders. 3-6 are managers who report to a
# founder. Everyone else reports to one of the managers. A manager always
# has a lower id than the people who report to them, so loading the rows
# in id order puts every manager in before their reports.

NAMES = [
    ("Maya", "Lindqvist"), ("Omar", "Haddad"), ("Priya", "Raman"),
    ("Lucas", "Moreau"), ("Hannah", "Okafor"), ("Daniel", "Kim"),
    ("Sofia", "Alvarez"), ("Ethan", "Brooks"), ("Aisha", "Bello"),
    ("Noah", "Fischer"), ("Grace", "Liu"), ("Mateo", "Rossi"),
    ("Chloe", "Nguyen"), ("Samuel", "Adeyemi"), ("Lena", "Novak"),
    ("Ryan", "Walsh"), ("Zara", "Hussain"), ("Felix", "Berg"),
    ("Emily", "Carter"), ("Arjun", "Mehta"), ("Isabel", "Santos"),
    ("Jonas", "Larsen"), ("Mia", "Tanaka"), ("Leo", "Ivanov"),
    ("Nora", "Quinn"),
]
MANAGER_TITLES = ["Head of Engineering", "Head of Product",
                  "Engineering Manager", "Data Lead"]
STAFF_TITLES = ["ML Engineer", "Software Engineer", "Data Engineer",
                "Product Designer", "Data Analyst", "Solutions Engineer"]

people = []  # dicts, in id order
for i, (first, last) in enumerate(NAMES, start=1):
    if i <= 2:
        manager_id = None
        title = "CEO & Co-founder" if i == 1 else "CTO & Co-founder"
        start = FIRST_DAY
    elif i <= 6:
        manager_id = 1 if i <= 4 else 2
        title = MANAGER_TITLES[i - 3]
        start = rand_date(date(2025, 11, 3), date(2026, 1, 30))
    else:
        manager_id = 3 + (i - 7) % 4  # spreads the staff over managers 3-6
        title = random.choice(STAFF_TITLES)
        manager_start = people[manager_id - 1]["start_date"]
        start = rand_date(max(manager_start + timedelta(days=7),
                              date(2025, 12, 1)), date(2026, 8, 31))
    people.append({
        "person_id": i,
        "first_name": first,
        "last_name": last,
        "work_email": f"{first}.{last}@babsonailabs.com".lower(),
        "title": title,
        "start_date": start,
        "manager_id": manager_id,
    })
person_by_id = {p["person_id"]: p for p in people}

# -------------------------------------------------------------- projects
# (name, client or None for internal, category, status, start date)
PROJECTS = [
    ("Invoice Reader", "Northside Plumbing", "LLM app", "done", date(2025, 11, 10)),
    ("Menu Chat", "Harbor Pizza Co.", "LLM app", "active", date(2025, 12, 1)),
    ("Inventory Sync", "Greenleaf Grocers", "data pipeline", "active", date(2025, 11, 17)),
    ("Review Summarizer", "Lumen Salon", "LLM app", "active", date(2026, 2, 9)),
    ("Sales Data Lake", "Atlas Hardware", "data pipeline", "done", date(2025, 12, 8)),
    ("Booking Assistant", "Cedar Dental", "LLM app", "active", date(2026, 4, 6)),
    ("Shipment Tracker", "Bayside Logistics", "data pipeline", "paused", date(2026, 1, 12)),
    ("Support Copilot", "Brightwave Fitness", "LLM app", "active", date(2026, 1, 19)),
    ("Lead Scorer", "Pine & Oak Realty", "data pipeline", "active", date(2026, 5, 18)),
    ("Hiring Tracker", None, "internal tool", "active", date(2025, 12, 15)),
    ("GPU Cost Monitor", None, "internal tool", "paused", date(2026, 2, 2)),
    ("Eval Harness", None, "internal tool", "active", date(2026, 3, 2)),
    ("Contract Q&A", "Merrow Law Group", "LLM app", "planned", date(2026, 11, 16)),
    ("Onboarding Wiki", None, "internal tool", "planned", date(2026, 12, 1)),
]

projects = []
work_end = {}  # last day work happened on each project (not stored in the CSV)
for i, (name, client, category, status, start) in enumerate(PROJECTS, start=1):
    if category == "internal tool":
        budget = random.randrange(15_000, 45_001, 2_500)
    else:
        budget = random.randrange(40_000, 200_001, 5_000)
    projects.append({
        "project_id": i, "name": name, "client_name": client,
        "category": category, "budget": budget,
        "start_date": start, "status": status,
    })
    if status == "done":
        work_end[i] = start + timedelta(days=random.randint(120, 180))
    elif status == "paused":
        work_end[i] = rand_date(start + timedelta(days=60), date(2026, 8, 31))
    else:  # active or planned
        work_end[i] = AS_OF
project_by_id = {p["project_id"]: p for p in projects}

# ----------------------------------------------------------- assignments
ROLES = ["engineer", "engineer", "designer", "analyst", "advisor"]
assignments = {}  # (person_id, project_id) -> dict


def first_possible_join(person, project):
    """The earliest day a person can join a project."""
    pid = project["project_id"]
    if project["status"] == "planned":  # planning work starts in October
        return max(person["start_date"], date(2026, 10, 1))
    return max(person["start_date"], project["start_date"])


def add_assignment(person, project, role, hours):
    lo = first_possible_join(person, project)
    hi = min(lo + timedelta(days=30), work_end[project["project_id"]])
    assignments[(person["person_id"], project["project_id"])] = {
        "person_id": person["person_id"],
        "project_id": project["project_id"],
        "role": role,
        "hours_per_week": hours,
        "joined_date": rand_date(lo, hi),
    }


def can_join(person, project):
    """Started early enough to do at least two weeks of work on it."""
    end = work_end[project["project_id"]]
    return first_possible_join(person, project) <= end - timedelta(days=14)


for project in projects:
    pid = project["project_id"]
    # the lead: a founder for internal tools, a manager or founder otherwise
    lead_pool = [1, 2] if project["client_name"] is None else [1, 2, 3, 4, 5, 6]
    leads = [person_by_id[i] for i in lead_pool if can_join(person_by_id[i], project)]
    add_assignment(random.choice(leads), project, "lead", random.choice([10, 15, 20]))
    # the rest of the team
    staff = [p for p in people[6:] if can_join(p, project)]
    for person in random.sample(staff, min(len(staff), random.randint(2, 5))):
        add_assignment(person, project, random.choice(ROLES),
                       random.choice([5, 8, 10, 12, 15, 20]))

# Three people work 25 hours a week on two active projects each: 50 hours
# in total, which question 3 should find.
active_ids = [p["project_id"] for p in projects if p["status"] == "active"]
for person_id in [8, 12, 17]:
    person = person_by_id[person_id]
    options = [pid for pid in active_ids if can_join(person, project_by_id[pid])]
    for pid in random.sample(options, 2):
        key = (person_id, pid)
        if key in assignments:
            assignments[key]["hours_per_week"] = 25
        else:
            add_assignment(person, project_by_id[pid], "engineer", 25)

# Everyone works on at least one project.
for person in people:
    if not any(pid_person == person["person_id"] for pid_person, _ in assignments):
        options = [pid for pid in active_ids if can_join(person, project_by_id[pid])]
        add_assignment(person, project_by_id[random.choice(options)], "engineer", 10)

# ------------------------------------------------------------------ tasks
VERBS = ["Draft", "Build", "Test", "Review", "Fix", "Document", "Deploy",
         "Clean", "Label", "Benchmark", "Refactor", "Demo"]
THINGS = ["prompt templates", "ingestion job", "evaluation set", "API endpoint",
          "client dashboard", "retrieval index", "data schema", "error handling",
          "onboarding flow", "cost report", "unit tests", "release notes"]

team = {}  # project_id -> list of assignment dicts
for a in assignments.values():
    team.setdefault(a["project_id"], []).append(a)

# about 300 tasks: 4 for each planned project, the rest shared out by
# how long work went on
planned_ids = [p["project_id"] for p in projects if p["status"] == "planned"]
worked_ids = [p["project_id"] for p in projects if p["status"] != "planned"]
days_worked = {pid: (work_end[pid] - project_by_id[pid]["start_date"]).days
               for pid in worked_ids}
remaining = 300 - 4 * len(planned_ids)
task_count = {pid: 4 for pid in planned_ids}
for pid in worked_ids:
    task_count[pid] = max(8, round(remaining * days_worked[pid] / sum(days_worked.values())))

tasks = []
for project in projects:
    pid, status = project["project_id"], project["status"]
    for _ in range(task_count[pid]):
        if status == "planned":
            created = rand_date(date(2026, 10, 5), AS_OF)
        else:
            created = rand_date(project["start_date"], work_end[pid])
        # nobody creates a task before anybody works on the project
        first_join = min(a["joined_date"] for a in team[pid])
        created = max(created, first_join)
        due = created + timedelta(days=random.randint(5, 40))

        # only someone already on the project can be assigned the task
        eligible = [a["person_id"] for a in team[pid] if a["joined_date"] <= created]
        recent = created >= AS_OF - timedelta(days=21)
        if not eligible or (recent and random.random() < 0.4):
            assignee = None  # a new task may be unassigned
        else:
            assignee = random.choice(eligible)

        completed = None
        if assignee is not None:
            if status == "done":
                hi = max(created, min(due + timedelta(days=10), work_end[pid]))
                completed = rand_date(created, hi)
            elif due <= work_end[pid] and random.random() < 0.85:
                hi = max(created, min(due + timedelta(days=10), work_end[pid]))
                completed = rand_date(created, hi)
            elif due > work_end[pid] and random.random() < 0.25:
                completed = rand_date(created, work_end[pid])
            # otherwise the task is still open, and past due if due < AS_OF

        tasks.append({
            "task_id": len(tasks) + 1, "project_id": pid,
            "description": f"{random.choice(VERBS)} {random.choice(THINGS)}",
            "created_date": created, "assignee_id": assignee,
            "due_date": due, "completed_date": completed,
        })

# --------------------------------------------------------------- expenses
# Planned projects have no expenses yet, so question 5 finds two projects.
AMOUNTS = {"GPU cloud": (400, 6000), "data labeling": (300, 4000),
           "software": (40, 1200), "travel": (120, 2200)}
CATEGORY_WEIGHTS = {
    "LLM app":       {"GPU cloud": 5, "data labeling": 3, "software": 2, "travel": 1},
    "data pipeline": {"GPU cloud": 1, "data labeling": 2, "software": 5, "travel": 1},
    "internal tool": {"GPU cloud": 1, "data labeling": 0, "software": 6, "travel": 0},
}
NOTES = {
    "GPU cloud": ["fine-tuning run", "inference hosting", "batch embeddings", "eval runs"],
    "data labeling": ["label 1,000 examples", "review labels", "annotation vendor"],
    "software": ["API credits", "monitoring tool", "vector database plan", "dev tools"],
    "travel": ["client visit", "train to client", "demo day travel"],
}

expenses = []
for _ in range(180):
    pid = random.choices(worked_ids, weights=[days_worked[p] for p in worked_ids])[0]
    project = project_by_id[pid]
    weights = CATEGORY_WEIGHTS[project["category"]]
    category = random.choices(list(weights), weights=list(weights.values()))[0]
    low, high = AMOUNTS[category]
    expenses.append({
        "expense_id": len(expenses) + 1, "project_id": pid,
        "expense_date": rand_date(project["start_date"], work_end[pid]),
        "amount": round(random.uniform(low, high), 2),
        "category": category, "note": random.choice(NOTES[category]),
    })
expenses.sort(key=lambda e: e["expense_date"])
for i, e in enumerate(expenses, start=1):
    e["expense_id"] = i

# ------------------------------------------- break one rule on purpose
# Question 7 checks that every task's assignee works on the task's project.
# Here two tasks are given to somebody who does NOT work on their project
# (but who had already started), so that question 7 has two rows to find.
candidates = [t for t in tasks if t["assignee_id"] is not None]
broken = []
for t in random.sample(candidates, 2):
    outsiders = [p["person_id"] for p in people
                 if (p["person_id"], t["project_id"]) not in assignments
                 and p["start_date"] <= t["created_date"]]
    t["assignee_id"] = random.choice(outsiders)
    broken.append(t["task_id"])
for task_id in broken:
    t = tasks[task_id - 1]
    print(f"Rule broken on purpose: task {task_id} (project {t['project_id']}) "
          f"is assigned to person {t['assignee_id']}, who does not work on it")

# --------------------------------------------- check the rules before writing
for p in people:
    assert p["manager_id"] is None or p["manager_id"] < p["person_id"]
assert sum(p["manager_id"] is None for p in people) == 2
assert len({p["work_email"] for p in people}) == len(people)
for p in projects:
    assert p["budget"] > 0
    assert p["status"] in {"planned", "active", "paused", "done"}
for a in assignments.values():
    assert 1 <= a["hours_per_week"] <= 40
    assert a["joined_date"] >= person_by_id[a["person_id"]]["start_date"]
for t in tasks:
    assert FIRST_DAY <= t["created_date"] <= AS_OF
    if t["completed_date"] is not None:
        assert t["created_date"] <= t["completed_date"] <= AS_OF
    if t["assignee_id"] is not None and t["task_id"] not in broken:
        assert (t["assignee_id"], t["project_id"]) in assignments
        assert person_by_id[t["assignee_id"]]["start_date"] <= t["created_date"]
for e in expenses:
    assert FIRST_DAY <= e["expense_date"] <= AS_OF
    assert e["amount"] > 0
    assert e["category"] in AMOUNTS
assert len(projects) >= 12 and len(tasks) >= 250 and len(expenses) >= 150

# ----------------------------------------------------------------- write
DATA_DIR.mkdir(exist_ok=True)


def write_csv(name, rows):
    with open(DATA_DIR / f"{name}.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "" if v is None else v for k, v in row.items()})


write_csv("people", people)
write_csv("projects", projects)
write_csv("assignments", sorted(assignments.values(),
                                key=lambda a: (a["project_id"], a["person_id"])))
write_csv("tasks", tasks)
write_csv("expenses", expenses)

print(f"Wrote {len(people)} people, {len(projects)} projects, "
      f"{len(assignments)} assignments, {len(tasks)} tasks and "
      f"{len(expenses)} expenses to {DATA_DIR}")