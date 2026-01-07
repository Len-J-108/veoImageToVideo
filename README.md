KieAI Video Generation
 Overview
This project generates a video using the KieAI VEO3 model by providing a reference image and text prompts. It leverages asynchronous API calls for optimal performance.
 Setup
1. **Clone this repository:**
      git clone <repo-url>
   cd <repo-directory>
2. Set up a virtual environment:
      python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
3. Install the dependencies:
      pip install -r requirements.txt
   
4. Environment Variables:
   Create a .env file in the root directory with your KieAI API key:
      KIE_API_KEY=your_actual_api_key_here
   
Usage
Run the script with the following command:
python src/main.py --reference-image-url <URL> --prompt "<prompt>" --monologue "<monologue>" --directions "<directions>" --topic "<topic>" --language <language> --duration <duration>
Example
python src/main.py --reference-image-url http://example.com/image.jpg --prompt "An inspiring story..." --monologue "Hello there..." --directions "Angry mood" --topic "Hope" --language "german" --duration 12
