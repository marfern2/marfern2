"""Generate compact profile SVGs from GitHub's contribution calendar and user API."""

import html
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen


USERNAME = "marfern2"
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = Path("dist")
MONO = "'Courier New', monospace"


def get_json(url, payload=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {TOKEN}",
        "User-Agent": "marfern2-profile-assets",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = json.dumps(payload).encode() if payload is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    with urlopen(Request(url, data=data, headers=headers), timeout=25) as response:
        return json.load(response)


def svg(body, width, height, title):
    title = html.escape(title)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">'
        f'<title>{title}</title><rect x="1" y="1" width="{width - 2}" '
        f'height="{height - 2}" fill="#171b18" stroke="#a9c5ae" stroke-width="2"/>'
        f'{body}</svg>'
    )


def render_stats(total, public_repos, followers):
    metrics = [
        (total, "CONTRIB / 84D"),
        (public_repos, "PUBLIC REPOS"),
        (followers, "FOLLOWERS"),
    ]
    parts = [
        f'<text x="14" y="25" fill="#a9c5ae" font-family="{MONO}" '
        'font-size="14" font-weight="700">PLAYER STATS / GITHUB</text>'
    ]
    for index, (value, label) in enumerate(metrics):
        x = 14 + index * 135
        parts.append(
            f'<rect x="{x}" y="36" width="122" height="62" fill="#26352b"/>'
            f'<text x="{x + 10}" y="69" fill="#f3cb54" font-family="{MONO}" '
            f'font-size="26" font-weight="700">{value}</text>'
            f'<text x="{x + 10}" y="88" fill="#f7f2e7" font-family="{MONO}" '
            f'font-size="11" font-weight="700">{label}</text>'
        )
    return svg("".join(parts), 420, 112, "Estadísticas de GitHub")


def render_activity(days, counts):
    weekly = [sum(counts[index : index + 7]) for index in range(0, 84, 7)]
    peak = max(weekly + [1])
    parts = [
        f'<text x="22" y="28" fill="#f7f2e7" font-family="{MONO}" '
        'font-size="16" font-weight="700">12-WEEK ACTIVITY</text>',
        f'<text x="22" y="47" fill="#a9c5ae" font-family="{MONO}" '
        'font-size="11">GITHUB CONTRIBUTIONS / UTC</text>',
        '<path d="M30 172H570M30 119H570M30 66H570" '
        'stroke="#3d5545" stroke-width="1"/>',
    ]
    for index, value in enumerate(weekly):
        x = 35 + index * 45
        height = round(104 * value / peak) if value else 0
        if height:
            parts.append(
                f'<rect x="{x}" y="{172 - height}" width="30" height="{height}" '
                'fill="#ef6738"/>'
            )
        parts.append(
            f'<text x="{x + 15}" y="{max(59, 165 - height)}" '
            f'fill="#f7f2e7" font-family="{MONO}" font-size="10" '
            f'text-anchor="middle">{value}</text>'
        )
        if index in (0, 3, 6, 9, 11):
            date_label = days[index * 7].strftime("%d %b").upper()
            parts.append(
                f'<text x="{x + 15}" y="193" fill="#a9c5ae" '
                f'font-family="{MONO}" font-size="10" '
                f'text-anchor="middle">{date_label}</text>'
            )
    return svg("".join(parts), 600, 210, "Contribuciones de las últimas doce semanas")


def main():
    query = (
        "query($login: String!) { user(login: $login) { contributionsCollection "
        "{ contributionCalendar { weeks { contributionDays "
        "{ date contributionCount } } } } } }"
    )
    result = get_json(
        "https://api.github.com/graphql",
        {"query": query, "variables": {"login": USERNAME}},
    )
    if result.get("errors") or not result.get("data", {}).get("user"):
        raise RuntimeError(f"GitHub GraphQL calendar unavailable: {result.get('errors')}")
    calendar = result["data"]["user"]["contributionsCollection"][
        "contributionCalendar"
    ]["weeks"]
    by_day = {
        day["date"]: int(day["contributionCount"])
        for week in calendar
        for day in week["contributionDays"]
    }
    today = datetime.now(timezone.utc).date()
    days = [today - timedelta(days=83 - index) for index in range(84)]
    if any(day.isoformat() not in by_day for day in days):
        raise RuntimeError("GitHub calendar is missing days from the 84-day window")
    counts = [by_day[day.isoformat()] for day in days]
    user = get_json(f"https://api.github.com/users/{USERNAME}")
    if user.get("login", "").lower() != USERNAME:
        raise RuntimeError("GitHub user API returned an unexpected account")
    OUT.mkdir(exist_ok=True)
    (OUT / "player-stats.svg").write_text(
        render_stats(sum(counts), user["public_repos"], user["followers"]),
        encoding="utf-8",
    )
    (OUT / "activity-graph.svg").write_text(
        render_activity(days, counts), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
