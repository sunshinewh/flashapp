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

# Set the path to the fonts you wish to use
FONT_PATH = "/path/to/your/fonts/NotoSansSC-ExtraBold.ttf"

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
    static_paths = []
    image_paths = []  # Initialize image_paths as an empty list
    seednums = [] 
    
    # Initialize the Stability client if not already initialized
    stability_api = client.StabilityInference(
        key=STABILITY_API_KEY,
        verbose=True,
        engine="stable-diffusion-xl-1024-v1-0",
    )
    
    # Generate 4 images
    for i in range(4):
        filename = f"{filename_base}_{i}.jpg"
        static_path = os.path.join('static', filename)
        static_path = static_path.replace('\\', '/') 
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
                    image_paths.append(static_path)  # Append to image_paths
                    
    return image_paths 


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
            {'$set': {'primary_image': image_path}}
        )

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
        # Create full image paths
        card['image_paths'] = [f"{card['image_path' + str(i)]}" for i in range(4)]
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
        if len(decks[card['deck']]['sample_cards']) < 4:
            decks[card['deck']]['sample_cards'].append(card)

    # Sort the decks by deck name
    sorted_decks = sorted(decks.items(), key=lambda x: x[0])

    return render(request, 'flashcards/alldecks.html', {'decks': sorted_decks})

def deck(request, deck_name=None):
    mongo_collection = mongo_handler()

    if request.method == 'POST' and deck_name:
        mongo_collection.delete_many({"deck": deck_name})
        messages.info(request, 'Your deck has been removed.')
        return redirect('deck')
    
    if request.method == 'POST' and ('csv_file' in request.FILES):
        deck_name, ext = os.path.splitext(request.FILES['csv_file'].name)
        decoded_file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)
        all_cards = []

        for row in reader:
            new_row = {key: value for key, value in row.items()}
            new_row['deck'] = deck_name
            new_row['reviewed'] = 0
            

            text_for_image = new_row['word']
            image_filename = f"{deck_name}_{text_for_image}".replace('\\', '/')

            try:
                image_paths = generate_image(f"A beautiful and imaginative depiction of {text_for_image}, infused with {deck_name} culture, without text or strange body renderings", image_filename)
                new_row.update({
                    'primary_image': image_paths[0],
                    'image_path0': image_paths[0] if len(image_paths) > 0 else None,
                    'image_path1': image_paths[1] if len(image_paths) > 1 else None,
                    'image_path2': image_paths[2] if len(image_paths) > 2 else None,
                    'image_path3': image_paths[3] if len(image_paths) > 3 else None,
                })
            except ValueError as e:
                messages.error(request, f'Error generating image for "{text_for_image}": {e}')
                continue

            all_cards.append(new_row)

        mongo_collection.insert_many(all_cards)
        messages.info(request, 'Your deck has been uploaded.')
        return redirect('deck')
    
    all_docs = list(mongo_collection.find({}))
    decks_count = defaultdict(int)
    for doc in all_docs:
        decks_count[doc['deck']] += 1
    
    return render(request, 'flashcards/deck.html', {'decks': dict(decks_count)})
   
    

def card(request, deck_name, word=None):
	mongo_collection= mongo_handler()
	if word:
		res = list(mongo_collection.find({"deck": deck_name}).sort([("word", pymongo.ASCENDING)]))
		indx = [i for i, d in enumerate(res) if word in d.values()]
		new_indx = [indx[0]+1 if indx[0]+1 < len(res) else 0]
		next_card = res[new_indx[0]]
		increment_reviewed(next_card, mongo_collection)
		return render(request, 'flashcards/card.html', {'card': next_card})
	res = list(mongo_collection.find({"deck": str(deck_name)}).sort([("word", pymongo.ASCENDING)]))
	first_card = res[0]
	increment_reviewed(first_card, mongo_collection)
	return render(request, 'flashcards/card.html', {'card': first_card})


def increment_reviewed(card, mongo_handler):
	query = { 'word': card.get('word'), 'deck': card.get('deck') }
	updated_card = { "$set": { 'reviewed': card.get('reviewed') + 1 } }
	mongo_handler.update_one(query, updated_card)
	return