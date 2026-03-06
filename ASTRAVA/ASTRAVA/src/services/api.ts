const API_BASE_URL = '/api';

export interface AnalysisResult {
    confidence: number;
    label: string;
    behavioral_score: number;
    media_score: number;
    signals: Record<string, number>;
    triggered_patterns: string[];
    gemini_insights: {
        summary: string;
        risk_factors: string;
        recommendation: string;
        ai_score?: number;
        confidence_level?: string;
        details?: string;
    } | null;
    timestamp: string;
    video_id?: string;
    reel_metadata?: {
        username: string;
        caption: string;
    };
}

const api = {
    analyzeReel: async (reelData: {
        id: string;
        videoUrl: string;
        username: string;
        caption: string;
    }): Promise<AnalysisResult> => {
        const response = await fetch(`${API_BASE_URL}/analyze/reel`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                reel: {
                    id: reelData.id,
                    video_url: reelData.videoUrl,
                    username: reelData.username,
                    caption: reelData.caption,
                },
                interactions: [],
            }),
        });
        if (!response.ok) throw new Error('Reel analysis failed');
        return response.json();
    },

    detectMedia: async (mediaUrl: string, postId?: string): Promise<AnalysisResult> => {
        const response = await fetch('/detect', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                media_url: mediaUrl,
                post_id: postId || 'post_unknown',
            }),
        });
        if (!response.ok) throw new Error('Detection failed');
        return response.json();
    },
};

export default api;
