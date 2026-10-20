"""Build the small, self-contained SVG panels used by the profile README."""

from html import escape
from pathlib import Path


OUT = Path(__file__).resolve().parents[2] / "assets"
BG = "#171b18"
PANEL = "#213127"
EDGE = "#a9c5ae"
WHITE = "#f7f2e7"
ORANGE = "#ef6738"
GOLD = "#f3cb54"
GREEN = "#9ddbb1"
MUTED = "#a9c5ae"
FONT = "'Courier New', monospace"


def rect(x, y, width, height, fill, stroke=None, sw=1):
    border = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="{fill}"{border}/>'


def line(x1, y1, x2, y2, color=EDGE, sw=1):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{color}" stroke-width="{sw}"/>' if y1 == y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="{sw}" fill="none"/>'


def text(x, y, value, size=13, color=WHITE, weight="normal", anchor=None):
    align = f' text-anchor="{anchor}"' if anchor else ""
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}" fill="{color}"{align}>{escape(value)}</text>')


def svg(name, width, height, label, parts):
    title = escape(label)
    data = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">'
            f'<title>{title}</title>{"".join(parts)}</svg>\n')
    (OUT / name).write_text(data, encoding="utf-8")


def panel(width, height, heading, accent=ORANGE):
    return [
        rect(1, 1, width - 2, height - 2, BG, EDGE, 2),
        rect(2, 2, width - 4, 32, PANEL),
        rect(12, 13, 7, 7, accent),
        rect(23, 13, 7, 7, GOLD),
        text(40, 23, heading, 13, WHITE, "bold"),
        line(2, 34, width - 2, 34, EDGE, 2),
    ]


def button(name, label, width, accent=ORANGE, subtitle=None):
    height = 56 if subtitle else 40
    parts = [
        rect(1, 1, width - 2, height - 2, BG, EDGE, 2),
        rect(5, 5, 5, height - 10, accent),
        rect(width - 13, 7, 5, 5, GOLD),
        rect(width - 13, height - 12, 5, 5, accent),
        text(17, 25 if subtitle else 26, label, 13 if subtitle else 12.5, WHITE, "bold"),
    ]
    if subtitle:
        parts.append(text(17, 43, subtitle, 12, GREEN, "bold"))
    svg(name, width, height, f"Botón {label}" + (f", {subtitle}" if subtitle else ""), parts)


def quest(name, number, title, rows, stack):
    parts = panel(320, 194, f"QUEST {number} / MAIN", GOLD)
    title_size = 17 if len(title) > 18 else 22
    parts += [
        text(16, 62, title, title_size, WHITE, "bold"),
        line(16, 72, 304, 72, "#3d5545"),
    ]
    for index, (key, value) in enumerate(rows):
        y = 92 + index * 23
        parts += [text(16, y, key, 11, MUTED, "bold"),
                  text(103, y, value, 12 if len(value) < 22 else 11.5, GREEN, "bold")]
    parts += [rect(10, 173, 300, 15, PANEL), text(16, 185, stack, 10.5, GOLD)]
    svg(name, 320, 194, f"Misión {number}: {title}. " + ". ".join(f"{key}: {value}" for key, value in rows), parts)


def hud():
    rows = [
        ("CLASS", "FULL-STACK DEVELOPER"),
        ("MAIN", "JAVA / SPRING BOOT"),
        ("OS", "LINUX"),
        ("LOCATION", "MADRID, SPAIN"),
        ("ACADEMY", "42 MADRID"),
        ("STATUS", "BUILDING..."),
    ]
    parts = panel(320, 229, "PLAYER STATUS")
    for index, (key, value) in enumerate(rows):
        y = 58 + index * 29
        if index % 2 == 0:
            parts.append(rect(10, y - 17, 300, 27, PANEL))
        parts += [text(18, y, key, 11.5, MUTED, "bold"),
                  text(107, y, value, 12, GREEN if key == "STATUS" else WHITE, "bold")]
    parts += [rect(291, 206, 7, 7, GREEN)]
    svg("player-hud.svg", 320, 229, "Player status: desarrollador full-stack, Java y Spring Boot, Linux, Madrid, 42 Madrid", parts)


def system_status():
    rows = [
        ("portfolio", "ONLINE"),
        ("donit", "PRODUCTION"),
        ("github", "CONNECTED"),
        ("current_quest", "42 MADRID"),
        ("main_stack", "JAVA + SPRING BOOT"),
    ]
    parts = panel(320, 183, "SYSTEM STATUS", GREEN)
    for index, (key, value) in enumerate(rows):
        y = 56 + index * 25
        parts += [text(14, y, ">", 13, ORANGE, "bold"),
                  text(29, y, key, 11.5, MUTED),
                  text(302, y, value, 11.5, GREEN if index < 3 else WHITE, "bold", "end")]
    svg("system-status.svg", 320, 183, "Estado: portfolio online, Donit en producción, GitHub conectado, 42 Madrid, Java y Spring", parts)


def chip(x, y, label):
    width = 18 + len(label) * 7
    return width, [rect(x, y, width, 21, PANEL, "#3d5545"),
                   rect(x + 4, y + 7, 5, 5, GOLD),
                   text(x + 13, y + 15, label, 11, WHITE, "bold")]


def inventory():
    sections = [
        ("BACKEND", [["JAVA", "SPRING BOOT", "SECURITY"], ["REST API", "JPA", "HIBERNATE", "JWT"]]),
        ("FRONTEND", [["ANGULAR", "TYPESCRIPT", "HTML"], ["CSS"]]),
        ("MOBILE", [["KOTLIN", "ANDROID"], ["JETPACK COMPOSE"]]),
        ("DATA", [["POSTGRESQL", "SQL", "FLYWAY"]]),
        ("INFRASTRUCTURE", [["DOCKER", "LINUX", "AWS"], ["CLOUDFLARE", "GITHUB ACTIONS"]]),
        ("TOOLS", [["GIT", "GITHUB", "PYTHON"], ["PLAYWRIGHT", "C#", ".NET"]]),
    ]
    y = 44
    items = []
    for name, chip_rows in sections:
        section_height = 26 + 25 * len(chip_rows)
        items += [rect(10, y, 300, section_height, BG, "#3d5545"),
                  rect(10, y, 4, section_height, ORANGE),
                  text(22, y + 17, name, 11.5, GOLD, "bold")]
        for row_index, labels in enumerate(chip_rows):
            x = 20
            row_y = y + 23 + row_index * 25
            for label in labels:
                width, elements = chip(x, row_y, label)
                if x + width > 304:
                    raise ValueError(f"Inventory row too wide: {name} {labels}")
                items.extend(elements)
                x += width + 5
        y += section_height + 5
    parts = panel(320, y + 6, "TECH INVENTORY", GOLD) + items
    svg("tech-inventory.svg", 320, y + 6, "Inventario tecnológico por categorías: backend, frontend, mobile, data, infrastructure y tools", parts)


def node(parts, x, y, width, label, small=False):
    parts += [rect(x, y, width, 31, PANEL, EDGE),
              text(x + width / 2, y + 20, label, 11 if small else 12, WHITE, "bold", "middle")]


def skill_tree():
    parts = panel(320, 280, "SKILL TREE", GOLD)
    parts += [line(160, 72, 77, 92, "#3d5545", 2), line(160, 72, 243, 92, "#3d5545", 2),
              line(77, 123, 43, 145, "#3d5545", 2), line(77, 123, 117, 145, "#3d5545", 2),
              line(243, 123, 205, 145, "#3d5545", 2), line(243, 123, 277, 145, "#3d5545", 2)]
    node(parts, 94, 43, 132, "FULL-STACK")
    node(parts, 20, 92, 114, "BACKEND")
    node(parts, 186, 92, 114, "CLIENT")
    for x, label in [(12, "JAVA"), (90, "DATA"), (168, "WEB"), (246, "MOBILE")]:
        node(parts, x, 145, 63, label, True)
    for x, label in [(8, "SPRING"), (87, "POSTGRES"), (166, "ANGULAR"), (245, "KOTLIN")]:
        parts.append(text(x, 194, label, 10.5, GREEN, "bold"))
    parts += [line(44, 199, 44, 220, "#3d5545", 2),
              rect(16, 220, 288, 42, PANEL, "#3d5545"),
              text(160, 239, "SECURITY", 11.5, GOLD, "bold", "middle"),
              text(160, 255, "JWT / OAUTH", 10.5, WHITE, "bold", "middle")]
    svg("skill-tree.svg", 320, 280, "Árbol de habilidades: full-stack; backend Java, Spring, datos PostgreSQL y seguridad; cliente Angular y Kotlin", parts)


def terminal():
    parts = panel(320, 234, "TERMINAL / MARCOS@DEV", GREEN)
    commands = [
        ("whoami", "Full-Stack Developer"),
        ("cat main-stack", "Java + Spring Boot"),
        ("uptime", "Always building something."),
        ("open portfolio", "https://marfern.dev"),
    ]
    for index, (command, output) in enumerate(commands):
        y = 55 + index * 44
        parts += [text(14, y, "marcos@dev:~$", 11.5, GREEN, "bold"),
                  text(126, y, command, 11.5, WHITE),
                  text(14, y + 18, output, 12, GOLD)]
    parts.append(rect(14, 222, 7, 3, GREEN))
    svg("terminal.svg", 320, 234, "Terminal: desarrollador full-stack, Java y Spring Boot, construyendo proyectos, marfern.dev", parts)


def achievements():
    items = [
        ("DoNit TFG", "RESULT 10/10"),
        ("Donit v1.0.0", "PRODUCTION"),
        ("marfern.dev", "DEPLOYED"),
        ("42 Madrid", "COMMON CORE"),
        ("AWS", "EC2 + RDS DEPLOYMENT"),
        ("Docker", "CONTAINERIZED APPS"),
    ]
    parts = panel(320, 330, "ACHIEVEMENTS UNLOCKED", GOLD)
    for index, (name, detail) in enumerate(items):
        y = 42 + index * 47
        parts += [rect(10, y, 300, 43, PANEL, "#3d5545"),
                  rect(19, y + 12, 15, 15, GOLD), rect(23, y + 8, 7, 23, GOLD),
                  text(44, y + 17, name, 13, WHITE, "bold"),
                  text(44, y + 34, detail, 10.5, GREEN, "bold")]
    svg("achievements.svg", 320, 330, "Logros reales: DoNit TFG 10/10, Donit en producción, portfolio desplegado, 42 Madrid, AWS EC2 y RDS, Docker", parts)


def current_quest():
    items = ["Backend architecture", "Testing", "Security", "Donit evolution", "Playwright automation"]
    parts = panel(320, 248, "CURRENT QUEST", ORANGE)
    parts += [rect(12, 44, 296, 57, PANEL, "#3d5545"),
              rect(21, 53, 51, 17, GREEN), text(46, 66, "ACTIVE", 10, BG, "bold", "middle"),
              text(21, 88, "42 MADRID / COMMON CORE", 14, WHITE, "bold"),
              text(16, 121, "SIDE QUESTS", 12, GOLD, "bold")]
    for index, item in enumerate(items):
        y = 145 + index * 19
        parts += [rect(18, y - 8, 6, 6, ORANGE), text(32, y, item, 12, WHITE)]
    svg("current-quest.svg", 320, 248, "Misión actual: 42 Madrid Common Core. Misiones secundarias: arquitectura backend, testing, seguridad, evolución de Donit y Playwright", parts)


def divider(name, label, accent):
    parts = [line(2, 12, 318, 12, "#3d5545", 2), rect(2, 8, 9, 9, accent),
             rect(309, 8, 9, 9, accent), rect(38, 5, 244, 14, BG),
             text(160, 16, label, 11, accent, "bold", "middle")]
    svg(name, 320, 24, f"Separador {label}", parts)


def main():
    OUT.mkdir(exist_ok=True)
    for args in [
        ("button-enter-portfolio.svg", "ENTER PORTFOLIO", 214, ORANGE, None),
        ("button-player-profile.svg", "PLAYER PROFILE", 166, GREEN, None),
        ("button-case-study.svg", "VIEW CASE STUDY", 176, ORANGE, None),
        ("button-backend.svg", "BACKEND", 122, GREEN, None),
        ("button-android.svg", "ANDROID", 122, GREEN, None),
        ("button-admin.svg", "ADMIN", 122, GREEN, None),
        ("button-open-website.svg", "OPEN WEBSITE", 162, ORANGE, None),
        ("button-open-repository.svg", "OPEN REPOSITORY", 192, GREEN, None),
        ("button-github.svg", "GITHUB", 118, GREEN, None),
        ("button-portal.svg", "ENTER PORTFOLIO", 256, ORANGE, "MARFERN.DEV"),
    ]:
        button(*args)
    quest("quest-donit.svg", "01", "DONIT v1.0.0",
          [("STATUS", "PRODUCTION"), ("ROLE", "FULL-STACK DEVELOPER"),
           ("TYPE", "FULL-STACK APPLICATION")], "JAVA  SPRING  ANGULAR  KOTLIN")
    quest("quest-donit-tfg.svg", "02", "DoNit TFG",
          [("STATUS", "COMPLETED"), ("RESULT", "10/10"),
           ("ROLE", "FULL-STACK DEVELOPER"),
           ("TYPE", "FINAL DEGREE PROJECT")], "SPRING  ANDROID  POSTGRES  AWS")
    quest("quest-trending-radar.svg", "03", "GITHUB TRENDING RADAR",
          [("TYPE", "PYTHON AUTOMATION"), ("SOURCE", "GITHUB TRENDS"),
           ("OUTPUT", "CSV EXPORT")], "PYTHON  PLAYWRIGHT  SCRAPING")
    quest("quest-portfolio.svg", "04", "MARFERN PORTFOLIO",
          [("STATUS", "ONLINE"), ("HOST", "CLOUDFLARE"),
           ("URL", "MARFERN.DEV")], "ANGULAR 21  /  CLOUDFLARE")
    hud()
    system_status()
    inventory()
    skill_tree()
    terminal()
    achievements()
    current_quest()
    divider("section-divider.svg", "NEW AREA", ORANGE)
    divider("quest-divider.svg", "QUEST LOG", GOLD)
    divider("system-divider.svg", "SYSTEM / ONLINE", GREEN)


if __name__ == "__main__":
    main()
