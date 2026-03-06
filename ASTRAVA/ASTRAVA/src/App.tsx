import { useState, useRef, memo } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Layout } from './components/Layout';
import { Post } from './components/Post';
import { ReelsView } from './components/ReelsView';
import { ProfileView } from './components/ProfileView';
import { mockPosts } from './data/mock';
import './index.css';

const StoriesRow = memo(() => {
  const storiesRef = useRef<HTMLDivElement>(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(true);

  const handleScroll = () => {
    if (!storiesRef.current) return;
    const { scrollLeft, scrollWidth, clientWidth } = storiesRef.current;
    setShowLeftArrow(scrollLeft > 0);
    setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 5);
  };

  const scrollStories = (direction: 'left' | 'right') => {
    if (storiesRef.current) {
      const scrollAmount = direction === 'left' ? -320 : 320;
      storiesRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  return (
    <div className="relative w-full max-w-[630px] mb-[30px]">
      <div
        ref={storiesRef}
        onScroll={handleScroll}
        className="flex gap-[14px] overflow-x-auto w-full pb-4 pt-2 px-4 sm:px-2 scrollbar-none snap-x"
      >
        {[
          { name: "sarah_designs", img: "https://i.pravatar.cc/150?u=sarah" },
          { name: "tech_bro", img: "https://i.pravatar.cc/150?u=marcus" },
          { name: "creative_mind", img: "https://i.pravatar.cc/150?u=jessica" },
          { name: "photo_diary", img: "https://i.pravatar.cc/150?u=alex" },
          { name: "daily_coffee", img: "https://i.pravatar.cc/150?u=emma" },
          { name: "wanderlust.ai", img: "https://i.pravatar.cc/150?u=ryan" },
          { name: "yoga_vibes", img: "https://i.pravatar.cc/150?u=priya" },
        ].map((story, i) => (
          <div key={i} className="flex flex-col items-center gap-[6px] cursor-pointer shrink-0 snap-start">
            <div className={`w-[66px] h-[66px] rounded-full p-[2px] ${i > 3 ? 'bg-[#363636]' : 'bg-gradient-to-tr from-[#f09433] via-[#dc2743] to-[#bc1888]'}`}>
              <div className="w-full h-full rounded-full border-[2.5px] border-black overflow-hidden bg-black flex items-center justify-center">
                <img src={story.img} alt="story" className="w-[110%] h-[110%] object-cover" />
              </div>
            </div>
            <span className="text-xs text-[#F5F5F5] w-[70px] truncate text-center">{story.name}</span>
          </div>
        ))}
      </div>

      {/* Navigation Arrows */}
      {showLeftArrow && (
        <button
          onClick={() => scrollStories('left')}
          className="absolute left-4 top-[40px] -translate-y-1/2 w-[24px] h-[24px] bg-white text-black rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform hidden sm:flex z-10"
        >
          <ChevronLeft size={16} strokeWidth={3} />
        </button>
      )}
      {showRightArrow && (
        <button
          onClick={() => scrollStories('right')}
          className="absolute right-4 top-[40px] -translate-y-1/2 w-[24px] h-[24px] bg-white text-black rounded-full flex items-center justify-center shadow-lg hover:scale-110 transition-transform hidden sm:flex z-10"
        >
          <ChevronRight size={16} strokeWidth={3} />
        </button>
      )}
    </div>
  );
});

function App() {
  const [activeView, setActiveView] = useState('home');

  return (
    <Layout activeView={activeView} setActiveView={setActiveView}>
      {activeView === 'home' && (
        <div className="w-full flex justify-center py-2 sm:py-[22px]">
          <div className="w-full max-w-[630px] flex flex-col items-center">
            <StoriesRow />

            <div className="flex flex-col gap-0 w-full max-w-[470px]">
              {mockPosts.map(post => (
                <Post key={post.id} post={post} />
              ))}
            </div>
          </div>
        </div>
      )}

      {activeView === 'reels' && (
        <ReelsView />
      )}

      {activeView === 'profile' && (
        <ProfileView />
      )}
    </Layout>
  );
}

export default App;
