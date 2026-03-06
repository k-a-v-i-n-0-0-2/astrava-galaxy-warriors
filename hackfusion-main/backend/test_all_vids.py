"""Test all videos with updated ML classifier."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['PYTHONIOENCODING'] = 'utf-8'
from src.video_analyzer import VideoAIAnalyzer
from src.ml_classifier import get_classifier

pub = r'c:\Users\profe\Downloads\deepfake-detection\code4change4\ASTRAVA\ASTRAVA\public'
analyzer = VideoAIAnalyzer()
clf = get_classifier()

for f in sorted(os.listdir(pub)):
    if f.endswith('.mp4'):
        path = os.path.join(pub, f)
        print(f"\n{'='*50}")
        print(f"VIDEO: {f} ({os.path.getsize(path)//1024}KB)")
        print(f"{'='*50}")
        r = analyzer.analyze_video(path)
        fv = r['feature_vector']
        forensic_score = r['ai_probability']
        ml = clf.predict(fv, forensic_score=forensic_score)
        print(f"  Forensics score:  {forensic_score}%")
        print(f"  ML RF:            {ml['rf_probability']}%")
        print(f"  ML Ensemble:      {ml['ai_probability']}%")
        print(f"  Feature vector:   {[round(x,1) for x in fv]}")
        print(f"  Patterns:         {r['triggered_patterns']}")
        verdict = "AI-GENERATED" if ml['ai_probability'] >= 50 else "LIKELY HUMAN"
        print(f"  VERDICT:          {verdict}")
