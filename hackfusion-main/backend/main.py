#!/usr/bin/env python3
"""
Instagram AI Confidence Labeler with Gemini API
YOU provide the post data, the system returns confidence labels + Gemini insights
"""

import os
import sys
import pandas as pd
from datetime import datetime
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.loader import InteractionDataLoader
from src.detector import InstagramAIConfidenceLabeler


def analyze_post_from_csv(csv_file_path, use_gemini=True):
    """Analyze posts from a CSV file with optional Gemini insights."""
    
    print(f"\n📊 Analyzing data from: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        print(f"❌ ERROR: File not found: {csv_file_path}")
        return
    
    # Load and analyze the data
    loader = InteractionDataLoader(data_source=csv_file_path)
    
    try:
        df = loader.load_data()
        print(f"✓ Loaded {len(df)} interactions")
        print(f"✓ Found {df['post_id'].nunique()} posts")
        
        # Get Gemini API key from environment
        gemini_key = os.getenv('GEMINI_API_KEY')
        
        # Initialize labeler with Gemini
        labeler = InstagramAIConfidenceLabeler(gemini_api_key=gemini_key)
        
        if use_gemini and gemini_key:
            print("✓ Gemini API enabled for enhanced analysis")
        
        # Analyze each post
        for post_id in df['post_id'].unique():
            post_df = df[df['post_id'] == post_id]
            result = labeler.analyze_post(post_id, post_df, use_gemini=use_gemini)
            
            # Display result
            print("\n" + "="*70)
            print(f"📱 POST ANALYSIS RESULT")
            print("="*70)
            print(f"Post ID: {result['post_id']}")
            print(f"Total Interactions: {result['total_interactions']}")
            print(f"Unique Users: {result['unique_users']}")
            print(f"Abnormal Signals: {result['abnormal_signal_count']}/6")
            print(f"Confidence Score: {result['confidence']}%")
            print("-"*70)
            
            if result['label']:
                print(f"\n🔍 {result['label']}")
                print(f"   ↳ {result['tap_detail']}")
            else:
                print(f"\n✓ No label needed - appears organic")
            
            if result['triggered_signals']:
                print("\n⚠️  Detected Patterns:")
                for signal in result['triggered_signals']:
                    print(f"   • {signal}")
            
            # Show Gemini insights if available
            if 'gemini_insights' in result:
                print("\n🤖 GEMINI INSIGHTS:")
                insights = result['gemini_insights']
                if insights.get('summary'):
                    print(f"   📝 {insights['summary']}")
                if insights.get('risk_factors'):
                    print(f"\n   ⚠️  Risk Factors:\n{insights['risk_factors']}")
                if insights.get('recommendation'):
                    print(f"\n   💡 {insights['recommendation']}")
            
            if 'moderation_note' in result:
                print(f"\n   📋 Moderation Note: {result['moderation_note']}")
            
            print("="*70)
            
    except Exception as e:
        print(f"❌ Error analyzing post: {e}")


def interactive_mode():
    """Interactive mode with Gemini support."""
    
    print("\n" + "="*70)
    print("📱 INSTAGRAM AI CONFIDENCE LABELER WITH GEMINI")
    print("="*70)
    
    # Check for Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        print("✓ Gemini API configured")
        use_gemini = input("\nUse Gemini for enhanced insights? (y/n): ").lower() == 'y'
    else:
        print("⚠️  No Gemini API key found (set GEMINI_API_KEY in .env file)")
        use_gemini = False
    
    print("\n📝 Enter your post data manually")
    print("-"*50)
    
    # Get post ID
    post_id = input("\n📌 Enter Post ID: ").strip()
    
    # Get interactions
    print("\n📝 Enter interactions (format: user_id,timestamp,action_type)")
    print("   Example: user123,2025-02-13 14:30:00,like")
    print("   Type 'done' when finished")
    print("-"*50)
    
    interactions = []
    while True:
        line = input("➡️  ").strip()
        if line.lower() == 'done':
            break
        
        try:
            parts = line.split(',')
            if len(parts) == 3:
                user_id, timestamp, action = parts
                interactions.append({
                    'post_id': post_id,
                    'user_id': user_id.strip(),
                    'timestamp': timestamp.strip(),
                    'action_type': action.strip()
                })
                print(f"   ✓ Added: {user_id} - {action}")
            else:
                print("   ⚠️  Format: user_id,timestamp,action_type")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
    
    if interactions:
        # Convert to DataFrame
        df = pd.DataFrame(interactions)
        
        # Initialize labeler
        labeler = InstagramAIConfidenceLabeler(gemini_api_key=gemini_key if use_gemini else None)
        
        # Analyze
        result = labeler.analyze_post(post_id, df, use_gemini=use_gemini)
        
        # Display result
        print("\n" + "="*70)
        print("📱 ANALYSIS RESULT")
        print("="*70)
        print(f"Post ID: {post_id}")
        print(f"Total Interactions: {result['total_interactions']}")
        print(f"Unique Users: {result['unique_users']}")
        print(f"Abnormal Signals: {result['abnormal_signal_count']}/6")
        print(f"Confidence Score: {result['confidence']}%")
        print("-"*70)
        
        if result['label']:
            print(f"\n🔍 {result['label']}")
            print(f"   ↳ {result['tap_detail']}")
        else:
            print(f"\n✓ No label needed")
        
        if result['triggered_signals']:
            print("\n⚠️  Detected Patterns:")
            for signal in result['triggered_signals']:
                print(f"   • {signal}")
        
        # Show Gemini insights
        if 'gemini_insights' in result:
            print("\n🤖 GEMINI INSIGHTS:")
            insights = result['gemini_insights']
            if insights.get('summary'):
                print(f"   📝 {insights['summary']}")
            if insights.get('risk_factors'):
                print(f"\n   ⚠️  Risk Factors:\n{insights['risk_factors']}")
            if insights.get('recommendation'):
                print(f"\n   💡 {insights['recommendation']}")
        
        print("="*70)
    else:
        print("\n⚠️  No interactions entered")


def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(description='Instagram AI Confidence Labeler with Gemini')
    parser.add_argument('--file', '-f', help='CSV file containing post interactions')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--no-gemini', action='store_true', help='Disable Gemini API')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("📱 INSTAGRAM AI CONFIDENCE LABELER WITH GEMINI")
    print("="*70)
    
    if args.interactive:
        interactive_mode()
    elif args.file:
        analyze_post_from_csv(args.file, use_gemini=not args.no_gemini)
    else:
        print("\nUsage:")
        print("  python main.py --file <your_data.csv>")
        print("  python main.py --interactive")
        print("  python main.py --file data.csv --no-gemini")
        print("\nCSV Format Required:")
        print("  post_id,user_id,timestamp,action_type")
        print("  video123,user456,2025-02-13 14:30:00,like")
        print("\nGemini Setup:")
        print("  1. Get API key from: https://makersuite.google.com/app/apikey")
        print("  2. Create .env file with: GEMINI_API_KEY=your_key_here")
        print("="*70)


if __name__ == "__main__":
    main()