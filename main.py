from scripts.utils import *
from scripts.models import *
import glob

input_directory = "input/example1"
input_filename = "math910curr.pdf"

input_filename_reduced = input_filename.replace(".pdf", "_glossary.pdf")
extract_pdf_pages(f"{input_directory}/{input_filename}", f"{input_directory}/{input_filename_reduced}", 60, 62)
convert_pdf_to_images(f"{input_directory}/{input_filename_reduced}", f"{input_directory}/data")

# For each image, get the vision response
for image_path in glob.glob(f"{input_directory}/data/*.png"):
    print(f"Processing image: {image_path}")
    vision_response = get_vision_response(image_path, f"{image_path}.pkl")
    # print(vision_response.content)
    # Given the response, pass it to the LLM to convert to json
    json_response = get_json_formatted_response(vision_response, f"{image_path}.json")
    
    
# Combine the JSON files into a single JSON file
combined_json = {}
for json_path in glob.glob(f"{input_directory}/data/*.png.json"):
    with open(json_path, "r") as file:
        combined_json.update(json.load(file))
save_json_to_file(json.dumps(combined_json), f"{input_directory}/{input_filename_reduced.replace('.pdf', '_glossary.json')}")