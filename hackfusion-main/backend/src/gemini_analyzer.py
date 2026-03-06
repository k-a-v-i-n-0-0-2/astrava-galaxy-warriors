"""
Gemini Vision Analyzer — OPTIONAL bonus for AI detection.

This is NOT required for the system to work. The ML classifier handles
detection independently. Gemini is a bonus that adds +/-15% adjustment.
If the API key is leaked/revoked/missing, the system continues at full accuracy.
"""

import os
import time
import json
import tempfile
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def _log(msg: str):
    print(msg, flush=True)

# Global state
_WORKING_MODEL_NAME = None
_IS_GLOBALLY_UNAVAILABLE = False
_INIT_ATTEMPTED = False

# Try to import — if missing, Gemini is just disabled
try:
    import google.generativeai as genai
    _HAS_GENAI = True
except ImportError:
    _HAS_GENAI = False
    _log("  [GEMINI] google.generativeai not installed - Gemini disabled (ML classifier handles detection)")


class GeminiPostAnalyzer:
    """
    Optional Gemini Vision analysis. Gracefully disabled if API key is
    leaked, revoked, missing, or the package isn't installed.
    """

    def __init__(self, api_key: Optional[str] = None):
        global _WORKING_MODEL_NAME, _IS_GLOBALLY_UNAVAILABLE, _INIT_ATTEMPTED

        self.is_available = False
        self.quota_exceeded = False
        self.model = None
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')

        if not _HAS_GENAI or _IS_GLOBALLY_UNAVAILABLE:
            return

        if not self.api_key or self.api_key == 'YOUR_NEW_API_KEY_HERE':
            return

        try:
            genai.configure(api_key=self.api_key)

            if _WORKING_MODEL_NAME:
                self.model = genai.GenerativeModel(_WORKING_MODEL_NAME)
                self.is_available = True
                return

            if _INIT_ATTEMPTED:
                return  # Don't retry failed init

            _INIT_ATTEMPTED = True
            models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro-vision']

            preferred = os.getenv('GEMINI_MODEL')
            if preferred and preferred not in models:
                models.insert(0, preferred)

            masked = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
            _log(f"      [GEMINI] Initializing (key: {masked})")

            for name in models:
                try:
                    self.model = genai.GenerativeModel(name)
                    self.model.generate_content("test", generation_config={"max_output_tokens": 1})
                    self.is_available = True
                    _WORKING_MODEL_NAME = name
                    _log(f"      [GEMINI] Ready with {name}")
                    return
                except Exception as e:
                    err = str(e).lower()
                    if 'leaked' in err or 'revoked' in err:
                        _log(f"      [GEMINI] API key revoked - disabling Gemini (ML classifier handles detection)")
                        _IS_GLOBALLY_UNAVAILABLE = True
                        return
                    if '429' in str(e) or 'quota' in err:
                        self.quota_exceeded = True
                        _log(f"      [GEMINI] Quota exceeded for {name}")
                    elif '403' in str(e) or 'permission' in err:
                        _log(f"      [GEMINI] Permission denied - disabling")
                        _IS_GLOBALLY_UNAVAILABLE = True
                        return
                    else:
                        _log(f"      [GEMINI] {name} failed: {str(e)[:80]}")

        except Exception as e:
            _log(f"      [GEMINI] Init failed: {e}")

    def analyze_media_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze media with Gemini Vision. Returns ai_score 0-1."""
        if not self.is_available or not self.model:
            return {"ai_score": None, "details": "Gemini unavailable"}

        temp_file = None
        try:
            if file_path.startswith('http'):
                import requests
                resp = requests.get(file_path, stream=True, timeout=30)
                ext = os.path.splitext(file_path)[1] or '.mp4'
                with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                    for chunk in resp.iter_content(8192):
                        tmp.write(chunk)
                    temp_file = tmp.name
                file_path = temp_file

            media_file = genai.upload_file(path=file_path)

            if file_path.lower().endswith(('.mp4', '.mov', '.avi', '.webm')):
                _log("      [GEMINI] Processing video...")
                for _ in range(30):  # Max 60s wait
                    if media_file.state.name != "PROCESSING":
                        break
                    time.sleep(2)
                    media_file = genai.get_file(media_file.name)

                if media_file.state.name == "FAILED":
                    return {"ai_score": None, "details": "Gemini video processing failed"}

            prompt = """Analyze this media as a forensic AI-detection expert.
Is this AI-generated (Deepfake/GAN/Diffusion/Sora) or real camera footage?
Return ONLY JSON: {"ai_score": float 0.0-1.0, "confidence_level": "High"/"Moderate"/"Low", "details": "explanation", "signals": {"uncanny_valley": float, "physics_glitches": float, "texture_artifacts": float, "temporal_noise": float}}"""

            response = self.model.generate_content([media_file, prompt])
            text = response.text

            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                result = json.loads(match.group())
                _log(f"      [GEMINI] Result: {result.get('ai_score', 0.5)*100:.1f}% AI")
                return result

            return {"ai_score": None, "details": "Could not parse Gemini response"}

        except Exception as e:
            err = str(e).lower()
            if 'leaked' in err or 'revoked' in err:
                global _IS_GLOBALLY_UNAVAILABLE
                _IS_GLOBALLY_UNAVAILABLE = True
                _log("      [GEMINI] Key revoked - disabling permanently")
            else:
                _log(f"      [GEMINI] Error: {str(e)[:100]}")
            return {"ai_score": None, "details": str(e)}
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass