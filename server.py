"""
Resemble AI Voice Generation MCP Server

This module provides an MCP server interface for Resemble AI's voice generation API.
It includes functionality for managing projects, listing voices, and generating voice clips.
"""

import os
import requests
import json
import base64
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from resemble import Resemble

# Load environment variables
load_dotenv()

# Initialize MCP server
mcp = FastMCP("voice")

# Ensure you have a .env or set the API key
RESEMBLE_API_KEY = os.getenv('RESEMBLE_API_KEY')
if not RESEMBLE_API_KEY:
    raise ValueError("RESEMBLE_API_KEY not found in environment variables. Please set it in .env file")

Resemble.api_key = RESEMBLE_API_KEY

@mcp.tool()
def generate_voice(
    text: str, 
    voice_uuid: str, 
    project_uuid: str, 
    api_token: Optional[str] = None, 
    sample_rate: int = 22050,
    precision: str = "PCM_16"
) -> Dict[str, Any]:
    """
    Generate a voice clip using Resemble AI's streaming API.

    Args:
        text (str): The text to convert to speech
        voice_uuid (str): UUID of the voice to use
        project_uuid (str): UUID of the project
        api_token (Optional[str]): Optional API token, defaults to environment variable
        sample_rate (int): Audio sample rate in Hz (default: 22050)
        precision (str): Audio precision format (default: "PCM_16")

    Returns:
        Dict[str, Any]: Response containing:
            - success (bool): Whether the operation succeeded
            - audio_data_base64 (str): Base64 encoded WAV audio data (if successful)
            - error (str): Error message (if failed)
    """
    token = api_token or RESEMBLE_API_KEY
    if not token:
        return {"success": False, "error": "No API token provided"}

    url = "https://f.cluster.resemble.ai/stream"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "project_uuid": project_uuid,
        "voice_uuid": voice_uuid,
        "data": text,
        "precision": precision,
        "sample_rate": sample_rate
    }
    
    try:
        # First check if the request is accepted
        response = requests.post(url, headers=headers, json=payload, stream=True)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"API request failed with status code: {response.status_code}"
            }

        # Process the stream in chunks
        chunks = []
        total_size = 0
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                chunks.append(chunk)
                total_size += len(chunk)
                if total_size > 10 * 1024 * 1024:  # Limit to 10MB
                    return {
                        "success": False,
                        "error": "Audio response too large (>10MB)"
                    }

        # Combine chunks and encode
        try:
            audio_bytes = b''.join(chunks)
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return {
                "success": True,
                "audio_data_base64": audio_base64,
                "content_type": "audio/wav",
                "sample_rate": sample_rate,
                "precision": precision,
                "size_bytes": len(audio_bytes)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process audio data: {str(e)}"
            }
            
    except requests.RequestException as e:
        return {"success": False, "error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def list_available_voices(
    page: int = 1,  # Changed default from 10 to 1
    page_size: int = 10
) -> Dict[str, Any]:
    """
    List available voices from Resemble AI.

    Args:
        page (int): Page number for pagination (default: 1)
        page_size (int): Number of items per page (default: 10)

    Returns:
        Dict[str, Any]: Response containing list of voices or error message
    """
    url = "https://app.resemble.ai/api/v2/voices"
    headers = {
        "Authorization": f"Bearer {RESEMBLE_API_KEY}",
        "Content-Type": "application/json"
    }
    params = {
        "page": page,
        "page_size": page_size
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        return response.json()
    except requests.RequestException as e:
        return {"success": False, "error": f"API request failed: {str(e)}"}
    except json.JSONDecodeError:
        return {"success": False, "error": "Failed to parse API response"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def list_projects(page: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """
    List all projects from Resemble AI.

    Args:
        page (int): Page number for pagination (default: 1)
        page_size (int): Number of items per page (default: 10)

    Returns:
        Dict[str, Any]: Response containing:
            - success (bool): Whether the operation succeeded
            - projects (list): List of project data (if successful)
            - error (str): Error message (if failed)
            - Pagination metadata
    """
    url = "https://app.resemble.ai/api/v2/projects"
    headers = {
        "Authorization": f"Bearer {RESEMBLE_API_KEY}",
        "Accept": "application/json"
    }
    params = {
        "page": page,
        "page_size": page_size
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return {
                    "success": True,
                    "page": data.get("page"),
                    "num_pages": data.get("num_pages"),
                    "page_size": data.get("page_size"),
                    "projects": data.get("items", [])
                }
            else:
                return {
                    "success": False,
                    "error": "API request successful but returned no data"
                }
        elif response.status_code == 401:
            return {
                "success": False,
                "error": "Authentication failed. Please check your API key."
            }
        else:
            return {
                "success": False,
                "error": f"API returned status code {response.status_code}",
                "response": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

@mcp.tool()
def create_project(name: str) -> Dict[str, Any]:
    """
    Create a new project in Resemble AI.

    Args:
        name (str): Name of the project to create

    Returns:
        Dict[str, Any]: Response containing:
            - success (bool): Whether the operation succeeded
            - project (dict): Project details (if successful)
            - error (str): Error message (if failed)
    """
    url = "https://app.resemble.ai/api/v2/projects"
    headers = {
        "Authorization": f"Bearer {RESEMBLE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "name": name,
        "description": "Created via API"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in (200, 201):
            data = response.json()
            return {
                "success": True,
                "project": data.get("item", {})
            }
        else:
            return {
                "success": False,
                "error": f"API returned status code {response.status_code}",
                "response": response.text
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Request failed: {str(e)}"
        }

if __name__ == "__main__":
    mcp.run()