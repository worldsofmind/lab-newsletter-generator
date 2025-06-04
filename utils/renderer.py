import os
from jinja2 import Environment, FileSystemLoader
from html2image import Html2Image

TEMPLATE_DIR = "templates"
OUTPUT_DIR = "generated_reports"

def render_html(report, period):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template("newsletter.html")
    html_content = template.render(
        officer_name=report['officer_name'],
        period=period,
        inhouse_stats=report['inhouse_stats'],
        assigned_stats=report['assigned_stats'],
        ratings_summary=report['ratings_summary'],
    )
    return html_content

def save_html_and_png(html, filename):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    html_path = os.path.join(OUTPUT_DIR, f"{filename}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    hti = Html2Image(output_path=OUTPUT_DIR)
    hti.screenshot(html_str=html, save_as=f"{filename}.png")

def render_newsletters(reports, period):
    for report in reports:
        html = render_html(report, period)
        save_html_and_png(html, report['officer_name'])
