
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

def render_newsletters(reports, output_dir="generated"):
    template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("newsletter.html")

    os.makedirs(output_dir, exist_ok=True)

    for report in reports:
        html = template.render(officer=report)
        filename = f"{report['abbreviation']}_Newsletter.html"
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
