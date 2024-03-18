import fitz  # PyMuPDF
import base64
from PIL import Image
import io
import json


def extract_pdf_pages(source_pdf_path, output_pdf_path, start_page, end_page):
    """
    Extracts pages from a PDF within a specified range and saves them to a new PDF.

    :param source_pdf_path: Path to the source PDF file.
    :param output_pdf_path: Path to save the extracted pages PDF.
    :param start_page: The starting page number (0-indexed).
    :param end_page: The ending page number (0-indexed, inclusive).
    """
    source_pdf = fitz.open(source_pdf_path)
    output_pdf = fitz.open()

    for page_num in range(start_page, end_page + 1):
        page = source_pdf.load_page(page_num)
        output_pdf.insert_pdf(source_pdf, from_page=page_num, to_page=page_num)

    output_pdf.save(output_pdf_path)
    output_pdf.close()
    source_pdf.close()


def convert_pdf_to_images(pdf_path, output_folder, dpi=200):
    """
    Converts each page of a PDF file into images.

    :param pdf_path: Path to the PDF file.
    :param output_folder: Folder to save the output images.
    :param dpi: Resolution of the output images in dots per inch.
    """
    pdf_file = fitz.open(pdf_path)
    for page_num in range(len(pdf_file)):
        page = pdf_file.load_page(page_num)
        pix = page.get_pixmap(dpi=dpi)
        image_path = f"{output_folder}/page_{page_num + 1}.png"
        pix.save(image_path)

    pdf_file.close()


def image_to_base64(image_path, format='PNG'):
    """
    Converts an image to a base64-encoded string.

    :param image_path: Path to the image file.
    :param format: Format to encode the image as (e.g., 'JPEG', 'PNG'). Defaults to 'PNG'.
    :return: A base64-encoded string of the image.
    """
    # Open the image file
    with Image.open(image_path) as image:
        # Convert the image to bytes in the specified format
        buffered = io.BytesIO()
        image.save(buffered, format=format)
        # Encode the bytes to base64
        img_str = base64.b64encode(buffered.getvalue())
        return img_str.decode('utf-8')
    
# function that takes a json string and pretty prints it to file
def save_json_to_file(json_str, output_path):
    """
    Pretty prints a JSON string to a file, with added resilience against JSON decoding errors due to unescaped control characters.

    :param json_str: The JSON string to pretty print.
    :param output_path: The file path to save the pretty printed JSON.
    """
    try:
        # Attempt to decode the JSON to an object, which will handle escaping of control characters properly.
        parsed_json = json.loads(json_str)
        # Pretty print (re-encode) the JSON object to a string and save to file.
        with open(output_path, "w") as file:
            json.dump(parsed_json, file, indent=4)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON string: {e}")