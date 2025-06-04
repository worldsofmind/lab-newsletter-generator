
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
import pdfkit
from premailer import transform

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "generated")

env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

def render_newsletters(reports):
    template = env.get_template("newsletter.html")

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for report in reports:
        html_content = template.render(report)
        styled_html = transform(html_content)

        officer_safe_name = report['name'].replace(" ", "_").replace("/", "_")
        html_path = os.path.join(OUTPUT_DIR, f"{officer_safe_name}.html")
        pdf_path = os.path.join(OUTPUT_DIR, f"{officer_safe_name}.pdf")

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(styled_html)

        # Optional: Generate PDF from HTML (requires wkhtmltopdf installed)
        try:
            pdfkit.from_file(html_path, pdf_path)
        except Exception as e:
            print(f"Failed to generate PDF for {report['name']}: {e}")

    return f"Newsletters saved to: {OUTPUT_DIR}"
