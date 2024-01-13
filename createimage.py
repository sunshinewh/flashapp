#!/usr/bin/python
# -*- coding: utf-8 -*-
import textwrap
import stability_sdk
import os
import openai  # pip install openai
import urllib.request
import datetime
import io
import warnings
from IPython.display import display
from PIL import Image
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
# Importing the PIL library
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import getopt
import sys
import getopt

#lets fetch all the arguments from sys.argv except the script name
argv = sys.argv[1:]
#get option and value pair from getopt
try:
    opts,argv = getopt.getopt(argv, "s:f:t:", ["string =","filename ="])
    #lets's check out how getopt parse the arguments
    print(opts)
except:
    print('pass the arguments like -s <string to print> -f <file name> or --string <string to print> and --filename <file name>')
for o,v in opts:
    if o in ['-s','--string']:
        string = v
    elif o in ['-f','--filename']:
        filename = v
  
print(string + ' ' + filename)

#font = ImageFont.truetype("DejaVu Sans Bold.ttf", 64)
font = ImageFont.truetype("/c/Temp/pyfiles/django-example-main/flashcards/fonts/static/NotoSansSC-ExtraBold.ttf", 40)

text_color = (255, 255, 255) # white


def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()
    width = font.getmask(text_string).getbbox()[2]
    height = font.getmask(text_string).getbbox()[3] + descent 
    return (width, height)

os.environ['STABILITY_HOST'] = 'grpc.stability.ai:443'
os.environ['STABILITY_KEY'] = "sk-gyLG03XUnY4HWeuocSwbCXKTKRzPpVR8W2Jq1dRUXFF28JGi"

stability_api = client.StabilityInference(
    key=os.environ['STABILITY_KEY'], # API Key reference.
    verbose=True, # Print debug messages.
    engine="stable-diffusion-768-v2-1", # Set the engine to use for generation.
    # Check out the following link for a list of available engines: https://platform.stability.ai/docs/features/api-parameters#engine
)

answers = stability_api.generate(
    prompt= string,
    seed=4253978046, # If a seed is provided, the resulting generated image will be deterministic.
    steps=50, # Amount of inference steps performed on image generation. Defaults to 30.
    cfg_scale=8.0, # Influences how strongly your generation is guided to match your prompt.
    width=832, # Generation width, defaults to 512 if not included.
    height=1152, 
    samples=1, 
    sampler=generation.SAMPLER_K_DPMPP_2M )


for resp in answers:
    for artifact in resp.artifacts:
        if artifact.finish_reason == generation.FILTER: 
            warnings.warn("Your request activated the API's safety filters and could not be processed.Please modify the prompt and try again.")
        if artifact.type == generation.ARTIFACT_IMAGE: 
            img = Image.open(io.BytesIO(artifact.binary))

#font = ImageFont.truetype("DejaVu Sans Bold.ttf", 64)
font = ImageFont.truetype("/c/Temp/pyfiles/django-example-main/flashcards/fonts/static/NotoSansSC-ExtraBold.ttf", 40)

text_color = (255, 255, 255) # white


#text = "This is a test"
text = "光"
lines = textwrap.wrap(text, width=40)
draw = ImageDraw.Draw(img)

max_width = 0
total_height = 0

for line in lines:
    width, height = get_text_dimensions(line, font)
    max_width = max(max_width, width)
    total_height += height
    x = (img.width - max_width) // 2
    y = (img.height - total_height) // 2
    line_heights = []


for line in lines:
    width, height = get_text_dimensions(line, font)
    line_heights.append(height)
    line_y = y


for i in range(len(lines)):
    line_x = x + (max_width - draw.textsize(lines[i], font=font)[0]) // 2
    draw.text((line_x, line_y), lines[i], fill=text_color, font=font)
    line_y += line_heights[i]

img.save('./media/'+filename+'.jpg', 'JPEG')
