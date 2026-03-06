import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.video_analyzer import VideoAIAnalyzer

analyzer = VideoAIAnalyzer()
video = r'c:\Users\profe\Downloads\deepfake-detection\code4change4\ASTRAVA\ASTRAVA\public\test_video.mp4'
result = analyzer.analyze_video(video)

print("\n=== SIGNAL SCORES (REAL VIDEO) ===")
for k, v in result['signals'].items():
    print(f"  {k}: {v}")
print(f"\nAI Probability: {result['ai_probability']}")
print(f"Confidence: {result['confidence']}")
print(f"Feature Vector: {result['feature_vector']}")
print(f"Risk: {result['deepfake_risk']}")
print(f"Patterns: {result['triggered_patterns']}")
