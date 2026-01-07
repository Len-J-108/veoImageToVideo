import aiohttp
import logging
logger = logging.getLogger(__name__)
async def build_payload(prompt, monologue, directions, language, reference_url, duration_secs, model="veo3"):
    final_prompt = f"{prompt}\n{monologue}\n{directions}"
    return {
        "prompt": final_prompt,
        "imageUrls": [reference_url],
        "aspectRatio": "9:16",
        "model": model,
        "generationType": "REFERENCE_2_VIDEO",
        "duration": duration_secs,
        "language": language
    }
async def submit_generation(session, api_key, payload):
    url = "https://api.kie.ai/api/v1/veo/generate"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    async with session.post(url, headers=headers, json=payload) as response:
        if response.status != 200:
            logger.error(f"Failed to submit generation: {await response.text()}")
            response.raise_for_status()
        return await response.json()
async def fetch_status(session, api_key, task_id):
    url = f"https://api.kie.ai/api/v1/veo/record-info?taskId={task_id}"
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    async with session.get(url, headers=headers) as response:
        if response.status != 200:
            logger.error(f"Failed to fetch status: {await response.text()}")
            response.raise_for_status()
        return await response.json()
async def download_video(session, url, output_path):
    async with session.get(url) as response:
        if response.status != 200:
            logger.error(f"Failed to download video: {await response.text()}")
            response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(await response.read())
