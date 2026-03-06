"""
Simple test for Gemini API connection.
UPDATED with correct model names from your list.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini():
    """Test Gemini API connection with available models."""
    
    print("\n" + "="*60)
    print("🤖 GEMINI API TEST")
    print("="*60)
    
    # Check for API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("\n❌ No API key found!")
        print("\nTo fix:")
        print("1. Create a file called '.env' in this folder")
        print("2. Add this line: GEMINI_API_KEY=your_key_here")
        print("3. Get your key from: https://makersuite.google.com/app/apikey")
        return
    
    print(f"\n✓ API key found: {api_key[:8]}...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # List available models
        print("\n📋 Available models from API:")
        models = genai.list_models()
        working_models = []
        
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"   • {model.name}")
                working_models.append(model.name)
        
        # Test models from your list
        print("\n🔄 Testing recommended models...")
        
        models_to_test = [
            'gemini-2.5-flash',
            'gemini-2.5-pro',
            'gemini-2.0-flash',
            'gemini-flash-latest',
            'gemini-pro-latest'
        ]
        
        working_model = None
        
        for model_name in models_to_test:
            try:
                print(f"\n   Testing {model_name}...")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'OK' in one word")
                print(f"   ✅ SUCCESS: {response.text}")
                working_model = model_name
                break
                
            except Exception as e:
                print(f"   ❌ Failed: {str(e)[:50]}")
        
        if working_model:
            print(f"\n✅ Working model found: {working_model}")
            print("\nAdd this to your .env file:")
            print(f"GEMINI_MODEL={working_model}")
            
            # Update .env automatically
            update_env(working_model)
        else:
            print("\n❌ No working model found from test list")
            print("\nTry one of these from your available models:")
            for model in working_models[:5]:
                print(f"   • {model}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

def update_env(model_name):
    """Update .env file with working model."""
    try:
        env_path = '.env'
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                content = f.read()
            
            if 'GEMINI_MODEL=' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('GEMINI_MODEL='):
                        lines[i] = f'GEMINI_MODEL={model_name}'
                new_content = '\n'.join(lines)
            else:
                new_content = content + f'\nGEMINI_MODEL={model_name}\n'
            
            with open(env_path, 'w') as f:
                f.write(new_content)
            print(f"✅ Updated .env with model: {model_name}")
    except:
        pass

if __name__ == "__main__":
    test_gemini()