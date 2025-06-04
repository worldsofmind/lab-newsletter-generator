from jinja2 import Environment, FileSystemLoader
import os
from premailer import transform
from html2image import Html2Image

env = Environment(loader=FileSystemLoader("templates"))

def render_newsletters(officer_reports, template_file="VL.html", output_dir="generated"):
    os.makedirs(output_dir, exist_ok=True)
    template = env.get_template(template_file)
    hti = Html2Image()

    for report in officer_reports:
        name_display = f"{report['name']}"
        filename_base = name_display.replace(" ", "_").replace("(", "").replace(")", "")
        html_out = template.render(**report)
        html_out = transform(html_out)

        html_path = os.path.join(output_dir, f"{filename_base}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_out)

        hti.screenshot(
            html_str=html_out,
            save_as=f"{filename_base}.png",
            size=(800, 1000),
            output_path=output_dir
        )