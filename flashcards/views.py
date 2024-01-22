#!/usr/bin/python
# -*- coding: utf-8 -*-
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
from django.http import JsonResponse
from celery.result import AsyncResult

def get_task_status(request, task_id):
    task_result = AsyncResult(task_id)
    if task_result.ready():
        return JsonResponse({'status': 'complete', 'filenames': task_result.get()})
    else:
        return JsonResponse({'status': 'pending'})
    
AWS_STORAGE_BUCKET_NAME="flashappbucket"

def print_to_stderr(*a):
    print(*a, file=sys.stderr)

all_cards,ascent,ipa_font, line_spacing, positive_prompt, negative_prompt, sentenceeng, card_files, ext, front_texts, back_texts, front_fonts, back_fonts, audio_filename, s3client, current_time,full_ipa,line1 = ([] for i in range(18))
hdim = 896
vdim = 1152
FONTSIZE = 70
SHADOWWIDTH = 4
def get_existing_images(s3_client, bucket_name, prefix):
    try:
        existing_images = []
        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)
        for page in pages:
            for obj in page['Contents']:
                existing_images.append(obj['Key'])
        return existing_images
    except (NoCredentialsError, ClientError) as e:
        print(f"Error accessing S3: {e}")
        return None

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
    aws_access_key_id='AKIAVJ2P6UW74SZHNEMD',
    aws_secret_access_key='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',
    region_name='us-west-2'
)

import boto3
from botocore.exceptions import ClientError
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

def play_audio(file):
    sound = pydub.AudioSegment.from_file(file, format="mp3")
    playback.play(sound)

shadow_color='white'

# Second File Path - in the 'cards' subdirectory under static

def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()
    width = font.getmask(text_string).getbbox()[2]
    height = font.getmask(text_string).getbbox()[3] + descent 
    return (width, height)

def write_image(size, message, font, fontColor, hoffset, image):
    W, H = size
    draw = ImageDraw.Draw(image)
    _, _, w, h = draw.textbbox((0, 0), message, font=font)
    tw, th = get_text_dimensions(message, font)
    print("W:"+str(W)+" H:"+str(H)+" w: "+str(w)+" h: "+str(h)+" tw: "+str(tw)+" th: "+str(th))
    draw.text((((W-tw)/2), ((H-th)/2)+hoffset), message, font=font, fill=fontColor, stroke_width=SHADOWWIDTH, stroke_fill='white')
    #draw.text((((W-w)/2), ((H-h)/2)+125), TRADITIONAL_CHAR, font=font, fill=fontColor, stroke_width=10, stroke_fill='white')
    return image

s3client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION_NAME
)




def home(request):
	return render(request, 'general/home.html')

from django.shortcuts import render, redirect

from bson import ObjectId

from bson import ObjectId
from django.shortcuts import redirect
# Make sure you have the appropriate imports for other required modules and functions

FONTSIZE = 100
SHADOWWIDTH = 5

def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()
    width = font.getmask(text_string).getbbox()[2]
    height = font.getmask(text_string).getbbox()[3] + descent 
    return (width, height)

from django.http import JsonResponse
from .tasks import generate_image
from django.shortcuts import redirect

def generate_ai_images(request):
    if request.method == 'POST':
        # Extract the necessary data from the request
        filename_base = f"{deck}_{word}".replace(' ', '_')
        style_preset = request.POST.get('style_preset')
        numimages = int(request.POST.get('numimages', 1))  # Default to 1 if not provided
        engine_id = request.POST.get('engine_id')
        sampler = request.POST.get('sampler')
        positive_prompt = request.POST.get('positive_prompt')
        negative_prompt = request.POST.get('negative_prompt')
        vdim = int(request.POST.get('vdim', 896))  # Provide default value if not set
        hdim = int(request.POST.get('hdim', 1152))  # Provide default value if not set
        sentenceforeign = request.POST.get('sentenceforeign')
        meaning = request.POST.get('meaning')
        full_ipa = request.POST.get('full_ipa')
        card_id = request.POST.get('card_id')
        clip_guidance = request.POST.get('clip_guidance')
        deck = request.POST.get('deck_name')
        word = request.POST.get('word')
        sentenceeng = request.POST.get('sentenceeng')
        text_string = request.POST.get('text_string')
        print("POST Data:", request.POST)
        # Call the Celery task
        task_result = generate_image.delay(filename_base, style_preset, numimages, engine_id, sampler, positive_prompt, negative_prompt, vdim, hdim, sentenceforeign, meaning, full_ipa, card_id, clip_guidance, deck, word)

        # Return a response with the task ID
        return JsonResponse({'task_id': task_result.id})

    else:
        # Redirect if not a POST request or handle differently
        return redirect('my_cards')  # Replace 'some_view_name' with an appropriate redirect

# View for generating bulk AI images
@require_POST
def generate_bulk_ai_images(request):
    FONTSIZE = 100
    SHADOWWIDTH = 5
    line1 = -75
    line2 = 75
    line3 = 225
    mongo_collection = mongo_handler()
    FONTNAME = regular_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Times New Roman Bold.ttf')
    regular_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Times New Roman Bold.ttf')
    font = ImageFont.truetype(FONTNAME, FONTSIZE)
    ipa_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Times New Roman Bold.ttf')
    regular_font = ImageFont.truetype(regular_font_path, FONTSIZE)
    ipa_font = ImageFont.truetype(ipa_font_path, FONTSIZE)
    font = ImageFont.truetype(regular_font_path, FONTSIZE)
    line_spacing = 300  # Additional space between lines, adjust as needed

    if request.method == 'POST':
        s3_client = boto3.client('s3')
        existing_images = get_existing_images(s3_client, AWS_STORAGE_BUCKET_NAME, 'cards/')
        if existing_images is None:
            return redirect('error_page')

        all_cards = mongo_collection.find({}) 
        for card in all_cards:
            text_string = request.POST.get('text_string')
            card_id = request.POST.get('card_id')
            numimages = int(request.POST.get('numimages', 1))  # Default to 1 if not provided
            style_preset = request.POST.get('style_preset')
            engine_id = request.POST.get('engine_id')
            sampler = request.POST.get('sampler')
            clip_guidance = request.POST.get('clip_guidance')
            positive_prompt = request.POST.get('positive_prompt')
            negative_prompt = request.POST.get('negative_prompt')
            deck = request.POST.get('deck_name')
            word = request.POST.get('word')
            meaning = request.POST.get('meaning')
            full_ipa = request.POST.get('full_ipa')
            sentenceforeign = request.POST.get('sentenceforeign')
            sentenceeng = request.POST.get('sentenceeng')
            text_string = word
            filebase = f"{deck}_{word}".replace(' ', '_')
            #hdim = request.POST.get('hdim')
            #vdim = request.POST.get('vdim')
            filepaths_to_check = [f"cards/{filebase}_{i}.jpg" for i in range(numimages)]
            if not all(filepath in existing_images for filepath in filepaths_to_check):
                try:
                    # Call generate_image with filebase and text_string
                    # [Assuming generate_image and other necessary functions are defined elsewhere]
                    filenames = generate_image(filebase, style_preset, numimages, engine_id, sampler, positive_prompt, negative_prompt, vdim, hdim)

                    # Initialize update_dict
                    update_dict = {}

                    # Update dictionary with new image paths
                    for i, path in enumerate(filenames):
                        print(f"filenames: {filenames}")
                        print(f"path: {path}")
                        full_path = f"cards/{path}"

                        # Retrieve the image from S3
                        response = s3_client.get_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=full_path)
                        file_content = response['Body'].read()

                        # Open the image file directly from bytes
                        with Image.open(BytesIO(file_content)) as card_write:
                            # Perform your image modifications
                            # [Assuming write_image function is defined elsewhere]
                            write_image((hdim, vdim), "[" + full_ipa + "] " + meaning , font, 'black', line2, card_write)
                            write_image((hdim, vdim), sentenceforeign, font, 'black', line3, card_write)

                            # Save the modified image to a buffer
                            buffer = BytesIO()
                            card_write.save(buffer, 'JPEG')
                            buffer.seek(0)

                            # Upload the modified image back to S3
                            s3_client.upload_fileobj(buffer, AWS_STORAGE_BUCKET_NAME, full_path)

                        # Update your dictionary to reflect the full path
                        update_dict[f'image_path{i}'] = full_path
                    # Update the MongoDB document
                    mongo_collection.update_one({'_id': ObjectId(card_id)}, {'$set': update_dict})

                except Exception as e:
                    print(f"Error generating images: {e}")

        return redirect('my_cards')  # Redirect back to the cards page

    return redirect('home')  # Redirect to home if not a POST request

require_POST
def set_primary_image_view(request):
    try:
        data = json.loads(request.body)
        card_id = data.get('cardId')
        new_image_url = data.get('imagePath')

        if new_image_url:
            new_image_path = new_image_url.split('/')[-1].split('?')[0]
        else:
            new_image_path = None

        if card_id and new_image_path:
            success = set_primary_image(card_id, new_image_path)
            if success:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Database update failed'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})

    return JsonResponse({'success': False, 'error': 'Invalid data received'})

def set_primary_image(card_id, new_image_path):
    try:
        collection = mongo_handler()
        query = {'_id': ObjectId(card_id)}
        updated_card = {"$set": {'primary_image': new_image_path}}
        collection.update_one(query, updated_card)
        return True
    except Exception as e:
        print(f"Error updating the database: {e}")
        return False

# Assume mongo_handler() is a function that returns a MongoDB collection
#from your_app_name.mongo_utils import mongo_handler

from django.http import JsonResponse
import json
from bson import ObjectId
# Assuming mongo_handler is defined elsewhere

@csrf_exempt
def update_primary_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_id = data['cardId']
        image_path = data['imagePath']
        print(f"Updating primary image: {image_path}")  # Debug print
        mongo_collection = mongo_handler()
        update_result = mongo_collection.update_one(
            {'_id': ObjectId(card_id)},
            {'$set': {'primary_image': image_path}},
        )
        print(image_path)
        if update_result.modified_count > 0:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'not_modified'}, status=400)

    return JsonResponse({'status': 'fail'}, status=400)

from django.http import JsonResponse

def my_cards(request):
    mongo_collection = mongo_handler()

    # Handle POST request for updates
    if request.method == 'POST':
        data = request.POST
        card_id = data.get('card_id')  # Retrieve card_id from POST data
        deck_name = data.get('deck_name')
        updated_data = {
            'word': data.get('word'),
            'approximation': data.get('approximation'),
            'sentenceeng': data.get('sentenceeng'),
            'meaning': data.get('meaning'),
            'sentenceforeign': data.get('sentenceforeign'),
        }
        if card_id:
            mongo_collection.update_one({'_id': ObjectId(card_id)}, {'$set': updated_data})
            #return JsonResponse({'status': 'success', 'message': 'Card updated successfully'})
        else:
            # Handle the case where 'card_id' is missing
            pass
        return redirect('my_cards')

    # Handle GET request
    cards_data = mongo_collection.find({})
    cards = []

    for card in cards_data:
        card['id'] = str(card['_id'])
        card['front_image_url'] = generate_presigned_url(f"cards/{card['front_image']}")
        card['back_image_url'] = generate_presigned_url(f"cards/{card['back_image']}")
        card['image_paths'] = [generate_presigned_url(f"{card[key]}") for key in card if key.startswith('image_path')]
        cards.append(card)

    return render(request, 'flashcards/allcards.html', {'cards': cards})

def my_decks(request):
    mongo_collection = mongo_handler()
    cards_data = mongo_collection.find({})

    # Create a dictionary to store deck information
    decks = defaultdict(lambda: {'count': 0, 'sample_cards': []})

    # Group cards by deck
    for card in cards_data:
        # Convert ObjectId to string and add as 'id'
        card['id'] = str(card['_id'])
        # Add the card to the corresponding deck
        decks[card['deck']]['count'] += 1
        if len(decks[card['deck']]['sample_cards']) < 5:
            decks[card['deck']]['sample_cards'].append(card)

    # Sort the decks by deck name
    sorted_decks = sorted(decks.items(), key=lambda x: x[0])
    return render(request, 'flashcards/alldecks.html', {'decks': sorted_decks})
    
def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()
    width = font.getmask(text_string).getbbox()[2]
    height = font.getmask(text_string).getbbox()[3] + descent 
    return (width, height)

def deck(request, deck_name=None):
    mongo_collection = mongo_handler()  # Ensure mongo_handler is defined elsewhere

    # Handle deck deletion
    if request.method == 'POST' and deck_name:
        mongo_collection.delete_many({"deck": deck_name})
        messages.info(request, 'Your deck has been removed.')
        return redirect('deck')

    # Handle new deck upload
    if request.method == 'POST' and ('csv_file' in request.FILES):
        deck_name, ext = os.path.splitext(request.FILES['csv_file'].name)

        # Attempt to detect the encoding of the CSV file
        raw_data = request.FILES['csv_file'].read()
        detected_encoding = chardet.detect(raw_data)['encoding']

        # Decode the file with the detected encoding
        try:
            decoded_file = raw_data.decode(detected_encoding).splitlines()
        except UnicodeDecodeError as e:
            messages.error(request, f'Error decoding file: {e}')
            return redirect('deck')

        reader = csv.DictReader(decoded_file)
        # Setup paths for fonts

        FONTNAME = regular_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Times New Roman Bold.ttf')
        regular_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Times New Roman Bold.ttf')
        print(f"fontname{FONTNAME}")
        font = ImageFont.truetype(FONTNAME, FONTSIZE)
        ipa_font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Times New Roman Bold.ttf')

        def get_text_dimensions(text_string, font):
            ascent, descent = font.getmetrics()
            width = font.getmask(text_string).getbbox()[2]
            height = font.getmask(text_string).getbbox()[3] + descent 
            return (width, height)
        # Load fonts
        regular_font = ImageFont.truetype(regular_font_path, FONTSIZE)
        #font = ImageFont.truetype(regular_font_path, FONTSIZE)
        ipa_font = ImageFont.truetype(ipa_font_path, FONTSIZE)
        font = ImageFont.truetype(regular_font_path, FONTSIZE)
        line_spacing = 300  # Additional space between lines, adjust as needed
    

        for row in reader:
            line_spacing = 200
            new_row = {key: value for key, value in row.items()}
            new_row['deck'] = deck_name
            new_row['reviewed'] = 0
            text_for_image = new_row.get('word', 'DefaultWord')
            image_filename = f"{deck_name}_{new_row['word']}".replace(' ', '_')

            # Create front and back images
            front_img = Image.new('RGB', (vdim, hdim), 'maroon')
            back_img = Image.new('RGB', (vdim, hdim), 'darkblue')
            #front_img = Image.new('RGB', (832, 1152), 'maroon')
            #back_img = Image.new('RGB', (832, 1152), 'darkblue')

            #line1 = -225
            #line2 =  -75
            #line3 = 75

            line1 = -75
            line2 =  75
            line3 = 225
            # Write text to front image
            write_image((vdim, hdim), new_row['word'], font, 'black', line1, front_img)
            write_image((vdim, hdim), "[" + new_row['p_ipa'] + "] " + new_row['approximation'] , font, 'black', line2, front_img)
            write_image((vdim, hdim), new_row['sentenceeng'], font, 'black', line3, front_img)

            # Write text to back image
            write_image((vdim, hdim), "[" + new_row['full_ipa'] + "] " + new_row['meaning'], font, 'black', line2, back_img)
            write_image((vdim, hdim), new_row['sentenceforeign'], font, 'black', line3, back_img)
            
            # Save images and construct relative paths
            audio_filename = f"{image_filename}.mp3"
            front_filename = f"{image_filename}_front.jpg"
            back_filename = f"{image_filename}_back.jpg"
            

            AWS_STORAGE_BUCKET_NAME="flashappbucket"
            key = f"cards/{front_filename}"
            buffer = io.BytesIO()
            front_img.save(buffer, "JPEG")
            buffer.seek(0)
            s3client.upload_fileobj(buffer, AWS_STORAGE_BUCKET_NAME, key)

            key = f"cards/{back_filename}"
            buffer = io.BytesIO()
            back_img.save(buffer, "JPEG")
            buffer.seek(0)
            s3client.upload_fileobj(buffer, AWS_STORAGE_BUCKET_NAME, key)

            try:
                #image_files, card_files = generate_image(f"A beautiful photo realistic and imaginative, depiction of the phrase \"{new_row['sentenceeng']}.\" If people in scenes are absolutely necessary, then show mostly alternative lifestyle, postapocalyptic lifestyle, with themes of science and future. But only insert people if absolutely necessary to get the meaning across visually. Hyper photo realistic. Add French culture. No text or fingers", image_filename)
                #for ai_card in card_files:
                #    with Image.open(ai_card) as card_write:
                #        print(f"writen card is here: {ai_card}")
                #        write_image((hdim, vdim), new_row['meaning']+ " [" + new_row['full_ipa'] + "]", font, 'black', line2, card_write)
                #        write_image((hdim, vdim), new_row['sentenceforeign'], font, 'black', line3, card_write)
                #        #write_image((hdim, vdim), SIMPLIFIED_CHAR, font, 'black', 75, card_write)
                #        card_write.save(ai_card, 'JPEG')
                #print(f'{image_filename}_front.jpg')

                        #audio creation
                #client = []
                #client = OpenAI(api_key="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")
                #audiofile = f"{new_row['word']}.mp3"
                #speech_file_path = os.path.join(settings.STATICFILES_DIRS[0]) + "/cards/" + audio_filename
                #speech_file_path = speech_file_path.replace('\\', '/')  # Normalize path for OS compatibility
                #print(audiofile)
                #print(speech_file_path)
                
                #response = []
                #response = client.audio.speech.create(
                #model="tts-1-hd",
                #voice="onyx",
                #input=new_row['sentenceforeign']
                #) 
                #response.stream_to_file(speech_file_path)
                #play_audio(speech_file_path)
                print(f"image_filename: {image_filename}")
                new_row.update({
                    'front_image': f'{image_filename}_front.jpg',
                    'back_image': f'{image_filename}_back.jpg',
                    'primary_image': f'{image_filename}_back.jpg',
                    #'primary_image': image_files[0] if image_files else None,  # Check if image_files is not empty
                    #'phraseaudio': audio_filename
                })

                # Update new_row with 'image_pathN' keys
                #for i in range(len(image_files)):
                #    new_row[f'image_path{i}'] = image_files[i]

            except ValueError as e:
                messages.error(request, f'Error generating image for "{text_for_image}": {e}')
                continue

            all_cards.append(new_row)

        mongo_collection.insert_many(all_cards)
        messages.info(request, 'Your deck has been uploaded.')
        return redirect('deck')
    
    # Prepare data for displaying decks with thumbnails
    all_docs = list(mongo_collection.find({}))
    decks = defaultdict(lambda: {'count': 0, 'sample_cards': []})

    for doc in all_docs:
        decks[doc['deck']]['count'] += 1
        if len(decks[doc['deck']]['sample_cards']) < 4:
            thumbnail_url = generate_presigned_url(f"cards/{doc['primary_image']}")
            print(f"primage: {doc['primary_image']}")
            print(f"thumb: {thumbnail_url}")
            doc['thumbnail_url'] = thumbnail_url
            decks[doc['deck']]['sample_cards'].append(doc)

    # Sort the decks by deck name
    sorted_decks = sorted(decks.items(), key=lambda x: x[0])

    return render(request, 'flashcards/deck.html', {'decks': sorted_decks}) 

from datetime import datetime
import pymongo

def generate_presigned_url(object_key):
    s3_client = boto3.client('s3')
    try:
        url = s3client.generate_presigned_url('get_object', Params={
            'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'Key': object_key,
        }, ExpiresIn=3600)  # URL expires in 1 hour
        return url
        print(f"url: {url}")
    except Exception as e:
        print("Error generating presigned URL: ", e)
        return None

def card(request, deck_name, word=None):
    mongo_collection = mongo_handler()
    current_time = datetime.now()

    # Handle POST request for updates
    if request.method == 'POST' and word:
        updated_data = {
            'word': request.POST.get('word'),
            'approximation': request.POST.get('approximation'),
            'sentenceeng': request.POST.get('sentenceeng'),
            'meaning': request.POST.get('meaning'),
            'sentenceforeign': request.POST.get('sentenceforeign'),
        }
        # Update the database
        mongo_collection.update_one({'word': word, 'deck': deck_name}, {'$set': updated_data})
        # Redirect to avoid double submission
        return redirect('card', deck_name=deck_name, word=word)


    # Handle specific word request
    if word:
        
        res = list(mongo_collection.find({"deck": deck_name}).sort([("word", pymongo.ASCENDING)]))
        indx = [i for i, d in enumerate(res) if word in d.values()]
        if not indx:  # If the word is not found
            # Handle this case appropriately, e.g., show an error message or a default card
            pass

        # Calculate the index for the next card
        next_indx = indx[0] + 1 if indx[0] + 1 < len(res) else 0
        next_word = res[next_indx]['word']

        # Calculate the index for the previous card
        prev_indx = indx[0] - 1 if indx[0] > 0 else len(res) - 1
        prev_word = res[prev_indx]['word']

        current_card = res[indx[0]]
        increment_reviewed(current_card, mongo_collection)

        # Find the next session date for the current card
        next_session = find_next_session(current_card)
        next_session_formatted = next_session.strftime("%A %d/%m/%Y %H:%M") if next_session else None

        front_image_url = generate_presigned_url(f"cards/{current_card['front_image']}")
        back_image_url = generate_presigned_url(f"cards/{current_card['primary_image']}")

        return render(request, 'flashcards/card.html', {
            'card': current_card,
            'front_image_url': front_image_url,
            'back_image_url': back_image_url,
            'next_word': next_word,
            'prev_word': prev_word,
            'next_session': next_session_formatted
        })

    # Handle the case where word is None
   


# Make sure to define your increment_reviewed and find_next_session functions as well
def increment_reviewed(card, mongo_handler):
    current_review_count = card.get('reviewed', 0)

    # Preparing the update query
    update_query = {"$set": {"reviewed": current_review_count + 1}}

    # If the card has been reviewed less than once
    if current_review_count < 5:
        current_time = datetime.now()
        session_timings = {
            "session0": current_time,
            "session1": current_time + timedelta(days=2),   # +2 days
            "session2": current_time + timedelta(days=7),   # +5 days from session1
            "session3": current_time + timedelta(days=14),  # +7 days from session2
            "session4": current_time + timedelta(days=28),  # +14 days from session3
            "session5": current_time + timedelta(days=60),   # +32 days from session4
            "session5": current_time + timedelta(days=180),  # +120 days from session4
            "session5": current_time + timedelta(days=365), # +185 days from session4
        }
        update_query["$set"].update(session_timings)

    # Updating the document in the MongoDB collection
    query = {'word': card.get('word'), 'deck': card.get('deck')}
    mongo_handler.update_one(query, update_query)
    return

@csrf_exempt
def log_correct_click(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        word = data.get('word')
        deck_name = data.get('deck')
        # Retrieve the card from the database
        mongo_collection = mongo_handler()
        card = mongo_collection.find_one({"word": word, "deck": deck_name})
        if card:
            increment_reviewed(card, mongo_collection)
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"})

def find_next_session(card):
    current_time = datetime.now()
    session_keys = ['session1', 'session2', 'session3', 'session4', 'session5', 'session6', 'session7']

    for key in session_keys:
        session_time = card.get(key)
        if session_time and session_time > current_time:
            return session_time
    return None

def check_and_generate_images():
    mongo_collection = mongo_handler()  # Make sure this is properly defined
    cards_data = mongo_collection.find()

    for card in cards_data:
        if 'word' in card:
                image_filename = f"{card['deck']}_{card['word']}".replace(' ', '_')
                image_path = os.path.join(settings.STATICFILES_DIRS[0], 'cards', image_filename)

                if not os.path.exists(image_path):
                    print(image_path)
                    print(f"Generating Image for ID {card['_id']} Deck: {card['deck']} {card['word']}")
                    generate_image(f"A beautiful photo realistic and imaginative, depiction of the phrase \"{card['sentenceeng']}.\" If people in scenes are absolutely necessary, then show mostly alternative lifestyle, postapocalyptic lifestyle, with themes of science and future. But only insert people if absolutely necessary to get the meaning across visually. Hyper photo realistic. Add French culture. No text or fingers", image_filename)
        else:
            print(f"Card missing 'word': ID {card['_id']} in deck {card['deck']}")

