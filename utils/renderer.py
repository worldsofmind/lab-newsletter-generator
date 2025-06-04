
import os
from jinja2 import Environment, FileSystemLoader
from html2image import Html2Image

def render_newsletters(officer_reports, template_name="newsletter.html", output_dir="generated"):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(template_name)

    os.makedirs(output_dir, exist_ok=True)
    hti = Html2Image(output_path=output_dir)

    for report in officer_reports:
        html_content = template.render(report)
        html_file_path = os.path.join(output_dir, f"{report['name']}.html")
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Generate PNG from HTML
        hti.screenshot(html_str=html_content, save_as=f"{report['name']}.png")

    return output_dir
