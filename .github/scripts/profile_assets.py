"""Render compact, theme-aware profile metrics from public GitHub API data."""

from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen


USERNAME = "marfern2"
OUT = Path("dist")
WIDTH = 390
HEIGHT = 190
FONT = "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
THEMES = {
    "dark": {
        "background": "#0d1117", "panel": "#161b22", "border": "#30363d",
        "text": "#e6edf3", "muted": "#8b949e", "green": "#3fb950", "blue": "#58a6ff",
    },
    "light": {
        "background": "#ffffff", "panel": "#f6f8fa", "border": "#d0d7de",
        "text": "#1f2328", "muted": "#57606a", "green": "#1a7f37", "blue": "#0969da",
    },
}


def get_json(url, payload=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "User-Agent": "marfern2-profile-metrics",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    data = json.dumps(payload).encode() if payload is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    with urlopen(Request(url, data=data, headers=headers), timeout=25) as response:
        return json.load(response)


def label(x, y, value, size, color, weight=400, anchor=None):
    align = f' text-anchor="{anchor}"' if anchor else ""
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}"{align}>{escape(str(value))}</text>'
    )


def canvas(title, body, theme):
    color = THEMES[theme]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(title)}">'
        f'<title>{escape(title)}</title>'
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" '
        f'rx="10" fill="{color["background"]}" stroke="{color["border"]}"/>'
        f'{body}</svg>\n'
    )


def fetch_contributions():
    now = datetime.now(timezone.utc)
    start = now.date() - timedelta(days=83)
    query = (
        "query($login: String!, $from: DateTime!, $to: DateTime!) { "
        "user(login: $login) { contributionsCollection(from: $from, to: $to) { "
        "totalCommitContributions contributionCalendar { weeks { contributionDays "
        "{ date contributionCount } } } } } }"
    )
    result = get_json(
        "https://api.github.com/graphql",
        {"query": query, "variables": {
            "login": USERNAME,
            "from": f"{start.isoformat()}T00:00:00Z",
            "to": now.isoformat(timespec="seconds").replace("+00:00", "Z"),
        }},
    )
    if result.get("errors") or not result.get("data", {}).get("user"):
        raise RuntimeError(f"GitHub contribution data unavailable: {result.get('errors')}")
    collection = result["data"]["user"]["contributionsCollection"]
    calendar = collection["contributionCalendar"]["weeks"]
    by_day = {
        day["date"]: int(day["contributionCount"])
        for week in calendar for day in week["contributionDays"]
    }
    dates = [start + timedelta(days=index) for index in range(84)]
    if any(day.isoformat() not in by_day for day in dates):
        raise RuntimeError("GitHub calendar is missing dates in the 84-day window")
    counts = [by_day[day.isoformat()] for day in dates]
    return dates, counts, int(collection["totalCommitContributions"])


def fetch_public_languages():
    user = get_json(f"https://api.github.com/users/{USERNAME}")
    if user.get("login", "").lower() != USERNAME:
        raise RuntimeError("GitHub user API returned an unexpected account")
    repos = []
    page = 1
    while True:
        batch = get_json(
            f"https://api.github.com/users/{USERNAME}/repos?type=owner&per_page=100&page={page}"
        )
        if not isinstance(batch, list):
            raise RuntimeError("GitHub repository API returned an unexpected response")
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    languages = Counter()
    for repo in repos:
        if repo["fork"] or repo["private"]:
            continue
        name = quote(repo["name"], safe="")
        response = get_json(f"https://api.github.com/repos/{USERNAME}/{name}/languages")
        languages.update({language: int(size) for language, size in response.items()})
    return int(user["public_repos"]), int(user["followers"]), languages


def render_dashboard(public_repos, followers, dates, counts, commits, theme):
    c = THEMES[theme]
    total = sum(counts)
    values = [
        (public_repos, "PUBLIC REPOS"), (followers, "FOLLOWERS"),
        (total, "CONTRIB."), (commits, "COMMITS"),
    ]
    parts = [label(18, 28, "GitHub overview", 17, c["text"], 650),
             label(372, 27, "ACTIVITY: 84D", 10, c["muted"], 650, "end")]
    for index, (value, caption) in enumerate(values):
        x = 18 + index * 92
        parts.append(f'<rect x="{x}" y="42" width="84" height="54" rx="6" fill="{c["panel"]}"/>')
        parts.append(label(x + 8, 68, value, 22, c["text"], 650))
        parts.append(label(x + 8, 85, caption, 11, c["muted"], 600))
    parts.append(label(18, 115, "Contributions / last 12 weeks", 11, c["muted"], 500))
    weekly = [sum(counts[index:index + 7]) for index in range(0, 84, 7)]
    peak = max(weekly, default=0) or 1
    for index, amount in enumerate(weekly):
        x = 20 + index * 30
        height = max(2, round(38 * amount / peak)) if amount else 2
        color = c["green"] if amount else c["border"]
        parts.append(
            f'<rect x="{x}" y="{160 - height}" width="20" height="{height}" '
            f'rx="2" fill="{color}"/>'
        )
    parts.append(label(18, 178, dates[0].strftime("%d %b"), 10, c["muted"]))
    parts.append(label(372, 178, dates[-1].strftime("%d %b %Y"), 10, c["muted"], anchor="end"))
    return canvas("GitHub overview, public data and 84-day contributions", "".join(parts), theme)


def render_languages(languages, theme):
    c = THEMES[theme]
    total = sum(languages.values())
    parts = [
        label(18, 28, "Languages in public repos", 17, c["text"], 650),
        label(18, 46, "Non-fork repos · GitHub Linguist bytes", 11, c["muted"]),
    ]
    if total:
        top = languages.most_common(5)
        other = total - sum(size for _, size in top)
        if other:
            top.append(("Other", other))
        for index, (name, size) in enumerate(top):
            y = 70 + index * 18
            share = size / total
            parts.append(label(18, y, name, 11, c["text"], 500))
            parts.append(f'<rect x="132" y="{y - 8}" width="186" height="7" rx="3" fill="{c["panel"]}"/>')
            parts.append(f'<rect x="132" y="{y - 8}" width="{max(2, round(186 * share))}" height="7" rx="3" fill="{c["blue"]}"/>')
            parts.append(label(372, y, f"{share:.1%}", 10, c["muted"], anchor="end"))
    else:
        parts.append(label(18, 92, "No language data in public repositories", 12, c["muted"]))
    parts.append(label(18, 179, "Code share, not a skill rating", 10, c["muted"]))
    return canvas("Most used languages in public non-fork repositories", "".join(parts), theme)


def main():
    dates, counts, commits = fetch_contributions()
    public_repos, followers, languages = fetch_public_languages()
    OUT.mkdir(exist_ok=True)
    for theme in THEMES:
        (OUT / f"dashboard-{theme}.svg").write_text(
            render_dashboard(public_repos, followers, dates, counts, commits, theme),
            encoding="utf-8",
        )
        (OUT / f"languages-{theme}.svg").write_text(
            render_languages(languages, theme), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
