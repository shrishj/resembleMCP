# Resemble AI Voice Generation MCP

A simple MCP server for generating voice clips using Resemble AI's API.

## Setup

1. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file in the project root and add your Resemble AI API key:
```bash
RESEMBLE_API_KEY=your_api_key_here
```

## Available Functions

### List Available Voices
```python
list_available_voices(page=1, page_size=10)
```
Returns a list of available voices from Resemble AI.

### List Projects
```python
list_projects(page=1, page_size=10)
```
Returns a list of your Resemble AI projects.

### Create Project
```python
create_project(name="My Project")
```
Creates a new project in Resemble AI.

### Generate Voice
```python
generate_voice(
    text="Hello world",
    voice_uuid="your_voice_uuid",
    project_uuid="your_project_uuid",
    sample_rate=22050,
    precision="PCM_16"
)
```
Generates voice audio from text. Returns base64 encoded WAV audio data.

## Example Usage

```python
# List available voices
voices = list_available_voices()

# Create a new project
project = create_project("My Voice Project")

# Generate voice audio
result = generate_voice(
    text="Hello, this is a test!",
    voice_uuid="voice_uuid_from_list_available_voices",
    project_uuid="project_uuid_from_create_project"
)

if result["success"]:
    # Audio data is in result["audio_data_base64"]
    print("Voice generation successful!")
```

## Requirements
- Python 3.7+
- mcp>=0.1.0
- resemble>=1.0.0
- python-dotenv>=0.19.0