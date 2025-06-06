from jinja2 import Environment, FileSystemLoader
import os
import pdfkit
import imgkit
from weasyprint import HTML
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
    # Round to nearest half‐star
    half_stars = int(round(val * 2))
    full_stars = half_stars // 2
    half_star   = half_stars % 2
    stars = "★" * full_stars + ("½" if half_star else "") + "☆" * (5 - full_stars - half_star)
    return stars


def html_to_pdf(html_path: str, pdf_path: str):
    """
    Convert a local HTML file (html_path) into a PDF (pdf_path).
    First try pdfkit (wkhtmltopdf). If that fails, fall back to WeasyPrint.
    """
    try:
        # If wkhtmltopdf is on your PATH, this will work.
        pdfkit.from_file(html_path, pdf_path)
    except Exception:
        # Fallback to WeasyPrint if pdfkit/wkhtmltopdf fails
        HTML(html_path).write_pdf(pdf_path)


def html_to_png(html_path: str, png_path: str):
    """
    Convert local HTML (html_path) to a full‐page PNG (png_path) using wkhtmltoimage via imgkit.
    Adjust width or zoom options as needed.
    """
    options = {
        "format": "png",
        "width": "1024",   # Adjust to your newsletter’s intended width
        "quality": "90",
    }
    imgkit.from_file(html_path, png_path, options=options)


def render_newsletters(all_reports, output_dir="output"):
    """
    Render each officer’s stats into three files:
      1) <ABBR>.html
      2) <ABBR>.pdf
      3) <ABBR>.png

    Uses Jinja to render HTML, then converts to PDF and PNG.
    """
    env = Environment(
        loader=FileSystemLoader(searchpath=os.path.join(os.getcwd(), "templates")),
        autoescape=True
    )
    # Make stars_from_score available inside the template
    env.globals['stars_from_score'] = stars_from_score

    template = env.get_template("newsletter.html")

    os.makedirs(output_dir, exist_ok=True)

    for report in all_reports:
        abbr = report["abbreviation"]
        html_path = Path(output_dir) / f"{abbr}.html"
        pdf_path  = Path(output_dir) / f"{abbr}.pdf"
        png_path  = Path(output_dir) / f"{abbr}.png"

        # 1) Render HTML
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(template.render(officer=report))

        # 2) Convert HTML → PDF
        try:
            html_to_pdf(str(html_path), str(pdf_path))
        except Exception as e:
            # If pdf conversion fails, delete any partial PDF
            if pdf_path.exists():
                pdf_path.unlink()
            print(f"Warning: PDF conversion failed for {abbr}: {e}")

        # 3) Convert HTML → PNG
        try:
            html_to_png(str(html_path), str(png_path))
        except Exception as e:
            # If PNG conversion fails, delete any partial PNG
            if png_path.exists():
                png_path.unlink()
            print(f"Warning: PNG conversion failed for {abbr}: {e}")
