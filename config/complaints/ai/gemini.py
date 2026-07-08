from google import genai
from django.conf import settings
from .prompt import PROMPT
import json
import time
import tempfile
from io import BytesIO
import requests
import mimetypes
from google.genai import types

client = genai.Client(api_key=settings.GEMINI_API_KEY)


import subprocess
import os

# FFMPEG = r"C:\Users\scien\OneDrive\Desktop\JanSankalpAI\config\ffmpeg-2026-06-29-git-de6bcf5c05-full_build\bin\ffmpeg.exe"
FFMPEG = "ffmpeg"

def convert_webm_to_mp3(input_path):
    output_path = os.path.splitext(input_path)[0] + ".mp3"

    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-i", input_path,
            "-ac", "1",          # mono
            "-ar", "16000",      # 16 kHz
            "-b:a", "128k",
            output_path,
        ],
        check=True,
    )

    # print("Created:", output_path)

    return output_path

def send_to_gemini(complaint):

    parts = [PROMPT]

    parts.append(f"Title: {complaint.title}")
    parts.append(f"Description: {complaint.description}")
    parts.append(f"State: {complaint.state}")
    parts.append(f"District: {complaint.district}")
    parts.append(f"Address: {complaint.address}")

    # if complaint.image:
    #     image_file = client.files.upload(file=complaint.image.path)
    #     parts.append(image_file)

    from PIL import Image
    from io import BytesIO

    if complaint.image:

        response = requests.get(
            complaint.image.url,
            stream=True,
            timeout=20
        )
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))

        img_format = img.format.lower()

        mime_type = f"image/{img_format}"

        image_part = types.Part.from_bytes(
            data=response.content,
            mime_type=mime_type
        )

        parts.append(image_part)

    # if complaint.voice:
    #     mp3_path = convert_webm_to_mp3(complaint.voice.path)

    #     audio_file = client.files.upload(file=mp3_path)
    #     while True:
    #         audio_file = client.files.get(name=audio_file.name)

    #         print("Current state:", audio_file.state.name)

    #         if audio_file.state.name == "ACTIVE":
    #             break

    #         if audio_file.state.name == "FAILED":
    #             raise Exception("Gemini failed to process audio file.")

    #         time.sleep(2)

    #     parts.append(audio_file)


    if complaint.voice:

        # Download audio from Cloudinary
        response = requests.get(
            complaint.voice,
            stream= True,
            timeout=20
        )

        response.raise_for_status()

        # Save temporary webm file
        with tempfile.NamedTemporaryFile(
            suffix=".webm",
            delete=False
        ) as temp_webm:

            temp_webm.write(response.content)
            webm_path = temp_webm.name


        # Convert webm to mp3
        mp3_path = convert_webm_to_mp3(webm_path)


        # Upload mp3 to Gemini
        audio_file = client.files.upload(
            file=mp3_path
        )

        # cleanup temporary files
        if os.path.exists(webm_path):
            os.remove(webm_path)

        if os.path.exists(mp3_path):
            os.remove(mp3_path)


        # Wait until Gemini processes audio
        while True:

            audio_file = client.files.get(
                name=audio_file.name
            )

            # print(
            #     "Current state:",
            #     audio_file.state.name
            # )

            if audio_file.state.name == "ACTIVE":
                break

            if audio_file.state.name == "FAILED":
                raise Exception(
                    "Gemini failed to process audio file."
                )

            time.sleep(2)


        parts.append(audio_file)

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=parts,
            )
            break
        except Exception as e:
            if attempt == 2:
                # print(e)
                raise e
            time.sleep(2**attempt)

    return json.loads(response.text)