import argparse
import asyncio
import logging
import os
from config import KIE_API_KEY, DEFAULT_LANGUAGE, DEFAULT_DURATION
from kie_client import build_payload, submit_generation, fetch_status, download_video

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def generate_intro_video(reference_image_url, prompt, spoken_language, monologue, character_directions, topic_name, video_length_seconds):
    async with aiohttp.ClientSession() as session:
        payload = await build_payload(prompt, monologue, character_directions, spoken_language, reference_image_url, video_length_seconds)
        response = await submit_generation(session, KIE_API_KEY, payload)
        task_id = response["data"]["taskId"]
        
        logger.info(f"Video generation task submitted. Task ID: {task_id}")
        
        # Implement logic for polling video generation...
        # (To be filled in)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a video from a reference image.")
    parser.add_argument('--reference-image-url', required=True, help='URL of the reference image')
    parser.add_argument('--prompt', required=True, help='Text prompt for video generation')
    parser.add_argument('--monologue', required=True, help='The spoken monologue')
    parser.add_argument('--directions', required=True, help='Character mood and behaviors directions')
    parser.add_argument('--topic', required=True, help='Topic for naming the video file')
    parser.add_argument('--language', default=DEFAULT_LANGUAGE, help='Language for the spoken content')
    parser.add_argument('--duration', type=int, default=DEFAULT_DURATION, help='Duration of the video in seconds')
    args = parser.parse_args()
    asyncio.run(generate_intro_video(args.reference_image_url, args.prompt, args.language, args.monologue, args.directions, args.topic, args.duration))
