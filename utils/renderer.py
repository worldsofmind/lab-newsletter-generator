
import os
import asyncio
from jinja2 import Environment, FileSystemLoader
from pyppeteer import launch

TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(TEMPLATE_DIR, "..", "generated")

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template("newsletter.html")

async def render_newsletter_to_png(input_path, output_path):
    browser = await launch()
    page = await browser.newPage()
    await page.goto("file://" + os.path.abspath(input_path))
    await page.screenshot({'path': output_path, 'fullPage': True})
    await browser.close()

def render_newsletters(reports):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for report in reports:
        filename = f"{report['abbreviation']}_Newsletter"
        html_path = os.path.join(OUTPUT_DIR, f"{filename}.html")
        png_path = os.path.join(OUTPUT_DIR, f"{filename}.png")

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(template.render(**report))

        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(render_newsletter_to_png(html_path, png_path))
        except Exception as e:
            print(f"❌ Error rendering PNG for {filename}: {e}")
