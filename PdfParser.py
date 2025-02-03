import os
import time

import pytesseract
from pdf2image import convert_from_path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re

def generate_html_views(data: dict, doc_name):
    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Avize</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="p-4">
        <h2 class="text-center">{doc_name}</h2>
        <div class="container">
            <table class="table table-bordered table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th class="text-center">Avize bifate</th>
                        <th class="text-center">Avize nebifate</th>
                    </tr>
                </thead>
                <tbody>
    '''

    max_rows = max(len(data.get('checked', [])), len(data.get('unchecked', [])))
    checked_list = data.get("checked", [])
    unchecked_list = data.get("unchecked", [])

    for i in range(max_rows):
        checked_item = checked_list[i] if i < len(checked_list) else ""
        unchecked_item = unchecked_list[i] if i < len(unchecked_list) else ""
        html_content += f"""
        <tr>
            <td>{checked_item}</td>
            <td>{unchecked_item}</td>
        </tr>
        """

    html_content += """
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    print("Generating html view...")

    if os.path.exists(html_content):
        os.remove(html_content)
    with open(f"views/{doc_name}.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("Finished generating html view for document " + doc_name)


def get_opinions_from_pdf(pdf_file: str):
    checked_boxes = ('X', 'x', 'm', 'M', 'B')
    unchecked_boxes = ('O', 'o', 'Ol', 'D')
    start_pattern = re.compile(r"([a-zA-Z])\.(\d+)\)\s*avize\s*(.*)")
    end_pattern = re.compile(r"([a-zA-Z])\.(\d+)\)\s*studii de specialitate\s*(.*)")
    opinions_all = []
    opinions_checked = []
    opinions_unchecked = []
    content = []
    start_found = False

    with open("opinions.txt", "r", encoding="utf-8") as file:
        for line in file:
            opinions_all.append(line.strip())

    with open(pdf_file, "r", encoding="utf-8") as file:
        for index, line in enumerate(file, start=0):
            line = line
            if start_found:
                content.append(line)
            if start_pattern.search(line):
                start_found = True
            elif end_pattern.search(line):
                break

    for content_line in content:
        for opinion in opinions_all:
            index = content_line.lower().find(opinion.lower())
            if index != -1:
                if index > 1:
                    if content_line[index - 2:index].strip() in checked_boxes:
                        opinions_checked.append(opinion)
                    elif content_line[index - 2:index].strip() in unchecked_boxes:
                        opinions_unchecked.append(opinion)
                    elif content_line[index - 3:index].strip() in unchecked_boxes:
                        opinions_unchecked.append(opinion)
                elif index == 1:
                    if content_line[1] in checked_boxes:
                        opinions_checked.append(opinion)
                    if content_line[1] in unchecked_boxes:
                        opinions_unchecked.append(opinion)
                else:
                    opinions_unchecked.append(opinion)
    return {
        "checked": opinions_checked,
        "unchecked" : opinions_unchecked
    }

def extract_text_from_pdf(pdf_path_param):
    pages = convert_from_path(pdf_path_param)

    extracted_text_result = []

    for page_number, page in enumerate(pages):
        print(f"Processing page {page_number + 1}...")

        text = pytesseract.image_to_string(page, lang='ron')

        lines = text.split('\n')
        for line in lines:
            extracted_text_result.append(line)
            print(line + '\n')

    return extracted_text_result


def process_document(event):
    extracted_text = extract_text_from_pdf(event.src_path)
    output_path = event.src_path.replace("input", "output").replace(".pdf", "_extracted.txt")
    if os.path.exists(output_path):
        os.remove(output_path)
    with open(output_path, 'w') as f:
        for line in extracted_text:
            f.write(line + '\n')
    opinions_dictionary = get_opinions_from_pdf(output_path)
    generate_html_views(opinions_dictionary, event.src_path.replace("input/", "").replace(".pdf", ""))


class InputDirectoryHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return
        if event.src_path.startswith("input"):
            process_document(event)


observer = Observer()
event_handler = InputDirectoryHandler()
observer.schedule(event_handler, path="input", recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()

