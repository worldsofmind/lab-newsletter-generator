import asyncio
from pyppeteer import launch
from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../templates')
GENERATED_DIR = os.path.join(os.path.dirname(__file__), '../generated')
os.makedirs(GENERATED_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

async def render_newsletter_to_png(html_file, output_path):
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.goto(f'file://{html_file}', {'waitUntil': 'networkidle0'})
    await page.screenshot({'path': output_path, 'fullPage': True})
    await browser.close()

def render_newsletters(officer_reports):
    template = env.get_template("newsletter.html")
    for report in officer_reports:
        html_content = template.render(**report)
        safe_name = report['name'].replace(" ", "_").replace("(", "").replace(")", "")
        html_path = os.path.join(GENERATED_DIR, f"{safe_name}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        png_path = os.path.join(GENERATED_DIR, f"{safe_name}.png")
        asyncio.get_event_loop().run_until_complete(render_newsletter_to_png(html_path, png_path))
