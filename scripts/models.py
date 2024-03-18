from scripts.utils import *
from dotenv import load_dotenv
import os
from ratelimit import limits, sleep_and_retry
from groq import Groq
import anthropic
import pickle
load_dotenv()


@sleep_and_retry
@limits(calls=30, period=60)
def get_groq_chat_response(system_message, message):
    client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
        # Set an optional system message. This sets the behavior of the
        # assistant and can be used to provide specific instructions for
        # how it should behave throughout the conversation.
        {
            "role": "system",
            "content": system_message
        },
        # Set a user message for the assistant to respond to.
        {
            "role": "user",
            "content": message,
        }
    ],
        model="mixtral-8x7b-32768",
    )

    return chat_completion


@sleep_and_retry
@limits(calls=5, period=60)
def get_anthropic_vision_response(image_path):
    # Convert image to base64
    image1_data = image_to_base64(image_path)
    # Assume the media type for now
    image1_media_type = "image/png"
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1024,
        system="You are a transcription service that responds only with the text shown in the given image.\nYou will make no other comments.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image1_media_type,
                            "data": image1_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Transcribe this image as precisely as possible."
                    }
                    ],
            }
            ],
    )
    return response


# function to save response to cache using pickle
def save_response_to_cache(response, cache_path):
    with open(cache_path, "wb") as file:
        pickle.dump(response, file)
       
 
# function to load response from cache using pickle
def load_response_from_cache(cache_path):
    with open(cache_path, "rb") as file:
        response = pickle.load(file)
    return response

# Function to load response from cache if it exists, otherwise get response from anthropic and save to cache
def get_vision_response(image_path, cache_path):
    if os.path.exists(cache_path):
        response = load_response_from_cache(cache_path)
    else:
        response = get_anthropic_vision_response(image_path)
        save_response_to_cache(response, cache_path)
    return response


def get_json_formatted_response(vision_response, image_path):
    json_system_message = '''
    You are a helpful assistant that specializes in converting documents to JSON.
    You will be given unformatted glossary text and you will convert it to JSON, where the key is the term and the value is the definition.
    You will only respond with the required JSON and make no other comments.
    '''
    # If json file already exists, load it as string and return
    if os.path.exists(image_path):
        with open(image_path, "r") as file:
            json_str = file.read()
            return json_str
    # Otherwise, get response from groq
    else:
        json_response = get_groq_chat_response(json_system_message, vision_response.content[0].text)
        save_json_to_file(json_response.choices[0].message.content, image_path)
        return json_response