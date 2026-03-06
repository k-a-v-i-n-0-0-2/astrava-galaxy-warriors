"""
Setup script for Gemini API integration.
Run this first to configure your API key.
"""

import os
import sys

def setup_gemini():
    """Helper to set up Gemini API key."""
    
    # Make sure we're in the right directory
    current_dir = os.getcwd()
    print(f"\n📁 Current directory: {current_dir}")
    
    # Check if we're in the wrong place (data/src)
    if current_dir.endswith('data\\src') or current_dir.endswith('data/src'):
        print("⚠️  You're in the wrong directory!")
        print("   Please run this from the project root:")
        print("   cd C:\\Users\\ramgo\\OneDrive\\Desktop\\code4change\\coordinated_amplification_detector")
        return
    
    print("\n" + "="*60)
    print("🤖 GEMINI API SETUP")
    print("="*60)
    
    print("\n1. Get your API key from:")
    print("   https://makersuite.google.com/app/apikey")
    print("\n2. Enter your API key below:")
    
    api_key = input("\n🔑 API Key: ").strip()
    
    if not api_key:
        print("\n❌ No API key provided")
        return
    
    # Create .env file in the current directory
    env_content = f"""# Gemini API Configuration
GEMINI_API_KEY={api_key}
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.3
"""
    
    env_path = os.path.join(current_dir, '.env')
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ .env file created successfully at: {env_path}")
    
    # Test the key
    print("\n🔍 Testing API key...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Try different model names
        models_to_try = ['gemini-1.5-pro', 'gemini-pro', 'gemini-1.0-pro']
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'API key works!' in one word")
                print(f"✅ Success with model: {model_name}")
                print(f"   Response: {response.text}")
                
                # Update .env with working model
                with open(env_path, 'w') as f:
                    f.write(f"""# Gemini API Configuration
GEMINI_API_KEY={api_key}
GEMINI_MODEL={model_name}
GEMINI_TEMPERATURE=0.3
""")
                print(f"✅ Updated .env with working model: {model_name}")
                break
            except Exception as e:
                print(f"   ⚠️  Model {model_name} failed: {str(e)[:50]}...")
                continue
        else:
            print("❌ Could not find a working model. Your API key might be invalid.")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        print("\n⚠️  Please check your API key and try again")

if __name__ == "__main__":
    setup_gemini()