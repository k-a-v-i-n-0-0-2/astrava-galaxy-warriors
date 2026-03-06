import { useState, useRef, useEffect, memo } from 'react';
import type { FC } from 'react';
import { Heart, MessageCircle, Send, MoreHorizontal, Music, Cpu, Scan, CheckCircle, AlertTriangle } from 'lucide-react';
import type { mockReels } from '../data/mock';
import api from '../services/api';

type ReelProps = {
    reel: typeof mockReels[0];
};

interface BackendAnalysis {
    score: number;
    confidence: string;
    details: string;
    signals?: Record<string, number>;
    label?: string;
}

export const Reel: FC<ReelProps> = memo(({ reel }) => {
    const [isLiked, setIsLiked] = useState(false);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<BackendAnalysis | null>(null);
    const [scanProgress, setScanProgress] = useState(0);
    const videoRef = useRef<HTMLVideoElement>(null);

    const handleLike = () => setIsLiked(!isLiked);

    // Auto-play/pause based on visibility
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const observer = new IntersectionObserver(
            ([entry]) => {
                if (entry.isIntersecting) {
                    video.play().catch(() => { });
                } else {
                    video.pause();
                }
            },
            { threshold: 0.6 }
        );

        observer.observe(video);
        return () => observer.disconnect();
    }, []);

    const triggerAnalysis = async () => {
        if (analysisResult || isAnalyzing) return;

        setIsAnalyzing(true);
        setScanProgress(0);

        // Animate the progress bar
        const interval = setInterval(() => {
            setScanProgress(prev => {
                if (prev >= 95) return 95;
                return prev + 2;
            });
        }, 100);

        try {
            const result = await api.analyzeReel({
                id: reel.id,
                videoUrl: reel.videoUrl || reel.videoOverlayImage,
                username: reel.user.username,
                caption: reel.caption,
            });

            const confidence = result.confidence || 0;
            const gemini = result.gemini_insights;

            const mapped: BackendAnalysis = {
                score: confidence / 100,
                confidence: gemini?.confidence_level || (confidence > 70 ? 'High' : confidence > 40 ? 'Medium' : 'Low'),
                details: gemini?.details || gemini?.summary || result.label || 'Analysis complete.',
                signals: result.signals,
                label: result.label,
            };

            setScanProgress(100);

            setTimeout(() => {
                clearInterval(interval);
                setIsAnalyzing(false);
                setAnalysisResult(mapped);
            }, 400);

        } catch (err) {
            console.error('Analysis failed:', err);
            clearInterval(interval);
            setScanProgress(100);

            setTimeout(() => {
                setIsAnalyzing(false);
                setAnalysisResult(reel.aiAnalysis);
            }, 400);
        }
    };

    const isAI = analysisResult && analysisResult.score > 0.5;

    return (
        <div className="
            relative mx-auto bg-black overflow-hidden snap-start shrink-0
            flex items-center justify-center
            /* Mobile: full viewport */
            w-full h-[100dvh]
            /* Tablet portrait (640px+): keep full height, constrain width slightly */
            sm:h-[100dvh] sm:w-full
            /* Tablet landscape / small desktop (768px+): cap height, add rounded corners */
            md:h-[calc(100vh-80px)] md:max-h-[850px] md:max-w-[470px] md:rounded-xl
            /* Large desktop (1024px+): slight width bump */
            lg:max-w-[480px]
        ">

            {/* Background Video/Image */}
            {reel.videoUrl ? (
                <video
                    ref={videoRef}
                    src={reel.videoUrl}
                    className="absolute inset-0 w-full h-full object-cover"
                    autoPlay
                    loop
                    muted
                    playsInline
                    onDoubleClick={handleLike}
                />
            ) : (
                <img
                    src={reel.videoOverlayImage}
                    alt="Reel content"
                    className="absolute inset-0 w-full h-full object-cover opacity-90"
                    onDoubleClick={handleLike}
                />
            )}

            {/* Scanning Overlay */}
            {isAnalyzing && (
                <div className="absolute inset-0 z-20 bg-black/40 backdrop-blur-sm flex flex-col items-center justify-center px-4">
                    <div className="
                        relative flex items-center justify-center
                        w-28 h-28
                        xs:w-36 xs:h-36
                        sm:w-44 sm:h-44
                        md:w-48 md:h-48
                    ">
                        <div className="absolute w-full h-1 bg-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.8)] animate-[scan_1.5s_ease-in-out_infinite_alternate] z-10" />
                        <Scan className="text-cyan-400/50 w-12 h-12 sm:w-16 sm:h-16 md:w-20 md:h-20" />
                    </div>

                    <div className="mt-4 sm:mt-6 md:mt-8 text-cyan-400 font-mono text-sm sm:text-base md:text-xl font-bold tracking-widest animate-pulse text-center">
                        ANALYZING MEDIA
                    </div>

                    <div className="
                        h-2 bg-gray-800 rounded-full mt-3 sm:mt-4 overflow-hidden outline outline-1 outline-cyan-900/50
                        w-44 sm:w-56 md:w-64
                    ">
                        <div
                            className="h-full bg-gradient-to-r from-cyan-600 to-cyan-400 transition-all duration-100 ease-linear"
                            style={{ width: `${scanProgress}%` }}
                        />
                    </div>
                    <div className="text-cyan-400/80 font-mono text-[10px] sm:text-xs md:text-sm mt-2">
                        {scanProgress}% DEEP ANALYSIS
                    </div>
                </div>
            )}

            {/* Analysis Result Banner */}
            {analysisResult && (
                <div className={`
                    absolute z-20 p-2.5 sm:p-3 md:p-4 rounded-xl backdrop-blur-md border border-white/10 shadow-2xl
                    animate-in slide-in-from-top-4 fade-in duration-500
                    /* Positioning: tight on mobile, more breathing room on larger */
                    top-12 left-2 right-12
                    sm:top-14 sm:left-3 sm:right-14
                    md:top-16 md:left-4 md:right-16
                    ${isAI ? 'bg-rose-500/20 shadow-rose-500/20' : 'bg-emerald-500/20 shadow-emerald-500/20'}
                `}>
                    <div className="flex items-start gap-2 sm:gap-3">
                        <div className={`p-1.5 sm:p-2 rounded-full shrink-0 ${isAI ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                            {isAI
                                ? <AlertTriangle className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" />
                                : <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" />
                            }
                        </div>
                        <div className="min-w-0 flex-1">
                            <h3 className={`font-bold text-xs sm:text-sm md:text-lg leading-tight ${isAI ? 'text-rose-400' : 'text-emerald-400'}`}>
                                {isAI ? 'AI GENERATED MEDIA' : 'HUMAN GENERATED MEDIA'}
                            </h3>
                            <div className="flex items-center gap-1.5 sm:gap-2 mt-0.5 sm:mt-1 mb-1 sm:mb-2 flex-wrap">
                                <div className="bg-white/10 px-1.5 sm:px-2 py-0.5 rounded text-[9px] sm:text-[10px] md:text-xs text-white/90">
                                    Match: {(analysisResult.score * 100).toFixed(1)}%
                                </div>
                                <div className="bg-white/10 px-1.5 sm:px-2 py-0.5 rounded text-[9px] sm:text-[10px] md:text-xs text-white/90">
                                    Confidence: {analysisResult.confidence}
                                </div>
                            </div>
                            <p className="text-[10px] sm:text-xs md:text-sm text-white/80 leading-snug line-clamp-2 md:line-clamp-none">
                                {analysisResult.details}
                            </p>

                            {/* Signal breakdown from backend */}
                            {analysisResult.signals && Object.keys(analysisResult.signals).length > 0 && (
                                <div className="mt-2 sm:mt-2.5 md:mt-3 space-y-1 sm:space-y-1.5">
                                    {Object.entries(analysisResult.signals)
                                        .filter(([key]) => !key.startsWith('behavioral'))
                                        .slice(0, 4)
                                        .map(([key, val]) => (
                                            <div key={key} className="flex items-center gap-1.5 sm:gap-2">
                                                <span className="text-[8px] sm:text-[9px] md:text-[10px] text-white/50 uppercase w-16 sm:w-20 md:w-28 truncate shrink-0">
                                                    {key.replace(/forensic_|gemini_/g, '').replace(/_/g, ' ')}
                                                </span>
                                                <div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full ${Number(val) > 60 ? 'bg-rose-400' : 'bg-emerald-400'}`}
                                                        style={{ width: `${Math.min(100, Number(val))}%` }}
                                                    />
                                                </div>
                                                <span className="text-[8px] sm:text-[9px] md:text-[10px] text-white/70 w-6 sm:w-7 md:w-8 text-right shrink-0">
                                                    {Math.round(Number(val))}%
                                                </span>
                                            </div>
                                        ))}
                                </div>
                            )}
                        </div>
                    </div>
                    <button
                        onClick={() => setAnalysisResult(null)}
                        className="absolute top-1.5 right-1.5 sm:top-2 sm:right-2 text-white/50 hover:text-white text-base sm:text-lg leading-none w-5 h-5 flex items-center justify-center"
                        aria-label="Dismiss"
                    >
                        &times;
                    </button>
                </div>
            )}

            {/* Persistent Overlay Gradient */}
            <div className="absolute inset-0 bg-gradient-to-b from-black/20 via-transparent to-black/80 pointer-events-none z-10" />

            {/* Header (Top) */}
            <div className="absolute top-3 sm:top-4 left-3 sm:left-4 right-3 sm:right-4 z-10 flex justify-between items-center pointer-events-auto">
                <span className="font-bold text-lg sm:text-xl drop-shadow-md">Reels</span>
            </div>

            {/* Bottom Info Area */}
            <div className="
                absolute z-10 flex flex-col pointer-events-auto
                bottom-3 left-3 right-12
                sm:bottom-4 sm:left-4 sm:right-14
                md:right-16
                gap-2 sm:gap-2.5 md:gap-3
            ">
                {/* User row */}
                <div className="flex items-center gap-2">
                    <div className="
                        rounded-full overflow-hidden border border-white/20 shrink-0
                        w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10
                    ">
                        <img src={reel.user.avatar} alt={reel.user.username} className="w-full h-full object-cover" />
                    </div>
                    <span className="font-semibold drop-shadow-md text-sm sm:text-base truncate">{reel.user.username}</span>
                    <button className="
                        border border-white/80 rounded-lg font-semibold shrink-0 ml-1
                        hover:bg-white hover:text-black transition-colors
                        px-2 py-0.5 text-xs
                        sm:px-3 sm:py-1 sm:text-sm
                    ">
                        Follow
                    </button>
                </div>

                {/* Caption */}
                <p className="text-xs sm:text-sm drop-shadow-md line-clamp-2 pr-2 md:pr-4 leading-relaxed">
                    {reel.caption}
                </p>

                {/* Song pill */}
                <div className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm mt-0.5 bg-white/10 w-[max-content] max-w-full px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-full backdrop-blur-sm">
                    <Music className="animate-[spin_4s_linear_infinite] shrink-0 w-3 h-3 sm:w-3.5 sm:h-3.5" />
                    <span className="truncate max-w-[110px] sm:max-w-[140px] md:max-w-[160px]">{reel.song}</span>
                </div>
            </div>

            {/* Right Side Action Buttons */}
            <div className="
                absolute z-10 flex flex-col items-center pointer-events-auto
                bottom-3 right-1 gap-3.5
                sm:bottom-4 sm:right-1.5 sm:gap-5
                md:right-2 md:gap-6
            ">
                {/* Like */}
                <div className="flex flex-col items-center gap-0.5 group">
                    <button onClick={handleLike} className="p-1.5 sm:p-2 transition-transform active:scale-75">
                        <Heart className={`
                            transition-colors
                            w-6 h-6 sm:w-7 sm:h-7 md:w-7 md:h-7
                            ${isLiked ? 'fill-red-500 text-red-500' : 'text-white'}
                        `} />
                    </button>
                    <span className="text-[10px] sm:text-[11px] font-semibold">{reel.likes}</span>
                </div>

                {/* Comment */}
                <div className="flex flex-col items-center gap-0.5">
                    <button className="p-1.5 sm:p-2 transition-transform active:scale-75">
                        <MessageCircle className="text-white w-6 h-6 sm:w-7 sm:h-7 md:w-7 md:h-7" />
                    </button>
                    <span className="text-[10px] sm:text-[11px] font-semibold">{reel.comments}</span>
                </div>

                {/* Share */}
                <div className="flex flex-col items-center gap-0.5">
                    <button className="p-1.5 sm:p-2 transition-transform active:scale-75">
                        <Send className="text-white -rotate-12 w-6 h-6 sm:w-7 sm:h-7 md:w-7 md:h-7" />
                    </button>
                    <span className="text-[10px] sm:text-[11px] font-semibold">{reel.shares}</span>
                </div>

                {/* More */}
                <div className="flex flex-col items-center gap-0.5">
                    <button className="p-1.5 sm:p-2 transition-transform active:scale-75">
                        <MoreHorizontal className="text-white w-6 h-6 sm:w-7 sm:h-7 md:w-7 md:h-7" />
                    </button>
                </div>

                {/* AI Analysis Button */}
                <div className="flex flex-col items-center gap-0.5 mt-2 sm:mt-3 md:mt-4 relative">
                    <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full scale-150 pointer-events-none" />
                    <button
                        onClick={triggerAnalysis}
                        disabled={isAnalyzing}
                        className={`
                            relative overflow-hidden rounded-full border border-cyan-300/30
                            transition-all hover:scale-110 active:scale-90 group
                            p-2 sm:p-2.5 md:p-3
                            ${analysisResult
                                ? isAI
                                    ? 'bg-gradient-to-tr from-rose-600 to-orange-500 shadow-[0_0_15px_rgba(244,63,94,0.5)]'
                                    : 'bg-gradient-to-tr from-emerald-600 to-teal-500 shadow-[0_0_15px_rgba(16,185,129,0.5)]'
                                : 'bg-gradient-to-tr from-cyan-600 to-emerald-500 shadow-[0_0_15px_rgba(6,182,212,0.5)]'
                            }
                        `}
                    >
                        <div className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300" />
                        <Cpu className="text-white relative z-10 w-5 h-5 sm:w-6 sm:h-6 md:w-6.5 md:h-6.5" />
                    </button>
                    <span className={`
                        font-bold uppercase drop-shadow-[0_0_5px_rgba(6,182,212,0.8)] text-center
                        text-[8px] sm:text-[9px] md:text-[10px]
                        ${analysisResult
                            ? isAI ? 'text-rose-300' : 'text-emerald-300'
                            : 'text-cyan-300'
                        }
                    `}>
                        {analysisResult ? (isAI ? 'AI FOUND' : 'VERIFIED') : 'AI Eval'}
                    </span>
                </div>
            </div>
        </div>
    );
});