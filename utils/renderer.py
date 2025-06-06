from jinja2 import Environment, FileSystemLoader
import os
import pdfkit
import imgkit
from pathlib import Path


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
    half_stars = int(round(val * 2))
    full_stars = half_stars // 2
    half_star = half_stars % 2
    stars = "★" * full_stars + ("½" if half_star else "") + "☆" * (5 - full_stars - half_star)
    return stars


def html_to_pdf(html_path: str, pdf_path: str):
    """
    Convert a local HTML file (html_path) into a PDF (pdf_path) using pdfkit/wkhtmltopdf.
    """
    try:
        # If wkhtmltopdf is installed and on PATH, this will work:
        pdfkit.from_file(html_path, pdf_path)
    except Exception as e:
        # If conversion fails, delete any partial PDF and print a warning
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        print(f"Warning: PDF conversion failed for {html_path}: {e}")


def html_to_png(html_path: str, png_path: str):
    """
    Convert local HTML (html_path) to a full‐page PNG (png_path) using wkhtmltoimage via imgkit.
    Adjust width/options as needed.
    """
    options = {
        "format": "png",
        "width": "1024",
        "quality": "90",
    }
    try:
        imgkit.from_file(html_path, png_path, options=options)
    except Exception as e:
        if os.path.exists(png_path):
            os.remove(png_path)
        print(f"Warning: PNG conversion failed for {html_path}: {e}")


def render_newsletters(all_reports, output_dir="output"):
    """
    Render each officer’s stats into:
      1) <ABBR>.html
      2) <ABBR>.pdf
      3) <ABBR>.png

    Uses Jinja to render HTML, then converts to PDF and PNG via pdfkit & imgkit.
    """
    env = Environment(
        loader=FileSystemLoader(searchpath=os.path.join(os.getcwd(), "templates")),
        autoescape=True
    )
    env.globals['stars_from_score'] = stars_from_score
    template = env.get_template("newsletter.html")

    os.makedirs(output_dir, exist_ok=True)

    for report in all_reports:
        abbr = report["abbreviation"]
        html_path = Path(output_dir) / f"{abbr}.html"
        pdf_path = Path(output_dir) / f"{abbr}.pdf"
        png_path = Path(output_dir) / f"{abbr}.png"

        # 1) Render HTML
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(template.render(officer=report))

        # 2) Convert HTML → PDF
        html_to_pdf(str(html_path), str(pdf_path))

        # 3) Convert HTML → PNG
        html_to_png(str(html_path), str(png_path))
