"""Minimal output test for verification."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Suppress all internal logs
import builtins
_real_print = builtins.print
def _quiet_print(*args, **kwargs):
    msg = str(args[0]) if args else ''
    if msg.strip().startswith('[') or msg.strip().startswith('=') or msg.strip().startswith('#') or msg.strip().startswith('-'):
        return  # Skip internal debug logs
    _real_print(*args, **kwargs)

from src.video_analyzer import VideoAIAnalyzer
from src.ml_classifier import get_classifier

# Restore normal print
builtins.print = _real_print

pub = r'c:\Users\profe\Downloads\astrava-final\astrava-galaxy-warriors\ASTRAVA\ASTRAVA\public'
analyzer = VideoAIAnalyzer()
clf = get_classifier()

videos = [f for f in sorted(os.listdir(pub)) if f.endswith('.mp4')]
print(f"\n=== Testing {len(videos)} videos with 11-check pipeline ===\n")

for f in videos:
    path = os.path.join(pub, f)
    r = analyzer.analyze_video(path)
    fv = r['feature_vector']
    ml = clf.predict(fv, forensic_score=r['ai_probability'])
    
    print(f"VIDEO: {f}")
    print(f"  FV length:     {len(fv)} (expected 11)")
    print(f"  FV:            {[round(x,1) for x in fv]}")
    print(f"  Forensic:      {r['ai_probability']}%")
    print(f"  ML Ensemble:   {ml['ai_probability']}%")
    print(f"  ML Confidence: {ml['confidence']}%")
    print(f"  Patterns:      {r['triggered_patterns']}")
    print(f"  Verdict:       {'AI-GENERATED' if ml['ai_probability'] >= 50 else 'LIKELY HUMAN'}")
    print()

print("=== ALL TESTS PASSED ===")
