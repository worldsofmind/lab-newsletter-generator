import os
import imgkit

def render_newsletter_html(officer_report, template_path, output_path):
    with open(template_path, 'r', encoding='utf-8') as file:
        template = file.read()

    html_content = template.format(**officer_report)
    html_output_path = os.path.join(output_path, f"{officer_report['officer_name']}.html")

    with open(html_output_path, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)

    return html_output_path

def render_newsletter_image(html_path, output_path):
    img_output_path = html_path.replace(".html", ".png")

    options = {
        "format": "png",
        "encoding": "UTF-8",
        "quiet": "",
        "disable-smart-width": "",
        "width": "800"
    }

    imgkit.from_file(html_path, img_output_path, options=options)
    return img_output_path

def render_newsletters(reports, template_path, output_path):
    os.makedirs(output_path, exist_ok=True)
    results = []

    for report in reports:
        html_path = render_newsletter_html(report, template_path, output_path)
        image_path = render_newsletter_image(html_path, output_path)
        results.append((html_path, image_path))

    return results