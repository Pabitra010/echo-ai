

import asyncio  # Importing asyncio for handling asynchronous tasks
from random import randint  # Importing randint to generate random numbers
from PIL import Image  # Importing PIL for image handling
import requests  # Importing requests to make API calls
from dotenv import get_key  # Importing get_key to retrieve API keys from the .env file
import os  # Importing os for file operations
from time import sleep  # Importing sleep to introduce delays in execution

# Function to open generated images
def open_images(prompt):
    folder_path = r"Data"  # Folder where images are stored
    prompt = prompt.replace(" ", "_")  # Replacing spaces with underscores in the prompt

    # Creating a list of expected image file names
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    # Iterating through the expected image files
    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)  # Constructing the file path

        try:
            img = Image.open(image_path)  # Attempting to open the image
            print(f"Opening image: {image_path}")
            img.show()  # Displaying the image
            sleep(1)  # Adding a small delay before opening the next image
        
        except IOError:
            print(f"Unable to open {image_path}")  # Handling errors if the file cannot be opened

# API details for Hugging Face's image generation model
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Fetching the API key from the .env file
api_key = get_key(".env", "HuggingFaceAPIKey")

# Asynchronous function to make an API request for image generation
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content  # Returning the generated image data

# Function to generate multiple images asynchronously
async def generate_images(prompt: str):
    tasks = []  # List to store async tasks

    for _ in range(4):  # Generating 4 images
        payload = {
            "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))  # Creating an async task for each API call
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)  # Running all tasks concurrently and collecting results

    # Saving the generated images
    for i, image_bytes in enumerate(image_bytes_list):
        with open(fr"Data\{prompt.replace(' ', '_')}{i+1}.jpg", "wb") as f:
            f.write(image_bytes)  # Writing image data to a file

# Function to generate images and open them after generation
def GenerateImage(prompt: str):
    asyncio.run(generate_images(prompt))  # Running the async image generation function
    open_images(prompt)  # Opening the generated images

# Main loop to check for new image generation requests
while True:
    try:
        # Reading the image generation status file
        with open(r"Frontend/Files/ImageGeneration.data", "r") as f:
            Data: str = f.read()

        Prompt, Status = Data.split(",")  # Extracting the prompt and status

        if Status == "True":  # Checking if an image needs to be generated
            print("Generating Image...")
            ImageStatus = GenerateImage(prompt=Prompt)  # Generating the image

            # Updating the status file to indicate that image generation is complete
            with open(r"Frontend/Files/ImageGeneration.data", "w") as f:
                f.write("False,False")
                break  # Exiting the loop after processing

        else:
            sleep(1)  # If no image needs to be generated, wait before checking again
    
    except:
        pass  # Handling any unexpected errors
