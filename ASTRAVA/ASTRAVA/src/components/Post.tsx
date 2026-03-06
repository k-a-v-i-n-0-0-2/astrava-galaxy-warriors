import { useState, memo } from 'react';
import type { FC } from 'react';
import { Heart, MessageCircle, Send, Bookmark, MoreHorizontal, Cpu, Scan, CheckCircle, AlertTriangle, X } from 'lucide-react';
import type { mockPosts } from '../data/mock';
import api from '../services/api';

type PostProps = {
    post: typeof mockPosts[0] & { location?: string };
};

interface PostAnalysis {
    score: number;
    confidence: string;
    details: string;
    signals?: Record<string, number>;
    label?: string;
}

export const Post: FC<PostProps> = memo(({ post }) => {
    const [isLiked, setIsLiked] = useState(post.isLiked);
    const [likesCount, setLikesCount] = useState(post.likes);
    const [isSaved, setIsSaved] = useState(false);
    const [showLikeAnimation, setShowLikeAnimation] = useState(false);
    const [isCaptionExpanded, setIsCaptionExpanded] = useState(false);

    // AI Analysis state
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<PostAnalysis | null>(null);
    const [scanProgress, setScanProgress] = useState(0);

    const handleLike = () => {
        setIsLiked(!isLiked);
        setLikesCount(prev => isLiked ? prev - 1 : prev + 1);
    };

    const handleDoubleTap = () => {
        if (!isLiked) {
            setIsLiked(true);
            setLikesCount(prev => prev + 1);
        }
        setShowLikeAnimation(true);
        setTimeout(() => setShowLikeAnimation(false), 1000);
    };

    const triggerAnalysis = async () => {
        if (analysisResult || isAnalyzing) return;

        setIsAnalyzing(true);
        setScanProgress(0);

        const interval = setInterval(() => {
            setScanProgress(prev => {
                if (prev >= 95) return 95;
                return prev + 3;
            });
        }, 80);

        try {
            const result = await api.detectMedia(post.image, post.id);

            const confidence = result.confidence || 0;
            const gemini = result.gemini_insights;

            const mapped: PostAnalysis = {
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
            }, 300);

        } catch (err) {
            console.error('Post analysis failed:', err);
            clearInterval(interval);
            setScanProgress(100);
            setTimeout(() => {
                setIsAnalyzing(false);
                setAnalysisResult({
                    score: 0.15,
                    confidence: 'Low',
                    details: 'Could not reach analysis server. Please ensure the backend is running.',
                });
            }, 300);
        }
    };

    const isAI = analysisResult && analysisResult.score > 0.5;

    return (
        <article className="border-b border-[#262626] sm:pb-5 sm:mb-5 pb-4 mb-4 mx-auto w-full max-w-[470px]">
            {/* Header */}
            <div className="flex items-center justify-between pb-3 px-4 sm:px-0">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full overflow-hidden bg-gradient-to-tr from-yellow-400 to-fuchsia-600 p-[2px] cursor-pointer">
                        <img src={post.user.avatar} alt={post.user.username} className="w-full h-full rounded-full border border-black" />
                    </div>
                    <div className="flex flex-col">
                        <div className="flex items-center gap-1">
                            <span className="font-semibold text-[14px] text-[#F5F5F5] cursor-pointer hover:text-gray-300">{post.user.username}</span>
                            <span className="text-[#a8a8a8] text-[14px]">• {post.timestamp}</span>
                        </div>
                        {post.location && (
                            <span className="text-[12px] text-[#F5F5F5]">{post.location}</span>
                        )}
                    </div>
                </div>
                <button className="text-[#f5f5f5] hover:text-[#a8a8a8] transition-colors">
                    <MoreHorizontal size={24} />
                </button>
            </div>

            {/* Image */}
            <div
                className="w-full relative sm:border border-y border-[#262626] sm:rounded-[4px] overflow-hidden flex justify-center bg-black cursor-pointer select-none"
                onDoubleClick={handleDoubleTap}
            >
                <img
                    src={post.image}
                    alt={`Post by ${post.user.username}`}
                    className="w-full object-cover max-h-[585px]"
                />

                {/* Double Tap Heart Animation */}
                {showLikeAnimation && (
                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
                        <Heart size={100} className="fill-white text-white drop-shadow-2xl animate-like-pop" />
                    </div>
                )}

                {/* Scanning Overlay */}
                {isAnalyzing && (
                    <div className="absolute inset-0 z-20 bg-black/50 backdrop-blur-sm flex flex-col items-center justify-center">
                        <div className="relative w-32 h-32 flex items-center justify-center">
                            <div className="absolute w-full h-0.5 bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.8)] animate-[scan_1.5s_ease-in-out_infinite_alternate] z-10" />
                            <Scan size={50} className="text-cyan-400/50" />
                        </div>
                        <div className="mt-4 text-cyan-400 font-mono text-sm font-bold tracking-widest animate-pulse">
                            SCANNING IMAGE
                        </div>
                        <div className="w-48 h-1.5 bg-gray-800 rounded-full mt-3 overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-cyan-600 to-cyan-400 transition-all duration-100"
                                style={{ width: `${scanProgress}%` }}
                            />
                        </div>
                    </div>
                )}

                {/* Analysis Result Banner (overlay on image) */}
                {analysisResult && (
                    <div className={`absolute top-3 left-3 right-3 z-20 p-3 rounded-lg backdrop-blur-md border border-white/10 shadow-xl
                        ${isAI ? 'bg-rose-500/25' : 'bg-emerald-500/25'}
                    `}>
                        <div className="flex items-start gap-2">
                            <div className={`p-1.5 rounded-full shrink-0 ${isAI ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                                {isAI ? <AlertTriangle size={18} /> : <CheckCircle size={18} />}
                            </div>
                            <div className="min-w-0">
                                <h3 className={`font-bold text-sm ${isAI ? 'text-rose-400' : 'text-emerald-400'}`}>
                                    {isAI ? 'AI GENERATED' : 'HUMAN CONTENT'}
                                </h3>
                                <div className="flex items-center gap-1.5 mt-0.5 mb-1">
                                    <div className="bg-white/10 px-1.5 py-0.5 rounded text-[10px] text-white/90">
                                        {(analysisResult.score * 100).toFixed(1)}% match
                                    </div>
                                    <div className="bg-white/10 px-1.5 py-0.5 rounded text-[10px] text-white/90">
                                        {analysisResult.confidence}
                                    </div>
                                </div>
                                <p className="text-[11px] text-white/70 leading-snug line-clamp-2">
                                    {analysisResult.details}
                                </p>

                                {/* Signal breakdown from backend */}
                                {analysisResult.signals && Object.keys(analysisResult.signals).length > 0 && (
                                    <div className="mt-2.5 space-y-1">
                                        {Object.entries(analysisResult.signals)
                                            .filter(([key]) => !key.startsWith('behavioral'))
                                            .slice(0, 4)
                                            .map(([key, val]) => (
                                                <div key={key} className="flex items-center gap-2">
                                                    <span className="text-[9px] text-white/40 uppercase w-24 truncate">{key.replace(/_(forensic|gemini)_/, ' ').replace(/_/g, ' ')}</span>
                                                    <div className="flex-1 h-0.5 bg-white/10 rounded-full overflow-hidden">
                                                        <div
                                                            className={`h-full rounded-full ${Number(val) > 60 ? 'bg-rose-400' : 'bg-emerald-400'}`}
                                                            style={{ width: `${Math.min(100, Number(val))}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-[9px] text-white/60 w-6 text-right">{Math.round(Number(val))}%</span>
                                                </div>
                                            ))}
                                    </div>
                                )}
                            </div>
                        </div>
                        <button
                            onClick={(e) => { e.stopPropagation(); setAnalysisResult(null); }}
                            className="absolute top-1.5 right-1.5 text-white/40 hover:text-white p-0.5"
                        >
                            <X size={14} />
                        </button>
                    </div>
                )}
            </div>

            {/* Action Bar */}
            <div className="pt-2 pb-2 px-4 sm:px-0">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <button onClick={handleLike} className="hover:text-[#a8a8a8] transition-colors active:scale-90 p-2 -ml-2">
                            <Heart
                                size={26} strokeWidth={1.5}
                                className={`transition-transform duration-200 ${isLiked ? 'fill-[#ff3040] text-[#ff3040] scale-110' : 'text-[#f5f5f5]'}`}
                            />
                        </button>
                        <button className="hover:text-[#a8a8a8] transition-colors active:scale-90 p-2">
                            <MessageCircle size={26} strokeWidth={1.5} className="text-[#f5f5f5] -scale-x-100" />
                        </button>
                        <button className="hover:text-[#a8a8a8] transition-colors active:scale-90 p-2">
                            <Send size={26} strokeWidth={1.5} className="text-[#f5f5f5]" />
                        </button>

                        {/* AI Eval Button */}
                        <button
                            onClick={triggerAnalysis}
                            disabled={isAnalyzing}
                            className={`p-1.5 rounded-full transition-all hover:scale-110 active:scale-90 ml-1 ${analysisResult
                                ? isAI
                                    ? 'bg-rose-500/20 text-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.3)]'
                                    : 'bg-emerald-500/20 text-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.3)]'
                                : 'bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 shadow-[0_0_8px_rgba(6,182,212,0.2)]'
                                }`}
                            title="AI Detection Analysis"
                        >
                            <Cpu size={20} />
                        </button>
                    </div>
                    <button onClick={() => setIsSaved(!isSaved)} className="hover:text-[#a8a8a8] transition-colors active:scale-90 p-2 -mr-2">
                        <Bookmark size={26} strokeWidth={1.5} className={`transition-transform duration-200 ${isSaved ? 'fill-white text-white scale-110' : 'text-[#f5f5f5]'}`} />
                    </button>
                </div>

                {/* Likes */}
                <div className="text-[14px] text-[#F5F5F5] mb-2 leading-[18px] px-4 sm:px-0">
                    Liked by <span className="font-semibold cursor-pointer">sarah_designs</span> and <span className="font-semibold cursor-pointer">{likesCount.toLocaleString()} others</span>
                </div>

                {/* Caption */}
                <div className="text-[14px] leading-[18px] text-[#F5F5F5] mb-1 px-4 sm:px-0">
                    <span className="font-semibold mr-1 cursor-pointer">{post.user.username}</span>
                    <span>
                        {isCaptionExpanded || post.caption.length <= 80
                            ? post.caption
                            : `${post.caption.substring(0, 80)}...`}
                    </span>
                    {!isCaptionExpanded && post.caption.length > 80 && (
                        <button
                            className="text-[#a8a8a8] ml-1 hover:text-white"
                            onClick={() => setIsCaptionExpanded(true)}
                        >
                            more
                        </button>
                    )}
                </div>

                {/* Comments Prompt */}
                <div className="text-[#a8a8a8] text-[14px] leading-[18px] mb-2 cursor-pointer px-4 sm:px-0">
                    View all {post.comments} comments
                </div>

                {/* Add Comment */}
                <div className="flex items-center justify-between group mt-2 px-4 sm:px-0">
                    <div className="flex items-center gap-3 w-full">
                        <img src="https://i.pravatar.cc/150?u=developer_alex" alt="You" className="w-6 h-6 rounded-full" />
                        <input
                            type="text"
                            placeholder="Add a comment..."
                            className="bg-transparent border-none outline-none flex-1 text-[13px] text-[#F5F5F5] placeholder-[#a8a8a8]"
                        />
                    </div>
                    <button className="font-semibold text-[#0095f6] hover:text-white hidden group-focus-within:block text-sm ml-2">
                        Post
                    </button>
                </div>
            </div>
        </article>
    );
});

