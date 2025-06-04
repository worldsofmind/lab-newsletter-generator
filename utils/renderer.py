# lab_newsletter_generator/utils/renderer.py

import os
from jinja2 import Environment, FileSystemLoader
import imgkit

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
    png_path = os.path.join(OUTPUT_DIR, f"{filename}.png")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    imgkit.from_file(html_path, png_path)

def render_newsletters(reports, period):
    for report in reports:
        html = render_html(report, period)
        save_html_and_png(html, report['officer_name'])