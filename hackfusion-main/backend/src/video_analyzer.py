"""
Video Analysis Module — Full Forensic Pipeline for AI Content Detection.

8 forensic checks using OpenCV, numpy, scipy, scikit-image:
  1. Facial consistency (SSIM across frames)
  2. Expression symmetry (face left/right mirror analysis)
  3. Lip-sync coherence (mouth region motion patterns)
  4. GAN noise fingerprint (FFT spectral analysis)
  5. Texture regularity (LBP-based texture analysis)
  6. Color histogram anomaly (HSV distribution analysis)
  7. Temporal coherence (optical flow consistency)
  8. Edge/compression artifacts (Laplacian + Canny analysis)
"""

import cv2
import numpy as np
import os
import tempfile
from skimage.metrics import structural_similarity as ssim
from skimage.feature import local_binary_pattern
from typing import Dict, List, Optional
from scipy import stats, fft
from scipy.spatial import distance
import requests
import urllib.parse

try:
    import yt_dlp
except ImportError:
    yt_dlp = None


def _log(msg: str):
    print(msg, flush=True)


class VideoAIAnalyzer:
    """
    Analyzes video/image content for AI-generated artifacts using 8 forensic signals.
    All analysis is performed locally using OpenCV + numpy + scipy + scikit-image.
    """

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )

    # ── Download / Extract ─────────────────────────────────────────────────

    def _is_url(self, path: str) -> bool:
        try:
            result = urllib.parse.urlparse(path)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _download_media(self, url: str) -> Optional[str]:
        try:
            if ('youtube.com' in url or 'youtu.be' in url) and yt_dlp:
                _log("      [YT] YouTube detected, resolving with yt-dlp...")
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4][height<=720]/best',
                    'quiet': True, 'no_warnings': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    url = info['url']
                    _log("      [YT] Resolved")

            _log("      [DL] Downloading media...")
            resp = requests.get(url, stream=True, timeout=30)
            resp.raise_for_status()
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[-1] or '.mp4'
            fd, tmp = tempfile.mkstemp(suffix=ext)
            os.close(fd)
            total = 0
            with open(tmp, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)
                    total += len(chunk)
            _log(f"      [DL] Done ({total/1024:.0f} KB)")
            return tmp
        except Exception as e:
            _log(f"      [DL] Failed: {e}")
            return None

    def extract_frames(self, video_path: str, num_frames: int = 15) -> List[np.ndarray]:
        temp_file = None
        if self._is_url(video_path):
            _log("      [IO] Remote media")
            temp_file = self._download_media(video_path)
            if not temp_file:
                return []
            video_path = temp_file

        try:
            ext = os.path.splitext(video_path)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp']:
                _log("      [IO] Image file, loading single frame")
                img = cv2.imread(video_path)
                return [img] if img is not None else []

            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                _log("      [IO] Cannot open video")
                return []

            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            dur = total / fps if fps > 0 else 0
            _log(f"      [IO] Video: {total} frames, {fps:.0f} fps, {dur:.1f}s")

            if total <= 0:
                cap.release()
                return []

            indices = np.linspace(0, total - 1, num_frames, dtype=int)
            frames = []
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
            cap.release()
            _log(f"      [IO] Extracted {len(frames)} frames")
            return frames
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass

    # ── Forensic Check 1: Facial Consistency ───────────────────────────────

    def check_facial_consistency(self, frames: List[np.ndarray]) -> float:
        """Cross-frame SSIM of detected faces. AI faces tend to wobble/morph."""
        try:
            scores = []
            for i in range(len(frames) - 1):
                g1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                g2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
                f1 = self.face_cascade.detectMultiScale(g1, 1.3, 5)
                f2 = self.face_cascade.detectMultiScale(g2, 1.3, 5)
                if len(f1) > 0 and len(f2) > 0:
                    x1, y1, w1, h1 = f1[0]
                    x2, y2, w2, h2 = f2[0]
                    face1 = cv2.resize(g1[y1:y1+h1, x1:x1+w1], (100, 100))
                    face2 = cv2.resize(g2[y2:y2+h2, x2:x2+w2], (100, 100))
                    s, _ = ssim(face1, face2, full=True)
                    scores.append(s)

            if not scores:
                return 15.0  # No faces = probably real content, low suspicion

            avg = np.mean(scores)
            std = np.std(scores)
            # Very high SSIM (>0.96) = suspiciously consistent (AI)
            # Very low SSIM (<0.55) = unstable faces (AI deepfake wobble)
            # Natural range: 0.65 - 0.94
            if avg > 0.96:
                anomaly = 70 + (avg - 0.96) * 700  # Too perfect
            elif avg < 0.55:
                anomaly = 70 + (0.55 - avg) * 200  # Too unstable
            else:
                anomaly = max(0, 40 - (avg - 0.55) * 80)  # Normal range

            # High variance in face similarity = AI glitching
            anomaly += min(25, std * 150)
            return float(min(100, max(0, anomaly)))
        except:
            return 50.0

    # ── Forensic Check 2: Expression Symmetry ──────────────────────────────

    def check_expression_symmetry(self, frames: List[np.ndarray]) -> float:
        """AI faces tend to be unnaturally symmetric. Real faces have micro-asymmetry."""
        try:
            symmetry_scores = []
            for frame in frames[:8]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                if len(faces) == 0:
                    continue

                x, y, w, h = faces[0]
                face = gray[y:y+h, x:x+w]
                mid = w // 2
                left = face[:, :mid]
                right = face[:, mid:mid*2]

                if left.shape[1] == 0 or right.shape[1] == 0:
                    continue
                if left.shape != right.shape:
                    right = cv2.resize(right, (left.shape[1], left.shape[0]))

                flipped = cv2.flip(right, 1)
                s, _ = ssim(left, flipped, full=True)

                # Jensen-Shannon divergence of histograms
                lh = cv2.calcHist([left], [0], None, [256], [0, 256]).flatten()
                rh = cv2.calcHist([flipped], [0], None, [256], [0, 256]).flatten()
                lh = lh / (lh.sum() + 1e-8)
                rh = rh / (rh.sum() + 1e-8)
                js = distance.jensenshannon(lh, rh)

                combined = 0.6 * s + 0.4 * (1 - js)
                symmetry_scores.append(combined)

            if not symmetry_scores:
                return 15.0  # No faces = probably real, low suspicion

            avg_sym = np.mean(symmetry_scores)
            # Too symmetric (> 0.94) is suspicious (AI-generated faces)
            # Natural asymmetry: 0.7 - 0.90
            if avg_sym > 0.94:
                return float(min(100, 65 + (avg_sym - 0.94) * 600))
            elif avg_sym > 0.88:
                return float(30 + (avg_sym - 0.88) * 400)
            else:
                return float(max(0, 25 - (0.85 - avg_sym) * 100))
        except:
            return 50.0

    # ── Forensic Check 3: Lip-Sync Coherence ───────────────────────────────

    def check_lip_sync(self, frames: List[np.ndarray]) -> float:
        """Check mouth region motion patterns. AI lip-sync has unnatural variance."""
        try:
            mouth_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_smile.xml'
            )
            mouth_motions = []

            for i in range(len(frames) - 1):
                g1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                g2 = cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY)

                faces1 = self.face_cascade.detectMultiScale(g1, 1.3, 5)
                if len(faces1) == 0:
                    continue

                x, y, w, h = faces1[0]
                # Lower half of face = mouth region
                mouth_y = y + int(h * 0.6)
                mouth_h = int(h * 0.4)
                mouth1 = g1[mouth_y:mouth_y+mouth_h, x:x+w]
                mouth2 = g2[mouth_y:mouth_y+mouth_h, x:x+w]

                if mouth1.size == 0 or mouth2.size == 0:
                    continue

                mouth1 = cv2.resize(mouth1, (80, 40))
                mouth2 = cv2.resize(mouth2, (80, 40))

                # Optical flow in mouth region
                flow = cv2.calcOpticalFlowFarneback(mouth1, mouth2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                mag = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
                mouth_motions.append(np.mean(mag))

            if len(mouth_motions) < 3:
                return 15.0  # Not enough data = probably no talking face, low suspicion

            # AI lip-sync: unnaturally smooth OR spiky motion
            motion_std = np.std(mouth_motions)
            motion_mean = np.mean(mouth_motions)
            cv_motion = motion_std / (motion_mean + 1e-6)  # Coefficient of variation

            # Very low CV = robotically smooth (AI)
            # Very high CV = glitchy motion (bad deepfake)
            if cv_motion < 0.3:
                return float(min(100, 60 + (0.3 - cv_motion) * 200))
            elif cv_motion > 1.5:
                return float(min(100, 60 + (cv_motion - 1.5) * 40))
            else:
                return float(max(5, 30 - (cv_motion - 0.3) * 25))
        except:
            return 50.0

    # ── Forensic Check 4: GAN Noise Fingerprint ───────────────────────────

    def check_gan_noise(self, frames: List[np.ndarray]) -> float:
        """FFT spectral analysis. GANs leave characteristic frequency patterns."""
        try:
            spectral_scores = []
            for frame in frames[:8]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (256, 256))

                # 2D FFT
                f = fft.fft2(gray.astype(np.float64))
                fshift = fft.fftshift(f)
                mag = np.log(np.abs(fshift) + 1)

                h, w = mag.shape
                cy, cx = h // 2, w // 2

                # Ring-based analysis (GANs show peaks at specific radii)
                radii = [0.1, 0.2, 0.3, 0.4, 0.5]
                ring_energies = []
                for r in radii:
                    inner = int(r * min(h, w))
                    outer = int((r + 0.05) * min(h, w))
                    y, x = np.ogrid[:h, :w]
                    dist = np.sqrt((x - cx)**2 + (y - cy)**2)
                    ring = (dist >= inner) & (dist < outer)
                    ring_energies.append(np.mean(mag[ring]))

                # Check for GAN-characteristic spectral peaks
                energy_std = np.std(ring_energies)
                energy_range = max(ring_energies) - min(ring_energies)
                
                # High frequency energy ratio (outer vs total)
                outer_mask = np.sqrt((np.arange(w)[None, :] - cx)**2 + (np.arange(h)[:, None] - cy)**2) > 0.4 * min(h, w)
                hf_ratio = np.mean(mag[outer_mask]) / (np.mean(mag) + 1e-6)

                # Calibrated thresholds: real videos typically have hf_ratio 0.3-0.7
                # GANs show hf_ratio > 0.8 and high energy_std > 1.5
                gan_score = 0
                if hf_ratio > 0.8:
                    gan_score += min(40, (hf_ratio - 0.8) * 200)
                if energy_std > 1.5:
                    gan_score += min(30, (energy_std - 1.5) * 20)
                if energy_range > 2.0:
                    gan_score += min(30, (energy_range - 2.0) * 15)
                spectral_scores.append(min(100, max(0, gan_score)))

            return float(np.mean(spectral_scores)) if spectral_scores else 20.0
        except:
            return 50.0

    # ── Forensic Check 5: Texture Regularity (LBP) ────────────────────────

    def check_texture_regularity(self, frames: List[np.ndarray]) -> float:
        """LBP (Local Binary Patterns) to detect unnatural texture smoothness."""
        try:
            texture_scores = []
            for frame in frames[:8]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (256, 256))

                # Compute LBP
                lbp = local_binary_pattern(gray, P=8, R=1, method='uniform')
                lbp_hist, _ = np.histogram(lbp.ravel(), bins=10, density=True)

                # Real images: diverse LBP patterns (higher entropy)
                # AI images: more uniform textures (lower entropy)
                entropy = -np.sum(lbp_hist * np.log2(lbp_hist + 1e-10))

                # Also check gradient variance (AI tends to be smoother)
                grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                grad_mag = np.sqrt(grad_x**2 + grad_y**2)
                grad_var = np.var(grad_mag)

                # Low entropy + low gradient variance = AI
                # Normalize: typical entropy range 2.0-3.5, grad_var 500-5000
                entropy_score = max(0, (3.0 - entropy) / 1.5) * 50  # Low entropy → high score
                grad_score = max(0, (2000 - grad_var) / 2000) * 50  # Low grad → high score

                texture_scores.append(min(100, entropy_score + grad_score))

            return float(np.mean(texture_scores)) if texture_scores else 50.0
        except:
            return 50.0

    # ── Forensic Check 6: Color Histogram Anomaly ─────────────────────────

    def check_color_anomaly(self, frames: List[np.ndarray]) -> float:
        """Analyze HSV color distribution for unnatural patterns."""
        try:
            anomaly_scores = []
            for frame in frames[:8]:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                # Hue distribution
                hue_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180]).flatten()
                hue_hist = hue_hist / (hue_hist.sum() + 1e-8)
                hue_entropy = -np.sum(hue_hist * np.log2(hue_hist + 1e-10))

                # Saturation statistics
                sat = hsv[:, :, 1].astype(np.float64)
                sat_std = np.std(sat)
                sat_skew = abs(stats.skew(sat.flatten()))

                # Value (brightness) statistics
                val = hsv[:, :, 2].astype(np.float64)
                val_kurtosis = abs(stats.kurtosis(val.flatten()))

                # AI-generated: often has unnatural color uniformity or oversaturation
                # Low hue entropy = limited color palette (AI)
                # Low sat std = unnaturally uniform saturation (AI)
                # High skew/kurtosis = unnatural distribution
                score = 0
                if hue_entropy < 4.5:
                    score += (4.5 - hue_entropy) * 15
                if sat_std < 40:
                    score += (40 - sat_std) * 0.5
                if sat_skew > 1.5:
                    score += min(20, (sat_skew - 1.5) * 10)
                if val_kurtosis > 3:
                    score += min(15, (val_kurtosis - 3) * 5)

                anomaly_scores.append(min(100, score))

            return float(np.mean(anomaly_scores)) if anomaly_scores else 50.0
        except:
            return 50.0

    # ── Forensic Check 7: Temporal Coherence ──────────────────────────────

    def check_temporal_coherence(self, frames: List[np.ndarray]) -> float:
        """Optical flow consistency. AI videos have unnatural motion patterns."""
        if len(frames) < 3:
            return 50.0

        try:
            magnitudes = []
            coherences = []

            for i in range(len(frames) - 1):
                g1 = cv2.resize(cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY), (320, 240))
                g2 = cv2.resize(cv2.cvtColor(frames[i+1], cv2.COLOR_BGR2GRAY), (320, 240))

                flow = cv2.calcOpticalFlowFarneback(g1, g2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                mag = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)

                magnitudes.append(np.mean(mag))
                coherences.append(1 - np.std(mag) / (np.mean(mag) + 1e-6))

            if len(magnitudes) < 3:
                return 50.0

            # Motion statistics
            motion_skew = abs(stats.skew(magnitudes))
            motion_kurt = abs(stats.kurtosis(magnitudes))
            motion_cv = np.std(magnitudes) / (np.mean(magnitudes) + 1e-6)
            avg_coherence = np.mean(coherences)

            # AI videos: irregular motion, high skew/kurtosis, low coherence
            score = 0
            if avg_coherence < 0.5:
                score += (0.5 - avg_coherence) * 100
            if motion_skew > 1.0:
                score += min(25, (motion_skew - 1.0) * 15)
            if motion_kurt > 2.0:
                score += min(20, (motion_kurt - 2.0) * 10)
            if motion_cv > 1.0:
                score += min(20, (motion_cv - 1.0) * 20)

            return float(min(100, max(0, score)))
        except:
            return 50.0

    # ── Forensic Check 8: Edge & Compression Artifacts ────────────────────

    def check_edge_artifacts(self, frames: List[np.ndarray]) -> float:
        """Laplacian + Canny analysis for AI generation boundary artifacts."""
        try:
            artifact_scores = []
            for frame in frames[:8]:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Laplacian variance (sharpness measure)
                lap = cv2.Laplacian(gray, cv2.CV_64F)
                lap_var = np.var(lap)
                lap_mean = np.mean(np.abs(lap))

                # Canny edge density
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size

                # Block artifact detection (8x8 block boundaries from JPEG/AI)
                h, w = gray.shape
                block_diffs = []
                for by in range(8, h - 8, 8):
                    row_diff = np.mean(np.abs(gray[by, :].astype(float) - gray[by-1, :].astype(float)))
                    block_diffs.append(row_diff)
                block_artifact = np.mean(block_diffs) if block_diffs else 0

                # AI-generated: often unnaturally sharp (high lap_var) or too smooth
                # Also: distinctive block boundary patterns
                score = 0
                if lap_var > 2000:  # Unnaturally sharp
                    score += min(30, (lap_var - 2000) / 200)
                elif lap_var < 100:  # Unnaturally smooth
                    score += min(30, (100 - lap_var) / 5)

                # High edge density with low variance = AI pattern
                if edge_density > 0.15:
                    score += min(20, (edge_density - 0.15) * 200)

                # Block artifacts
                if block_artifact > 8:
                    score += min(20, (block_artifact - 8) * 3)

                # Ratio of laplacian mean to variance can indicate AI
                ratio = lap_mean / (np.sqrt(lap_var) + 1e-6)
                if ratio > 0.8:
                    score += min(15, (ratio - 0.8) * 50)

                artifact_scores.append(min(100, score))

            return float(np.mean(artifact_scores)) if artifact_scores else 50.0
        except:
            return 50.0

    # ── Main Pipeline ─────────────────────────────────────────────────────

    def analyze_video(self, video_path: str) -> Dict[str, float]:
        """Run all 8 forensic checks and return signal vector + AI probability."""
        _log("      [FORENSICS] Starting 8-check analysis...")
        frames = self.extract_frames(video_path, num_frames=15)

        if len(frames) == 0:
            _log("      [FORENSICS] No frames extracted")
            return {
                'ai_probability': 50, 'confidence': 30,
                'signals': {}, 'triggered_patterns': ['No visual data found'],
                'feature_vector': [50]*8
            }

        # Run all 8 checks
        checks = [
            ("facial_consistency", self.check_facial_consistency),
            ("expression_symmetry", self.check_expression_symmetry),
            ("lip_sync", self.check_lip_sync),
            ("gan_noise", self.check_gan_noise),
            ("texture_regularity", self.check_texture_regularity),
            ("color_anomaly", self.check_color_anomaly),
            ("temporal_coherence", self.check_temporal_coherence),
            ("edge_artifacts", self.check_edge_artifacts),
        ]

        signals = {}
        feature_vector = []
        for name, fn in checks:
            _log(f"      [CHECK] {name}...")
            score = fn(frames)
            signals[name] = round(score, 1)
            feature_vector.append(score)

        # Print signal bars
        _log("      ----------------------------------------")
        for name, val in signals.items():
            bar = "#" * int(val / 5) + "-" * (20 - int(val / 5))
            _log(f"      {name:<25} [{bar}] {val:.1f}%")
        _log("      ----------------------------------------")

        # Weighted scoring (forensic-only, before ML classifier)
        weights = {
            'facial_consistency': 0.18,
            'expression_symmetry': 0.12,
            'lip_sync': 0.12,
            'gan_noise': 0.15,
            'texture_regularity': 0.13,
            'color_anomaly': 0.10,
            'temporal_coherence': 0.10,
            'edge_artifacts': 0.10,
        }

        base_prob = sum(signals[k] * weights[k] for k in weights)

        # Max-Boost: strong signals dominate
        top_signals = sorted(signals.values(), reverse=True)
        if top_signals[0] > 80:
            base_prob = max(base_prob, top_signals[0] * 0.7 + base_prob * 0.3)
        if len(top_signals) > 1 and top_signals[1] > 70:
            base_prob = max(base_prob, (top_signals[0] + top_signals[1]) / 2 * 0.6 + base_prob * 0.4)

        ai_probability = min(99.0, max(0.0, base_prob))

        # Confidence from signal agreement
        signal_std = np.std(list(signals.values()))
        strength = ai_probability if ai_probability > 50 else (100 - ai_probability)
        confidence = max(40, min(98, strength * 0.7 + (100 - signal_std) * 0.3))

        result = {
            'ai_probability': round(ai_probability, 1),
            'confidence': round(confidence, 1),
            'deepfake_risk': 'High' if ai_probability >= 70 else ('Medium' if ai_probability >= 45 else 'Low'),
            'signals': signals,
            'feature_vector': feature_vector,
            'triggered_patterns': self._get_patterns(signals),
        }

        _log(f"      [FORENSICS] Result: {result['ai_probability']}% AI (confidence {result['confidence']}%)")
        return result

    def _get_patterns(self, signals: Dict[str, float]) -> List[str]:
        patterns = []
        thresholds = {
            'facial_consistency': ("Facial inconsistency across frames", 55),
            'expression_symmetry': ("Unnaturally symmetric facial expressions", 60),
            'lip_sync': ("Lip-sync motion anomaly detected", 55),
            'gan_noise': ("GAN spectral noise fingerprint found", 55),
            'texture_regularity': ("Unnatural texture smoothness patterns", 55),
            'color_anomaly': ("Abnormal color distribution detected", 55),
            'temporal_coherence': ("Unnatural motion between frames", 55),
            'edge_artifacts': ("AI-generation boundary artifacts visible", 55),
        }
        for key, (desc, thresh) in thresholds.items():
            if signals.get(key, 0) > thresh:
                patterns.append(desc)
        return patterns


# Singleton
video_analyzer = VideoAIAnalyzer()