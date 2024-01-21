import base64
import io
import requests
from PIL import Image

STABILITY_API_KEY = "sk-gyLG03XUnY4HWeuocSwbCXKTKRzPpVR8W2Jq1dRUXFF28JGi"
api_host = 'https://api.stability.ai'
api_key = STABILITY_API_KEY
engine_id = "stable-diffusion-v1-6"

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
                image.show()