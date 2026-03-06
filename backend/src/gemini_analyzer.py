"""
Gemini API integration with quota handling.
"""

import os
import time
import google.generativeai as genai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Global cache to prevent re-testing models on every request
_WORKING_MODEL_NAME = None
_IS_GLOBALLY_UNAVAILABLE = False
_IS_QUOTA_EXCEEDED = False

class GeminiPostAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        global _WORKING_MODEL_NAME, _IS_GLOBALLY_UNAVAILABLE, _IS_QUOTA_EXCEEDED
        
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        self.is_available = False
        self.quota_exceeded = _IS_QUOTA_EXCEEDED
        
        if _IS_GLOBALLY_UNAVAILABLE:
            return
            
        if self.api_key and not self.quota_exceeded:
            try:
                genai.configure(api_key=self.api_key)
                
                if _WORKING_MODEL_NAME:
                    self.model = genai.GenerativeModel(_WORKING_MODEL_NAME)
                    self.is_available = True
                    return

                # Try models in order of preference
                preferred_model = os.getenv('GEMINI_MODEL')
                models_to_try = [
                    'gemini-1.5-flash',
                    'gemini-1.5-pro',
                    'gemini-2.5-flash',
                    'gemini-2.0-flash',
                    'gemini-pro',
                    'gemini-flash-latest',
                ]
                
                if preferred_model and preferred_model not in models_to_try:
                    models_to_try.insert(0, preferred_model)
                
                print("\n🔍 Initializing Gemini...")
                
                for model_name in models_to_try:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        # Very quick test
                        response = self.model.generate_content("OK", generation_config={"max_output_tokens": 1})
                        self.is_available = True
                        _WORKING_MODEL_NAME = model_name
                        print(f"✅ Gemini ready with {model_name}")
                        break
                    except Exception as e:
                        if '429' in str(e) or 'Quota' in str(e):
                            print(f"⚠️ Quota exceeded for {model_name}")
                        elif '403' in str(e) or 'PermissionDenied' in str(e):
                            print(f"⚠️ API Key Blocked/Leaked. Stopping Gemini initialization.")
                            _IS_GLOBALLY_UNAVAILABLE = True
                            break
                        else:
                            # Print a shorter error message to avoid console flood
                            err_msg = str(e).split('\n')[0]
                            print(f"⚠️ Gemini init failed for {model_name}: {err_msg}")
                        continue
                
                if _IS_GLOBALLY_UNAVAILABLE:
                    return

                # If loop finishes and no model is available, mark quota exceeded if that was the reason
                if not self.is_available:
                    self.quota_exceeded = True
                    _IS_QUOTA_EXCEEDED = True
                    _IS_GLOBALLY_UNAVAILABLE = True

            except Exception as e:
                print(f"⚠️ Gemini init failed: {e}")
                _IS_GLOBALLY_UNAVAILABLE = True
    
    def generate_post_insights(self, post_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate insights with quota handling."""
        
        if self.quota_exceeded:
            return {
                'summary': '⚠️ API quota exceeded. Try again later.',
                'risk_factors': '• Rate limit reached\n• Wait 60 seconds',
                'recommendation': 'Use without Gemini for now'
            }
        
        if not self.is_available:
            return {
                'summary': 'Gemini unavailable',
                'risk_factors': '',
                'recommendation': 'Continue with basic analysis'
            }
        
        try:
            # Add small delay to avoid quota issues
            time.sleep(1)
            
            prompt = f"""
            Briefly analyze this post (1 sentence each):
            
            Post: {post_data.get('post_id', 'Unknown')}
            Confidence: {post_data.get('confidence', 0)}%
            Patterns: {len(post_data.get('triggered_signals', []))} detected
            
            SUMMARY:
            RISK:
            ACTION:
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response
            lines = response.text.split('\n')
            result = {
                'summary': '',
                'risk_factors': '',
                'recommendation': ''
            }
            
            for line in lines:
                if line.startswith('SUMMARY:'):
                    result['summary'] = line[8:].strip()
                elif line.startswith('RISK:'):
                    result['risk_factors'] = line[5:].strip()
                elif line.startswith('ACTION:'):
                    result['recommendation'] = line[7:].strip()
            
            return result
            
        except Exception as e:
            if '429' in str(e):
                self.quota_exceeded = True
                return {
                    'summary': 'Quota exceeded',
                    'risk_factors': 'Rate limit reached',
                    'recommendation': 'Try again in 60 seconds'
                }
            return {
                'summary': f'Error: {str(e)[:50]}',
                'risk_factors': '',
                'recommendation': ''
            }