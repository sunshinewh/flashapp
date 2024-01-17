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
from PIL import Image, ImageDraw, ImageFont
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST
from .utils import set_primary_image  # Importing from utils.py
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

hdim = 832
vdim = 1152
FONTSIZE = 70
SHADOWWIDTH = 4

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

# Set your Stability API Key and host
STABILITY_API_KEY = "sk-gyLG03XUnY4HWeuocSwbCXKTKRzPpVR8W2Jq1dRUXFF28JGi"
STABILITY_HOST = "grpc.stability.ai:443"

# Initialize the Stability client
stability_api = client.StabilityInference(
    key=STABILITY_API_KEY,
    verbose=True,
    engine="stable-diffusion-xl-1024-v1-0",
)

def generate_image(text_string, filename_base):
    static_path = []
    image_paths = []  # Initialize image_paths as an empty list
    ai_paths = []
    seednums = [] 
    ai_path = []
    cards_path = []
    card_files = []
    
    # Initialize the Stability client if not already initialized
    stability_api = client.StabilityInference(
        key=STABILITY_API_KEY,
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0",
    )
    

    # Generate images
    for i in range(4):
        filename = f"{filename_base}_{i}.jpg"
        print(filename)
        # First File Path - in the static directory
        static_path = os.path.join(settings.STATICFILES_DIRS[0], filename)
        static_path = static_path.replace('\\', '/')  # Normalize path for OS compatibility

        # Second File Path - in the 'cards' subdirectory under static
        cards_path = os.path.join(settings.STATICFILES_DIRS[0], 'cards', filename)
        cards_path = cards_path.replace('\\', '/')  # Normalize path for OS compatibility

        # Generate a random 8-digit number
        random_number = random.randint(10000, 99999)
       
        # Call the API to generate the image
        answers = stability_api.generate(
            prompt=text_string,
            seed=random_number,  # Modify seed for each image for variability
            steps=50,
            cfg_scale=8.0,
            width=832,
            height=1152,
            samples=1,  # If the API supports generating multiple images at once, set this to 4 and adjust the loop
            sampler=generation.SAMPLER_K_DPMPP_2M
        )
        
        # Process the response and create the image
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    raise ValueError("Request activated the API's safety filters and could not be processed.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary)) 
                    img.save(static_path, 'JPEG')
                    image_paths.append(filename)  # Append to image_paths
                    img.save(cards_path, 'JPEG') 
                    card_files.append(cards_path)  # Append to image_paths
                    print(f"Saved to static: {static_path}")   
                    print(f"Saved to cards: {cards_path}")   
                    print(f"Saved card file locations: {card_files}")   
    return image_paths, card_files

def home(request):
	return render(request, 'general/home.html')

@require_POST
def set_primary_image_view(request):
    # Decode the request body to JSON
    data = json.loads(request.body)
    card_id = data.get('cardId')
    new_image_path = data.get('imagePath')

    if card_id and new_image_path:
        set_primary_image(card_id, new_image_path)
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid data received'})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from bson import ObjectId

# Assume mongo_handler() is a function that returns a MongoDB collection
#from your_app_name.mongo_utils import mongo_handler

@csrf_exempt
def update_primary_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        card_id = data['cardId']
        image_path = data['imagePath']

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

def my_cards(request):
    mongo_collection = mongo_handler()
    cards_data = mongo_collection.find({})
    cards = []

    for card in cards_data:
        # Convert ObjectId to string and add as 'id'
        card['id'] = str(card['_id'])
        # Create full image paths dynamically based on existing keys
        card['image_paths'] = [card[key] for key in card if key.startswith('image_path')]
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
        all_cards = []
        card_write = []
        card_files = []

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
            static_path = []
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
            text_for_image = new_row['word']
            image_filename = f"{deck_name}_{new_row['word']}".replace('\\', '/')
            print(f"Word: {text_for_image}")
            print(f"image_filename: {image_filename}")
            

            # Create front and back images
            front_img = Image.new('RGB', (vdim, hdim), 'maroon')
            back_img = Image.new('RGB', (vdim, hdim), 'darkblue')
            #front_img = Image.new('RGB', (832, 1152), 'maroon')
            #back_img = Image.new('RGB', (832, 1152), 'darkblue')

            # Gather all texts and corresponding fonts for front and back images
            front_texts = [new_row['word'], new_row['approximation'] + " [" + new_row['p_ipa'] + "]", new_row['sentenceeng']]
            front_fonts = [regular_font, ipa_font, regular_font]
            print(f"front fonts {front_fonts}")
            back_texts = [new_row['meaning']+ " [" + new_row['full_ipa'] + "]", new_row['sentenceforeign']]
            back_fonts = [regular_font, ipa_font, regular_font]
            
            #line1 = -225
            #line2 =  -75
            #line3 = 75

            line1 = -75
            line2 =  75
            line3 = 225
            # Write text to front image
            write_image((vdim, hdim), new_row['word'], font, 'black', line1, front_img)
            write_image((vdim, hdim), new_row['approximation'] + " [" + new_row['p_ipa'] + "]", font, 'black', line2, front_img)
            write_image((vdim, hdim), new_row['sentenceeng'], font, 'black', line3, front_img)

            # Write text to back image        
            write_image((vdim, hdim), new_row['meaning']+ " [" + new_row['full_ipa'] + "]", font, 'black', line2, back_img)
            write_image((vdim, hdim), new_row['sentenceforeign'], font, 'black', line3, back_img)
            
            # Save images and construct relative paths
            front_image_path = os.path.join('cards', f'{image_filename}_front.jpg')
            back_image_path = os.path.join('cards', f'{image_filename}_back.jpg')

            audio_filename = f"{image_filename}.mp3"
            front_filename = f"{image_filename}_front.jpg"
            back_filename = f"{image_filename}_back.jpg"
            
            # First File Path - in the static directory
            staticfilesdirs = os.path.join(settings.STATICFILES_DIRS[0]) + "/cards/"
            front_filename = os.path.join(settings.STATICFILES_DIRS[0], 'cards', front_filename)
            front_filename = front_filename.replace('\\', '/')   # Normalize path for OS compatibility
            back_filename = os.path.join(settings.STATICFILES_DIRS[0], 'cards', back_filename)
            back_filename = back_filename.replace('\\', '/')  # Normalize path for OS compatibility
            print(staticfilesdirs)
            print(back_filename)
            front_img.save(front_filename), 'JPEG'
            back_img.save(back_filename), 'JPEG'

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
                front_image_path = front_image_path.replace('\\', '/') 
                back_image_path = back_image_path.replace('\\', '/') 
                new_row.update({
                    'front_image': f'{image_filename}_front.jpg',
                    'image_path_back': f'{image_filename}_back.jpg',
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
            decks[doc['deck']]['sample_cards'].append(doc)

    # Sort the decks by deck name
    sorted_decks = sorted(decks.items(), key=lambda x: x[0])
    
    # At the point in the view where you want to trigger the task:
    async_task(check_and_generate_images)

    return render(request, 'flashcards/deck.html', {'decks': sorted_decks}) 



from datetime import datetime

from datetime import datetime
import pymongo

def card(request, deck_name, word=None):
    mongo_collection = mongo_handler()
    current_time = datetime.now()

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

        return render(request, 'flashcards/card.html', {
            'card': current_card,
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
                image_filename = f"{card['deck']}_{card['word']}"
                image_path = os.path.join(settings.STATICFILES_DIRS[0], 'cards', image_filename)

                if not os.path.exists(image_path):
                    print(image_path)
                    print(f"Generating Image for ID {card['_id']} Deck: {card['deck']} {card['word']}")
                    generate_image(f"A beautiful photo realistic and imaginative, depiction of the phrase \"{card['sentenceeng']}.\" If people in scenes are absolutely necessary, then show mostly alternative lifestyle, postapocalyptic lifestyle, with themes of science and future. But only insert people if absolutely necessary to get the meaning across visually. Hyper photo realistic. Add French culture. No text or fingers", image_filename)
        else:
            print(f"Card missing 'word': ID {card['_id']} in deck {card['deck']}")


