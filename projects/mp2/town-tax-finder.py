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


@app.cell
def _():
    county = "Middlesex"
    budget_dollars = 700000
    tax_limit_dollars = 8000
    fiscal_year = 2026
    return budget_dollars, county, fiscal_year, tax_limit_dollars


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. The Work
    """)
    return


@app.cell
def _():
    import requests

    BASE_URL = "https://oim.zhili.dev"

    def get_towns(county):
        """Return every town in a county as a list of records."""
        towns = []
        page = 1
        while True:
            reply = requests.get(
                f"{BASE_URL}/ma/towns",
                params={"county": county, "page": page, "per_page": 100},
            )
            reply.raise_for_status()
            data = reply.json()
            for item in data["items"]:
                towns.append(item)
            if not data["pagination"]["has_next"]:
                break
            page = page + 1
        return towns

    return BASE_URL, get_towns, requests


@app.cell
def _(county, get_towns):
    towns = get_towns(county)
    print(f"Collected {len(towns)} towns in {county} County")
    return (towns,)


@app.cell
def _(BASE_URL, requests):
    def get_town_year(dor_code, fiscal_year):
        """Return one town's figures for one fiscal year, or None if that year is missing."""
        reply = requests.get(f"{BASE_URL}/ma/towns/{dor_code}/history")
        reply.raise_for_status()
        data = reply.json()
        for year in data["years"]:
            if year["fiscal_year"] == fiscal_year:
                return {
                    "dor_code": data["dor_code"],
                    "name": data["name"],
                    "fiscal_year": year["fiscal_year"],
                    "home_value": year["average_single_family_value_dollars"],
                    "tax_rate": year["residential_rate_per_thousand"],
                    "avg_bill": year["average_single_family_bill_dollars"],
                }
        return None

    return (get_town_year,)


@app.cell
def _(fiscal_year, get_town_year, towns):
    records = []
    missing = []
    for _town in towns:
        _figures = get_town_year(_town["dor_code"], fiscal_year)
        if _figures is None:
            missing.append(_town["name"])
        else:
            records.append(_figures)

    print(f"Got {fiscal_year} figures for {len(records)} towns; missing for {len(missing)}: {missing}")
    return (records,)


@app.cell
def _(county, fiscal_year, mo, records):
    import json

    data_dir = mo.notebook_dir() / "data"
    data_dir.mkdir(exist_ok=True)
    data_file = data_dir / f"{county.lower()}_{fiscal_year}.json"

    with open(data_file, "w") as _f:
        json.dump(records, _f, indent=2)

    print(f"Saved {len(records)} records to {data_file}")
    return


@app.cell
def _():
    def bill_of(record):
        return record["avg_bill"]

    def filter_and_sort(records, budget, tax_limit):
        """Return the towns that fit both limits, lowest bill first."""
        passing = []
        for record in records:
            if record["home_value"] is None or record["avg_bill"] is None:
                continue
            if record["home_value"] <= budget and record["avg_bill"] <= tax_limit:
                passing.append(record)
        return sorted(passing, key=bill_of)

    return (filter_and_sort,)


@app.cell
def _(budget_dollars, filter_and_sort, records, tax_limit_dollars):
    shortlist = filter_and_sort(records, budget_dollars, tax_limit_dollars)
    print(f"{len(shortlist)} of {len(records)} towns pass both limits")
    return (shortlist,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. The Answer
    """)
    return


@app.cell
def _(shortlist):
    print(f"{'Town':<20} {'Avg home value':>14} {'Tax rate':>10} {'Avg bill':>10}")
    print("-" * 57)
    for _town in shortlist:
        _value = "$" + format(_town["home_value"], ",")
        _bill = "$" + format(_town["avg_bill"], ",")
        print(f"{_town['name']:<20} {_value:>14} {_town['tax_rate']:>10.2f} {_bill:>10}")
    return


@app.cell
def _(
    budget_dollars,
    county,
    fiscal_year,
    records,
    shortlist,
    tax_limit_dollars,
):
    if len(shortlist) > 0:
        _best = shortlist[0]
        print(
            f"Of the {len(records)} towns in {county} County, {len(shortlist)} have an average "
            f"single-family home at or under ${budget_dollars:,} and an average tax bill at or under "
            f"${tax_limit_dollars:,} in fiscal {fiscal_year}. The lowest bill is in {_best['name']}: "
            f"${_best['avg_bill']:,} a year on an average home of ${_best['home_value']:,}."
        )
    else:
        print(f"No town in {county} County fits both a ${budget_dollars:,} budget and a ${tax_limit_dollars:,} tax limit in fiscal {fiscal_year}.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. How I Know These Numbers Are Right
    """)
    return


@app.cell
def _(BASE_URL, county, requests, towns):
    _reply = requests.get(f"{BASE_URL}/ma/towns", params={"county": county})
    _reply.raise_for_status()
    api_total = _reply.json()["pagination"]["total"]

    print(f"Towns the API reports: {api_total}")
    print(f"Towns I collected:     {len(towns)}")
    print(f"Match: {api_total == len(towns)}")
    return


@app.cell
def _(shortlist):
    print(f"{'Town':<20} {'API bill':>10} {'Calculated':>12} {'Difference':>11}")
    print("-" * 56)
    largest_gap = 0
    for _town in shortlist:
        _calculated = _town["home_value"] * _town["tax_rate"] / 1000
        _gap = abs(_town["avg_bill"] - _calculated)
        if _gap > largest_gap:
            largest_gap = _gap
        print(f"{_town['name']:<20} {_town['avg_bill']:>10,} {_calculated:>12,.0f} {_gap:>11,.2f}")
    print(f"Largest difference: ${largest_gap:,.2f}")
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
    The code for fetching, filtering and printing worked on the first run, so I did not change it. To verify it, I checked in section 6 that the number of towns I collected (54) equals the total the API reports (54), and that every bill in my table matches the home value × tax rate ÷ 1,000 within about a dollar.
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
    The first function, get_towns(county), takes a county name, like Middlesex, and returns a list of all the towns in that county, including their names and DOR codes. I had to ask about the line if not data["pagination"]["has_next"]: break. I learned that this checks whether there are more pages of towns to collect. If there are no more pages, the function stops looking and returns the list.

    The second function, get_town_year(dor_code, fiscal_year), takes a town’s DOR code and a year, and returns that town’s home value, tax rate and average tax bill for that year. I had to ask about the line return None. I learned that this happens when the function cannot find information for the year I requested. Instead of giving an error, it returns None, so I can keep track of which towns are missing information.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Prediction: I will lower budget_dollars from $700,000 to $600,000. Looking at my current table, Billerica and Marlborough have average home values above $600,000, so I expect them to drop out. That leaves 10 towns. The cheapest bill should still be Malden at $4,952, so the answer sentence should name the same town but say 10 towns instead of 12.


    Update: I made the change, ran it, and it did exactly that.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Going Further
    """)
    return


@app.cell
def _(shortlist):
    def rate_of(record):
        return record["tax_rate"]

    by_rate = sorted(shortlist, key=rate_of)

    print(f"{'Rate rank':<10} {'Town':<14} {'Tax rate':>8} {'Avg home value':>15} {'Avg bill':>9} {'Bill rank':>10}")
    print("-" * 71)
    for _i, _town in enumerate(by_rate):
        _bill_rank = shortlist.index(_town) + 1
        _value = "$" + format(_town["home_value"], ",")
        _bill = "$" + format(_town["avg_bill"], ",")
        print(f"{_i + 1:<10} {_town['name']:<14} {_town['tax_rate']:>8.2f} {_value:>15} {_bill:>9} {_bill_rank:>10}")
    return


@app.cell
def _(BASE_URL, requests):
    def get_town_history(dor_code, first_year, last_year):
        """Return one town's average bill for each year from first_year to last_year, skipping years with no bill."""
        reply = requests.get(f"{BASE_URL}/ma/towns/{dor_code}/history")
        reply.raise_for_status()
        data = reply.json()
        rows = []
        for year in data["years"]:
            in_range = first_year <= year["fiscal_year"] <= last_year
            has_bill = year["average_single_family_bill_dollars"] is not None
            if in_range and has_bill:
                rows.append({
                    "name": data["name"],
                    "fiscal_year": year["fiscal_year"],
                    "avg_bill": year["average_single_family_bill_dollars"],
                })
        return rows

    return (get_town_history,)


@app.cell
def _(fiscal_year, get_town_history, shortlist):
    trend_rows = []
    print(f"{'Town':<14} {'From':>12} {'To':>12} {'Change':>8}")
    print("-" * 49)
    for _town in shortlist[:3]:
        _rows = get_town_history(_town["dor_code"], fiscal_year - 9, fiscal_year)
        for _row in _rows:
            trend_rows.append(_row)
        _first = _rows[0]
        _last = _rows[-1]
        _change = (_last["avg_bill"] - _first["avg_bill"]) / _first["avg_bill"] * 100
        _from = f"{_first['fiscal_year']}: ${_first['avg_bill']:,}"
        _to = f"{_last['fiscal_year']}: ${_last['avg_bill']:,}"
        print(f"{_town['name']:<14} {_from:>12} {_to:>12} {_change:>7.1f}%")
    return (trend_rows,)


@app.cell
def _(trend_rows):
    import altair as alt

    alt.Chart(alt.Data(values=trend_rows)).mark_line(point=True).encode(
        x=alt.X("fiscal_year:O", title="Fiscal year"),
        y=alt.Y("avg_bill:Q", title="Average single-family tax bill ($)"),
        color=alt.Color("name:N", title="Town"),
    ).properties(title="Average tax bill over 10 years, three cheapest towns", width=600)

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    What I tried (both are in this section):

    1.Ranking by tax rate. Sorted by tax rate, the order changes: Dracut has the lowest rate but only the 3rd-lowest bill, while Malden has the lowest bill but ranks 5th by rate. The bill depends on both the rate and the home’s value, so for the couple the bill matters more than the rate.

    2.Ten-year trend. I charted the average bill for the three cheapest towns. Dracut has data for all 10 years and its bill rose 29.2% since 2017. Malden and Waltham only have bills from 2022, so their increases (15.8% and 12.0%) cover five years and can’t be compared directly with Dracut’s. The chart also shows the order changing: Malden’s bill was higher than Waltham’s in 2024 and 2025, and it only became the cheapest in 2026 because it stayed flat that year. So today’s cheapest town is not always the cheapest.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Time Spent
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    3 hours and 5 minutes!
    """)
    return


if __name__ == "__main__":
    app.run()
