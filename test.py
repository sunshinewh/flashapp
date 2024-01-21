import base64
import io
import requests
from PIL import Image
import boto3

AWS_ACCESS_KEY_ID='AKIAVJ2P6UW7XPTFZ2XT'
AWS_SECRET_ACCESS_KEY='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'
AWS_STORAGE_BUCKET_NAME="flashappbucket"
AWS_S3_REGION_NAME='us-west-2'

STABILITY_API_KEY = "sk-gyLG03XUnY4HWeuocSwbCXKTKRzPpVR8W2Jq1dRUXFF28JGi"
api_host = 'https://api.stability.ai'
api_key = STABILITY_API_KEY
engine_id = "stable-diffusion-v1-6"

s3client = boto3.client(
    's3',
    aws_access_key_id='AKIAVJ2P6UW74SZHNEMD',
    aws_secret_access_key='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',
    region_name='us-west-2'
)

if api_key is None:
    raise Exception("Missing Stability API key.")

response = requests.post(
    f"{api_host}/v1/generation/{engine_id}/text-to-image",
    headers={
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    },
    json={
        "text_prompts": [
            {
                "text": "A lighthouse on a cliff"
            }
        ],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
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

                key = f"cards/test4.jpg"
                buffer = io.BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)
                s3client.upload_fileobj(buffer, AWS_STORAGE_BUCKET_NAME, key)

                key = f"raw/test4.jpg"
                buffer = io.BytesIO()
                image.save(buffer, format="JPEG")
                buffer.seek(0)
                s3client.upload_fileobj(buffer, AWS_STORAGE_BUCKET_NAME, key)