import cv2
import numpy as np
from moviepy import VideoFileClip
from PIL import Image
import base64
import io
import os
from openai import OpenAI
from skimage.metrics import structural_similarity as ssim
import tempfile
from typing import Dict, List, Tuple, Any
import json


import requests
import os

BASE_ADK_URL = "https://shield-agent-service-952359417443.us-central1.run.app"
APP_NAME = "shield-agent-app"
USER_ID = "TEST_USER"
SESSION_ID = "TEST_SESSION"

def create_session():
    headers = {
        'Content-Type': 'application/json',
    }

    json_data = {
        'app_name': APP_NAME,
        'user_id': USER_ID,
        'session_id': USER_ID,
    }

    response = requests.post(BASE_ADK_URL + f'/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}', headers=headers, json=json_data)
    print(response.text)
    

def get_response_adk(frames, audio_path):
    create_session()
    headers = {
        'Content-Type': 'application/json',
    }

    messages = [
        {
            "role": "user", 
            "content": [
                {"type": "input_text", "text": "Analyze these video frames for appropriate playback speed for babies:"}
            ]
        }
    ]
    
    # Add frames to message
    for i, frame_b64 in enumerate(frames):
        messages[0]["content"].append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{frame_b64}"
        })

    json_data = {
        'app_name': APP_NAME,
        'user_id': USER_ID,
        'session_id': SESSION_ID,
        'new_message': {
            'role': 'user',
            'parts': [
                {
                    'text': json.dumps(messages),
                },
            ],
        },
        'streaming': False,
    }

    response = requests.post(BASE_ADK_URL+ '/run_sse', headers=headers, json=json_data)

    print("RAW")
    print(response.text)

    merged_res = json.loads(response.text.split("data: ")[-1])
    raw = merged_res["content"]["parts"][0]["text"]
    import re

    clean = re.sub(r"^```(?:json)?\n|\n```$", "", raw.strip(), flags=re.MULTILINE)

    # 2. Fix unquoted keys (turn {a: 10} into {"a": 10})
    clean = re.sub(r'(\w+):', r'"\1":', clean)

    # 3. Parse
    data = json.loads(clean)

    return data

# Initialize OpenAI client (make sure to set OPENAI_API_KEY environment variable)
client = OpenAI()

def extract_smart_frames(video_path: str, max_frames: int = 25) -> List[np.ndarray]:
    """
    Extract frames intelligently using scene change detection and content diversity.
    Uses structural similarity to avoid duplicate frames.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    frames = []
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = frame_count / fps
    
    # Calculate frame intervals for sampling
    interval = fps * 2 
    prev_frame_gray = None
    selected_frames = []
    
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        if frame_idx % interval == 0:
            # Convert to grayscale for comparison
            selected_frames.append(frame)
            
        frame_idx += 1
    
    cap.release()
    
    return selected_frames

def extract_audio_segment(video_path: str, duration_seconds: int = 30) -> str:
    """
    Extract a representative audio segment from the video.
    Returns path to temporary audio file.
    """
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        
        if audio is None:
            return None
        
        # Save to temporary file
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        audio.write_audiofile(temp_audio.name, logger=None)
        
        audio.close()
        video.close()
        
        return temp_audio.name
    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None

def encode_frame_to_base64(frame: np.ndarray) -> str:
    """Convert OpenCV frame to base64 encoded image."""
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(frame_rgb)
    
    # Resize for API efficiency (max 512px on longest side)
    width, height = pil_image.size
    max_size = 512
    if max(width, height) > max_size:
        ratio = max_size / max(width, height)
        new_size = (int(width * ratio), int(height * ratio))
        pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Convert to base64
    buffer = io.BytesIO()
    pil_image.save(buffer, format='JPEG', quality=85)
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return img_base64

# def playback_speed_agent(frames: List[str]) -> Dict[str, Any]:
    """
    Agent 1: Analyze if video needs slower playback for babies.
    """
    system_prompt = """You are a child development expert specializing in infant visual processing and sensory development. 
    Analyze the provided video frames to determine if the playback speed should be reduced for babies to prevent sensory overload.

    Consider:
    - Fast movements, quick cuts, or rapid scene changes
    - Visual complexity and information density
    - Motion patterns that might overwhelm developing visual systems
    - Age-appropriate pacing for infant attention spans

    Respond in JSON format:
    {
        "needs_slower_playback": boolean,
        "recommended_factor": float (e.g., 0.5 for half speed, 0.75 for 3/4 speed),
        "reasoning": "detailed explanation"
    }
    
    Return parsable json only.
    """

    messages = [
        {
            "role": "user", 
            "content": [
                {"type": "input_text", "text": "Analyze these video frames for appropriate playback speed for babies:"}
            ]
        }
    ]
    
    # Add frames to message
    for i, frame_b64 in enumerate(frames):
        messages[0]["content"].append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{frame_b64}"
        })
    
    response = client.responses.create(
        # model="gpt-4o",  # Using GPT-4 Vision as GPT-5 isn't available yet
        model="gpt-4.1",  # Using GPT-4 Vision as GPT-5 isn't available yet
        instructions=system_prompt,
        input=messages,
        max_output_tokens=500,
        temperature=0.3
    )

    result = json.loads(response.output[0].content[0].text)
    return result

# def color_contrast_agent(frames: List[str]) -> Dict[str, Any]:
    """
    Agent 2: Analyze if colors/contrast should be reduced for babies.
    """
    system_prompt = """You are a pediatric vision specialist and child development expert.
    Analyze the provided video frames to determine if the color contrast should be reduced for babies to prevent sensory overload.

    Consider:
    - High contrast elements that might be overwhelming
    - Bright, saturated colors that could overstimulate
    - Rapid color changes or flashing effects
    - Age-appropriate visual stimulation levels for infants
    - Developmental readiness for various color intensities

    Respond in JSON format:
    {
        "needs_reduced_contrast": boolean,
        "reasoning": "detailed explanation of why contrast should/shouldn't be reduced",
        "specific_concerns": ["list", "of", "specific", "visual", "elements", "of", "concern"]
    }
    
    Return parsable json only.
    """

    messages = [
        {
            "role": "user", 
            "content": [
                {"type": "input_text", "text": "Analyze these video frames for appropriate color contrast levels for babies:"}
            ]
        }
    ]
    
    # Add frames to message
    for i, frame_b64 in enumerate(frames):
        messages[0]["content"].append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{frame_b64}"
        })
    
    response = client.responses.create(
        # model="gpt-4o",  # Using GPT-4 Vision as GPT-5 isn't available yet
        model="gpt-4.1",
        instructions=system_prompt,
        input=messages,
        max_output_tokens=500,
        temperature=0.3
    )
    
    result = json.loads(response.output[0].content[0].text)
    return result

# def content_safety_agent(frames: List[str], audio_path: str = None) -> Dict[str, Any]:
    """
    Agent 3: Analyze for explicit or inappropriate content for babies.
    """
    system_prompt = """You are a child safety expert specializing in age-appropriate content for infants and toddlers.
    Analyze the provided video frames (and audio if available) for any explicit or inappropriate content that babies should not be exposed to.

    Consider:
    - Violence, aggression, or frightening imagery
    - Adult themes or inappropriate behavior
    - Scary or disturbing visuals
    - Content that might cause distress or fear in young children
    - Age-inappropriate themes or concepts
    - Any potentially harmful or unsuitable material for infant development

    Respond in JSON format:
    {
        "contains_inappropriate_content": boolean,
        "safety_message": "detailed explanation of any concerns or confirmation of safety",
        "content_issues": ["list", "of", "specific", "issues", "found"],
        "recommended_age": "minimum recommended age if content is questionable"
    }
    
    Return parsable json only.
    """

    messages = [
        {
            "role": "user", 
            "content": [
                {"type": "input_text", "text": "Analyze these video frames for content safety for babies:"}
            ]
        }
    ]
    
    # Add frames to message
    for i, frame_b64 in enumerate(frames):
        messages[0]["content"].append({
            "type": "input_image",
            "image_url": f"data:image/jpeg;base64,{frame_b64}"
        })
    
    # Add audio analysis note if audio is available
    # if audio_path and os.path.exists(audio_path):
    #     messages[1]["content"].append({
    #         "type": "text", 
    #         "text": "Note: This video also contains audio. Please consider that audio content should also be evaluated for appropriateness, though audio analysis is not provided here."
    #     })
    
    response = client.responses.create(
        # model="gpt-4o",  # Using GPT-4 Vision as GPT-5 isn't available yet
        model="gpt-4.1",  # Using GPT-4 Vision as GPT-5 isn't available yet
        instructions=system_prompt,
        input=messages,
        max_output_tokens=500,
        temperature=0.2
    )
    
    result = json.loads(response.output[0].content[0].text)
    return result

def process_video(video_path: str) -> Dict[str, Any]:
    """
    Main function to process video and analyze it for baby-appropriate content.
    
    Args:
        video_path (str): Path to the video file
        
    Returns:
        Dict containing analysis results from all three agents
    """
    try:
        # Validate input
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        print("Extracting smart frames from video...")
        frames = extract_smart_frames(video_path, max_frames=8)
        
        print("Encoding frames for AI analysis...")
        encoded_frames = [encode_frame_to_base64(frame) for frame in frames]
        
        print("Extracting audio segment...")
        audio_path = extract_audio_segment(video_path)
        
        print("Running AI analysis agents...")
        
        # # Run all three agents in parallel (conceptually)
        # playback_analysis = playback_speed_agent(encoded_frames)
        # contrast_analysis = color_contrast_agent(encoded_frames)
        # safety_analysis = content_safety_agent(encoded_frames, audio_path)
        
        # Clean up temporary audio file
        # if audio_path and os.path.exists(audio_path):
        #     os.unlink(audio_path)
        
        # Compile results
        # results = {
        #     "video_path": video_path,
        #     "analysis_timestamp": "2025-09-27",  # You could use datetime.now()
        #     "frames_analyzed": len(frames),
        #     "playback_speed_analysis": playback_analysis,
        #     "color_contrast_analysis": contrast_analysis,
        #     "content_safety_analysis": safety_analysis,
        #     "overall_recommendation": {
        #         "safe_for_babies": not safety_analysis.get("contains_inappropriate_content", True),
        #         "requires_modifications": (
        #             playback_analysis.get("needs_slower_playback", False) or 
        #             contrast_analysis.get("needs_reduced_contrast", False)
        #         ),
        #         "summary": "Video analysis complete. Check individual agent results for detailed recommendations."
        #     }
        # }

        
        # results = {
        #     "video_path": video_path,
        #     "analysis_timestamp": "2025-09-27",  # You could use datetime.now()
        #     "frames_analyzed": len(frames),
        #     "playback_speed_analysis": playback_analysis,
        #     "color_contrast_analysis": contrast_analysis,
        #     "content_safety_analysis": safety_analysis,
        #     "overall_recommendation": {
        #         "safe_for_babies": not safety_analysis.get("contains_inappropriate_content", True),
        #         "requires_modifications": (
        #             playback_analysis.get("needs_slower_playback", False) or 
        #             contrast_analysis.get("needs_reduced_contrast", False)
        #         ),
        #         "summary": "Video analysis complete. Check individual agent results for detailed recommendations."
        #     }
        # }
        
        # return results
        return get_response_adk(encoded_frames, audio_path)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": True,
            "error_message": str(e),
            "video_path": video_path,
            "analysis_timestamp": "2025-09-27"
        }
