import datetime
import json
from zoneinfo import ZoneInfo
from google.adk.agents import Agent, ParallelAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm


playback_speed_agent = Agent(
    model=LiteLlm(model="openai/gpt-4.1-mini"),
    name="playback_speed_agent",
    output_key="playback_speed_analysis",
    description=(
        "Agent that can adjust the playback speed of videos using the frames provided."
    ),
    instruction="""
      You are a child development expert specializing in infant visual processing and sensory development. 
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
    """,
)


color_contrast_agent = Agent(
    model=LiteLlm(model="openai/gpt-4.1"),
    name="color_contrast_agent",
    output_key="color_contrast_analysis",
    description=(
        "Agent that can adjust the color contrast of videos using the frames provided."
    ),
    instruction="""
You are a pediatric vision specialist and child development expert. Analyze the provided video frames to determine if the color contrast should be reduced for babies to prevent sensory overload.

    Consider:
    - High contrast elements that might be overwhelming
    - Bright, saturated colors that could overstimulate
    - Rapid color changes or flashing effects
    - Age-appropriate visual stimulation levels for infants
    - Developmental readiness for various color intensities

    Respond in JSON format:
    {
        "needs_reduced_contrast": boolean
    }
    
    Return parsable json only.
    """,
)

content_appropriation_agent = Agent(
    model=LiteLlm(model="openai/gpt-4.1-mini"),
    name="content_appropriation_agent",
    output_key="content_safety_analysis",
    description=(
        "Agent that can adjust the content appropriateness of videos using the frames and audio file provided."
    ),
    instruction="""
You are a child safety expert specializing in age-appropriate content for infants and toddlers.
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
    """,
)


p_agent = ParallelAgent(
   name="InfoGatherer",
    sub_agents=[
        playback_speed_agent,
        color_contrast_agent,
        content_appropriation_agent
    ],
    description="Runs multiple agents in parallel to gather information."

)

merger = Agent(
     name="BabyShieldCoordinator",
     model="gemini-2.0-flash",
     description=(
        "Root agent that coordinates analysis of video frames across three specialized agents in parallel."
    ),
    instruction=(
        """You are the BabyShield coordinator agent. You receive video frames and coordinate analysis across three specialized sub-agents that run in parallel:
        
        1. Playback Speed Agent - analyzes if video needs slower playback for babies
        2. Color Contrast Agent - analyzes if video needs reduced contrast
        3. Content Safety Agent - analyzes content appropriateness for babies
        
        Compile the results from all three agents into this JSON structure:
        {
            "video_path": "path/to/video",
            "playback_speed_analysis": {playback_speed_analysis},
            "color_contrast_analysis": {color_contrast_analysis}, 
            "content_safety_analysis": {content_safety_analysis},
            "overall_recommendation": {
                "safe_for_babies": boolean (true if no inappropriate content),
                "requires_modifications": boolean (true if playback or contrast changes needed),
                "summary": "Video analysis complete. Check individual agent results for detailed recommendations."
            }
        }
        
        Return parsable JSON only.
        """
    ),
)


root_agent = SequentialAgent(
     name="ResearchAndSynthesisPipeline",
     # Run parallel research first, then merge
     sub_agents=[p_agent, merger],
     description="Coordinates parallel research and synthesizes the results."
 )