import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

MAX_VIDEO_DURATION = 3

PHASES = {
    "Hook": {"start": 0, "end": 5},
    "Context": {"start": 5, "end": 15},
    "Conflict": {"start": 15, "end": 30},
    "Pivot": {"start": 30, "end": 45},
    "Climax": {"start": 45, "end": 55},
    "Reveal": {"start": 55, "end": 120}
}

AI_STYLE_KEYWORDS = "Cinematic lighting, hyper-realistic, 8k, moody atmosphere, volumetric fog, high-contrast, professional color grade, business-documentary style, no text, no cartoons."

NEGATIVE_KEYWORDS = [
    "talking head",
    "presenter",
    "spokesperson",
    "interview",
    "news anchor",
    "vlogger",
    "webcam",
    "direct to camera"
]

CORPORATE_NEGATIVE = [
    "office people",
    "corporate meeting",
    "handshake business",
    "happy office",
    "team cheering",
    "high five office"
]

KEN_BURNS_INSTRUCTION = "Instruction: Apply 110% Center-Zoom Ken Burns Effect."

SFX_MAPPINGS = {
    "money": "Money sound, cash register",
    "success": "Success chime, victory sound",
    "failure": "Dramatic bass drop, tension sound",
    "reveal": "Swoosh, reveal sound",
    "transition": "Whoosh, transition swoosh",
    "impact": "Bass impact, thud",
    "growth": "Rising tone, ascending sound",
    "decline": "Descending tone, falling sound"
}
