#!/usr/bin/python
# -*- coding: utf-8 -*-
# tasks.py in your Django app
from .utils import mongo_handler
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST, csrf_exempt
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import sys
import base64
import logging

from celery import shared_task
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import random
import boto3
from django.conf import settings
from bson import ObjectId

AWS_STORAGE_BUCKET_NAME="flashappbucket"

def print_to_stderr(*a):
    print(*a, file=sys.stderr)

all_cards,ascent,ipa_font, line_spacing, positive_prompt, negative_prompt, sentenceeng, card_files, ext, front_texts, back_texts, front_fonts, back_fonts, audio_filename, s3client, current_time,full_ipa,line1 = ([] for i in range(18))
hdim = 1152
vdim = 896
line1 = -75
line2 =  75
line3 = 225
FONTSIZE = 70
SHADOWWIDTH = 4
FONTNAME = regular_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Times New Roman Bold.ttf')
regular_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Times New Roman Bold.ttf')
font = ImageFont.truetype(FONTNAME, FONTSIZE)

# Create an S3 client
STABILITY_API_KEY='sk-gyLG03XUnY4HWeuocSwbCXKTKRzPpVR8W2Jq1dRUXFF28JGi'
MONGO_USER='user'
MONGO_PASSWORD='KJLhK8rwgYKYMpcGr6v4'
MONGO_HOST='cluster0.sirwuvv.mongodb.net'
MONGO_DB='flashcard_db'
MONGO_COLLECTION='cards'
AWS_ACCESS_KEY_ID='AKIAVJ2P6UW7XPTFZ2XT'
AWS_SECRET_ACCESS_KEY='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'
AWS_STORAGE_BUCKET_NAME="flashappbucket"
AWS_S3_REGION_NAME='us-west-2'

# Initialize S3 client for AWS operations
s3client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

def upload_to_s3(file_buffer, bucket_name, object_name):
    """Uploads a file to S3."""
    try:
        s3client.upload_fileobj(file_buffer, bucket_name, object_name)
    except Exception as e:
        logging.error(f"Error uploading to S3: {e}")

def write_image(size, message, font, fontColor, hoffset, image):
    W, H = size
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), message, font=font)
    tw, th = get_text_dimensions(message, font)
    draw.text((((W-tw)/2), ((H-th)/2)+hoffset), message, font=font, fill=fontColor, stroke_width=SHADOWWIDTH, stroke_fill='white')
    return image

@shared_task
def generate_image(filename_base, style_preset, numimages, engine_id, sampler, positive_prompt, negative_prompt, vdim, hdim, sentenceforeign, meaning, full_ipa):
    filenames = []
    update_dict = {}
    mongo_collection = mongo_handler()  # Assuming mongo_handler is defined to get the collection

    for i in range(numimages):
        filename = f"{filename_base}_{i}.jpg"
        random_number = random.randint(10000, 99999)
        response = requests.post(
            f"https://api.stability.ai/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {STABILITY_API_KEY}"
            },
            json={
                "text_prompts": [
                    {"text": positive_prompt, "weight": 1},
                    {"text": negative_prompt, "weight": -1}
                ],
                "cfg_scale": 7,
                "height": vdim,
                "width": hdim,
                "samples": 1,
                "steps": 30,
                "seed": random_number,
                "style_preset": style_preset
            }
        )

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()
        if "artifacts" in data:
            artifacts = data["artifacts"]
            if artifacts:
                for artifact in artifacts:
                    base64_image = artifact.get("base64")
                    if base64_image:
                        image_data = base64.b64decode(base64_image)
                        image = Image.open(io.BytesIO(image_data))

                        # Save a raw copy to the 'raw' folder
                        buffer_raw = io.BytesIO()
                        image.save(buffer_raw, format="JPEG")
                        buffer_raw.seek(0)
                        s3client.upload_fileobj(buffer_raw, AWS_STORAGE_BUCKET_NAME, f"raw/{filename}")

                        # Perform Pillow operations
                        write_image((hdim, vdim), "[" + full_ipa + "] " + meaning, font, 'black', line2, image)
                        write_image((hdim, vdim), sentenceforeign, font, 'black', line3, image)

                        # Save the processed image to a buffer
                        buffer_cards = io.BytesIO()
                        image.save(buffer_cards, format='JPEG')
                        buffer_cards.seek(0)

                        # Upload the processed image to the 'cards' folder
                        upload_to_s3(buffer_cards, AWS_STORAGE_BUCKET_NAME, f"cards/{filename}")

                        # Update dictionary to reflect filename
                        update_dict[f'image_path{i}'] = filename

                        # Update MongoDB document
                        mongo_collection.update_one({'_id': ObjectId(card_id)}, {'$set': update_dict})

    return "Task Completed"

