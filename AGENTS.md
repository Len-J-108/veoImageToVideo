# AGENTS.md
This project builds a Python application that converts a reference image—a person seated on a bench in front of a stone wall—into an animated 8-second (9:16) video using KieAI's VIE API with the `veo3` model. The person must walk around while speaking hardcoded German dialogue. Follow these rules when contributing.
## Architecture Expectations
- Maintain a modular, functional layout under `src/`:
  - `config.py`: constants/env access (API key name, base URL, topic string, reference image URL, speech text, stage direction, outro description, duration, aspect ratio, poll interval, timeout, results directory).
  - `models.py`: dataclasses/pydantic models for request payloads and task responses.
  - `prompt_builder.py`: pure functions composing the German narration, stage directions, speech text, outro instructions, and reference image metadata.
  - `client.py`: HTTP wrapper for submitting generation jobs and retrieving/polling task IDs.
  - `downloader.py`: streams completed MP4 assets into `./results/<topic>-intro.mp4`.
  - `main.py` (or similar) orchestrating the flow.
- Inputs remain hardcoded; CLI arguments or external configs are future enhancements.
## API Usage & Polling
- Always call KieAI with `model="veo3"`, supplying the provided reference image URL, 8-second duration, and 9:16 aspect ratio.
- Upon task creation, log the task ID (e.g., "Task <id> generated, video processing...") and poll its status every 20 seconds until completion or a long timeout (≥10 minutes).
- Implement retries/backoff for transient HTTP failures. Log each status transition (`processing`, `completed`, `failed`, timeouts).
## Output Handling
- Ensure `./results/` exists prior to saving. Write the final MP4 to `./results/<topic>-intro.mp4`, overwriting only when intended.
- Downloader should stream downloads to disk and log both start and completion events (e.g., "Processing finished", "Video saved to ./results/<topic>-intro.mp4").
## Logging Requirements
- Use INFO-level structured logging with timestamps, covering configuration load, prompt building, generation initiation, task ID, each polling iteration, completion/failure, download, and timeout conditions.
## Extensibility
- Continue updating documentation (README, etc.) whenever defaults or workflows change.
- Future contributors may add CLI or config support, but current baseline must function entirely via hardcoded defaults.
