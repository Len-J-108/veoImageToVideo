# VEO Image-to-Video Workflow

This project submits a hardcoded generation request to KieAI's VIE API to transform a
reference image of a person seated on a stone bench into an eight-second, vertical video.
The resulting clip shows the subject standing up, walking around the bench, narrating in
German, and ending with a confident outro pose. Logging covers every major step—from
configuration load, through polling and retries, to streaming the finished MP4 into
`./results/stone-bench-walkthrough-intro.mp4`.

## Prerequisites

- Python 3.11+
- A valid KieAI API key with access to the `veo3` model
- Network egress to `https://api.kieai.com`

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

| Variable | Description |
| --- | --- |
| `KIEAI_API_KEY` | **Required**. Bearer token passed to the VIE API. |
| `KIEAI_BASE_URL` | Optional. Defaults to `https://api.kieai.com/v1`. |

All other inputs (topic, reference image URL, narration text, directions, duration, aspect
ratio) remain hardcoded per project requirements. The application creates `./results/`
automatically before downloading the video.

## Usage

```bash
python -m src.main
```

Execution flow:

1. Load configuration and compose the German prompt/stage directions.
2. Submit a `veo3` generation request referencing the bench photo.
3. Poll the task every 20 seconds (up to 10 minutes) with logged status transitions.
4. Stream the finished MP4 to `results/stone-bench-walkthrough-intro.mp4` and log the
   completion message.

Any HTTP failures encounter logged retries with exponential-style backoff. Timeouts,
failures, and missing asset URLs raise descriptive exceptions so automation can react.
