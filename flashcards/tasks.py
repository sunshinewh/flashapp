#!/usr/bin/python
# -*- coding: utf-8 -*-
# tasks.py in your Django app
from celery import shared_task
import requests
from PIL import Image
import io
import random
from django.shortcuts import render, redirect
from .utils import mongo_handler
from django.contrib import messages
import pymongo
from collections import defaultdict
import csv
import os
import io
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST
#from .utils import set_primary_image  # Importing from utils.py
import random
import chardet
import textwrap
import openai  # pip install openai
import urllib.request
import datetime
import warnings
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import getopt
import sys
from django.conf import settings
from pathlib import Path
import pydub
from pydub import playback
from openai import OpenAI
from pydub import AudioSegment
from datetime import datetime, timedelta
from django_q.tasks import async_task
import boto3
import requests
from botocore.exceptions import NoCredentialsError, ClientError
import base64
import boto3
import logging

def create_presigned_url(bucket_name, object_name, expiration=3600):
    try:
        response = s3client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging.error(e)
        return None

    return response



AWS_STORAGE_BUCKET_NAME="flashappbucket"

def print_to_stderr(*a):
    print(*a, file=sys.stderr)

all_cards,ascent,ipa_font, line_spacing, positive_prompt, negative_prompt, sentenceeng, card_files, ext, front_texts, back_texts, front_fonts, back_fonts, audio_filename, s3client, current_time,full_ipa,line1 = ([] for i in range(18))
hdim = 896
vdim = 1152
FONTSIZE = 70
SHADOWWIDTH = 4

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



s3client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION_NAME
)
AWS_STORAGE_BUCKET_NAME="flashappbucket"

def print_to_stderr(*a):
    print(*a, file=sys.stderr)
    
@shared_task
def generate_image(filename_base, style_preset, numimages, engine_id, sampler, positive_prompt, negative_prompt, vdim, hdim):
    print(f"Sampler: {sampler}")
    filenames = []  # Initialize image_paths as an empty list

    if STABILITY_API_KEY is None:
        raise Exception("Missing Stability API key.")

    # Generate images
    for i in range(numimages):
        filename = f"{filename_base}_{i}.jpg"

        # Generate a random 8-digit number
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
                    {
                        "text": positive_prompt,
                        "weight": 1
                    },
                    {
                        "text": negative_prompt,
                        "weight": -1
                    }
                ],
                "cfg_scale": 7,
                "height": 896,
                "width": 1152,
                "samples": 1,
                "steps": 30,
                "seed": random_number,
                "style_preset": style_preset,
                #"sampler": sampler,
            },
        )

        if response.status_code != 200:
            raise Exception("Non-200 response: " + str(response.text))

        data = response.json()
        AWS_STORAGE_BUCKET_NAME = "flashappbucket"
        # Check if "artifacts" is present in the response
        if "artifacts" in data:
            artifacts = data["artifacts"]

            # Check if there are artifacts to display
            if artifacts:
                for i, artifact in enumerate(artifacts):
                    base64_image = artifact.get("base64")

                    # Check if "base64" is present in the artifact
                    if base64_image:
                        # Decode base64 image data
                        image_data = base64.b64decode(base64_image)
                        # Open the image using PIL
                        image = Image.open(io.BytesIO(image_data))
                        # Display the image using Pillow

                        key = f"cards/{filename}"
                        buffer = io.BytesIO()
                        image.save(buffer, format="JPEG")
                        buffer.seek(0)
                        s3client.upload_fileobj(buffer, AWS_STORAGE_BUCKET_NAME, key)

                        key = f"raw/{filename}"
                        buffer = io.BytesIO()
                        image.save(buffer, format="JPEG")
                        buffer.seek(0)
                        s3client.upload_fileobj(buffer, AWS_STORAGE_BUCKET_NAME, key)
                        filenames.append(filename)

    return filenames
    print(f"######################### GI Filenames: {filenames}")
