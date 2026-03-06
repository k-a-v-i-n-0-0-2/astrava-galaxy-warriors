"""Verify no false positives on human videos after ML fix."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['PYTHONIOENCODING'] = 'utf-8'
from src.video_analyzer import VideoAIAnalyzer
from src.ml_classifier import get_classifier

pub = r'c:\Users\profe\Downloads\deepfake-detection\code4change4\ASTRAVA\ASTRAVA\public'
analyzer = VideoAIAnalyzer()
clf = get_classifier()

# Test first two videos (known human) plus video5 (known AI)
test_files = ['test_video.mp4', 'test_video5.mp4']
for f in test_files:
    path = os.path.join(pub, f)
    if not os.path.exists(path):
        print(f"SKIP: {f} not found")
        continue
    r = analyzer.analyze_video(path)
    fv = r['feature_vector']
    ml = clf.predict(fv, forensic_score=r['ai_probability'])
    verdict = "AI-GENERATED" if ml['ai_probability'] >= 50 else "LIKELY HUMAN"
    print(f"\n{f}: [{round(ml['ai_probability'],1)}%] -> {verdict}")
    print(f"  FV: {[round(x,1) for x in fv]}")
