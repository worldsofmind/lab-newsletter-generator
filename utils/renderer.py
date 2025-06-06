from jinja2 import Environment, FileSystemLoader
import os


def stars_from_score(score):
    """
    Convert a numeric rating (e.g. 3.5, 4.0) into a 5‐character string with ★/☆.
    Round to nearest 0.5. Examples:
      4.0 → '★★★★☆'
      3.5 → '★★★☆☆'
      2.0 → '★★☆☆☆'
    If score is not a number (e.g. 'N/A'), return an empty string.
    """
    try:
        val = float(score)
    except Exception:
        return ""
    # Round to nearest half‐star
    half_stars = int(round(val * 2))
    full_stars = half_stars // 2
    half_star   = half_stars % 2
    stars = "★" * full_stars + ("½" if half_star else "") + "☆" * (5 - full_stars - half_star)
    return stars


def render_newsletters(all_reports, output_dir="generated"):
    """
    Render each officer’s stats into an HTML file that matches VL.html’s style
    (including star‐based ratings). all_reports is a list of dicts returned by
    compute_officer_stats. output_dir is a Path or string; files will be written
    to output_dir/<abbreviation>.html
    """
    env = Environment(
        loader=FileSystemLoader(searchpath=os.path.join(os.getcwd(), "templates")),
        autoescape=True
    )

    # ── REGISTER stars_from_score AS A GLOBAL IN THE TEMPLATE ────────────────────
    env.globals['stars_from_score'] = stars_from_score

    template = env.get_template("newsletter.html")

    os.makedirs(output_dir, exist_ok=True)
    for report in all_reports:
        output_path = os.path.join(output_dir, f"{report['abbreviation']}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(template.render(officer=report))
