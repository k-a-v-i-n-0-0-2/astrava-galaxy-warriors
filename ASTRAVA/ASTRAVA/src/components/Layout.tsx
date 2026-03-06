import { useState } from 'react';
import type { FC, ReactNode } from 'react';
import { Home, Search, Compass, Film, MessageCircle, Heart, PlusSquare, User, Menu, Instagram, X } from 'lucide-react';

interface LayoutProps {
    children: ReactNode;
    activeView: string;
    setActiveView: (view: string) => void;
}

export const Layout: FC<LayoutProps> = ({ children, activeView, setActiveView }) => {
    const [activeDrawer, setActiveDrawer] = useState<'search' | 'notifications' | null>(null);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

    const handleNavClick = (view: string) => {
        if (view === 'search' || view === 'notifications') {
            setActiveDrawer(activeDrawer === view ? null : view);
        } else {
            setActiveDrawer(null);
            setActiveView(view);
        }
    };

    const isDrawerOpen = activeDrawer !== null;

    return (
        <div className="flex flex-col md:flex-row min-h-screen bg-black text-[#F5F5F5] font-sans selection:bg-white/30 truncate-x-hidden relative overflow-x-hidden">
            {/* Sidebar for Desktop */}
            <nav className={`hidden md:flex flex-col ${isDrawerOpen ? 'w-[72px]' : 'w-[72px] lg:w-[244px]'} border-r border-[#262626] fixed h-full z-50 bg-black pt-2 pb-5 px-3 transition-all duration-300`}>
                <div className="mb-[18px] lg:mb-8 pl-3 pt-6 pb-2 flex items-center h-[73px]">
                    <div className="text-white hover:scale-105 transition-transform cursor-pointer px-[10px]">
                        <Instagram size={28} className="stroke-[2px]" />
                    </div>
                </div>
                <div className="flex flex-col gap-1 relative h-full">
                    <NavItem label="Home" icon={<Home className={activeView === 'home' ? 'fill-white' : ''} />} active={activeView === 'home'} onClick={() => handleNavClick('home')} collapsed={isDrawerOpen} />
                    <NavItem label="Search" icon={<Search className={activeDrawer === 'search' ? 'stroke-[3px]' : ''} />} active={activeDrawer === 'search'} onClick={() => handleNavClick('search')} collapsed={isDrawerOpen} border={activeDrawer === 'search'} />
                    <NavItem label="Explore" icon={<Compass />} collapsed={isDrawerOpen} />
                    <NavItem label="Reels" icon={<Film className={activeView === 'reels' ? 'fill-white' : ''} />} active={activeView === 'reels'} onClick={() => handleNavClick('reels')} collapsed={isDrawerOpen} />
                    <NavItem
                        label="Messages"
                        icon={<MessageCircle />}
                        collapsed={isDrawerOpen}
                        badge={<div className="absolute -top-1.5 -right-1.5 bg-[#FF3040] text-white text-[10px] font-bold px-[5px] py-[1px] rounded-full border-[2px] border-black flex items-center justify-center">9+</div>}
                    />
                    <NavItem
                        label="Notifications"
                        icon={<Heart className={activeDrawer === 'notifications' ? 'fill-white' : 'stroke-[2px]'} />}
                        active={activeDrawer === 'notifications'}
                        onClick={() => handleNavClick('notifications')}
                        collapsed={isDrawerOpen}
                        border={activeDrawer === 'notifications'}
                        badge={!isDrawerOpen ? <div className="absolute top-0 right-0 w-[10px] h-[10px] bg-[#FF3040] rounded-full border-[2px] border-black"></div> : undefined}
                    />
                    <NavItem label="Create" icon={<PlusSquare />} onClick={() => setIsCreateModalOpen(true)} collapsed={isDrawerOpen} />
                    <NavItem label="Profile" icon={<User className={activeView === 'profile' ? 'fill-white' : ''} />} active={activeView === 'profile'} onClick={() => handleNavClick('profile')} collapsed={isDrawerOpen} />

                    <div className="mt-auto">
                        <NavItem label="More" icon={<Menu />} collapsed={isDrawerOpen} />
                    </div>
                </div>
            </nav>

            {/* Sliding Drawer (Desktop Only) */}
            <div className={`hidden md:block fixed top-0 bottom-0 left-[72px] w-full max-w-[397px] bg-black border-r border-[#262626] z-40  rounded-r-2xl shadow-[4px_0_24px_rgba(0,0,0,0.5)] transition-transform duration-300 ease-in-out ${isDrawerOpen ? 'translate-x-0' : '-translate-x-full'}`}>
                {activeDrawer === 'search' && (
                    <div className="flex flex-col h-full w-full">
                        <div className="pt-6 pb-8 px-6 border-b border-[#262626]">
                            <h2 className="text-2xl font-bold mb-8">Search</h2>
                            <div className="relative">
                                <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#a8a8a8]" />
                                <input
                                    type="text"
                                    placeholder="Search"
                                    className="w-full bg-[#262626] text-white rounded-lg pl-10 pr-4 py-2 text-sm outline-none focus:bg-[#262626]"
                                />
                                <button className="absolute right-3 top-1/2 -translate-y-1/2 bg-[#a8a8a8] rounded-full p-0.5 hidden">
                                    <X size={12} className="text-black" />
                                </button>
                            </div>
                        </div>
                        <div className="flex-1 overflow-y-auto pt-4 px-6">
                            <div className="flex justify-between items-center mb-4">
                                <span className="font-semibold text-base">Recent</span>
                                <button className="text-[#0095f6] text-sm font-semibold hover:text-white">Clear all</button>
                            </div>
                            <div className="flex flex-col gap-4 mt-6">
                                {/* Mock Recent Search History */}
                                {[
                                    { name: "creative_mind", desc: "Jessica • Following" },
                                    { name: "puppy_love", desc: "Golden Retrievers" },
                                    { name: "arch_digest", desc: "Architecture & Design" }
                                ].map((item, i) => (
                                    <div key={i} className="flex items-center justify-between cursor-pointer group">
                                        <div className="flex items-center gap-3">
                                            <img src={`https://i.pravatar.cc/150?u=s_${i}`} className="w-11 h-11 rounded-full object-cover" alt="Avatar" />
                                            <div className="flex flex-col shrink-0">
                                                <span className="font-semibold text-[14px] leading-tight">{item.name}</span>
                                                <span className="text-[#a8a8a8] text-[14px]">{item.desc}</span>
                                            </div>
                                        </div>
                                        <button className="text-[#a8a8a8] group-hover:text-white transition-colors p-1">
                                            <X size={16} />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
                {activeDrawer === 'notifications' && (
                    <div className="flex flex-col h-full w-full pt-6">
                        <h2 className="text-2xl font-bold px-6 mb-4">Notifications</h2>
                        <div className="flex-1 overflow-y-auto px-6">
                            <span className="font-bold text-[15px] mb-4 block mt-2">New</span>
                            {/* Mock Notifications */}
                            <div className="flex items-center gap-3 mb-6">
                                <div className="w-11 h-11 rounded-full bg-gradient-to-tr from-yellow-400 to-fuchsia-600 p-[2px]">
                                    <img src="https://i.pravatar.cc/150?u=sarah" className="w-full h-full rounded-full border border-black" alt="avatar" />
                                </div>
                                <div className="text-[14px] leading-[18px]">
                                    <span className="font-bold cursor-pointer">sarah_designs</span> started following you. <span className="text-[#a8a8a8]">2h</span>
                                </div>
                                <button className="ml-auto bg-[#0095f6] hover:bg-[#1877f2] text-white font-semibold text-sm px-4 py-1.5 rounded-lg transition-colors">
                                    Follow
                                </button>
                            </div>
                            <div className="flex items-center gap-3 mb-6">
                                <img src="https://i.pravatar.cc/150?u=marcus" className="w-11 h-11 rounded-full" alt="avatar" />
                                <div className="text-[14px] leading-[18px]">
                                    <span className="font-bold cursor-pointer">tech_bro</span> liked your comment: "This is exactly what I was looking for!" <span className="text-[#a8a8a8]">5h</span>
                                </div>
                                <img src="https://images.unsplash.com/photo-1542831371-32f555c86880?q=80&w=800&auto=format&fit=crop" className="w-11 h-11 object-cover ml-auto" alt="post" />
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Main Content Area */}
            <main className={`flex-1 ${isDrawerOpen ? 'md:ml-[72px]' : 'md:ml-[72px] lg:ml-[244px]'} w-full h-full pb-[50px] md:pb-0 min-h-screen bg-black relative transition-all duration-300 md:flex md:justify-center`}>

                {/* Mobile Top Header (Only on Home) */}
                {activeView === 'home' && (
                    <div className="md:hidden fixed top-0 w-full h-[60px] bg-black/80 backdrop-blur-md border-b border-[#262626] flex items-center justify-between px-4 z-50">
                        <div className="flex items-center mt-2 cursor-pointer">
                            <span className="font-['Instagram'] text-xl font-bold tracking-tight">Instagram</span>
                        </div>
                        <div className="flex items-center gap-5">
                            <div className="relative cursor-pointer">
                                <Heart size={24} strokeWidth={2} />
                                <div className="absolute top-0 right-0 w-[8px] h-[8px] bg-[#FF3040] rounded-full border border-black"></div>
                            </div>
                            <div className="relative cursor-pointer">
                                <MessageCircle size={24} strokeWidth={2} />
                                <div className="absolute -top-1.5 -right-1.5 bg-[#FF3040] text-white text-[10px] font-bold px-[4px] py-[1px] rounded-full border-[2px] border-black flex items-center justify-center">
                                    9+
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <div className={`w-full md:max-w-[630px] md:flex md:justify-center h-full min-h-screen ${activeView === 'home' ? 'pt-[60px] md:pt-0' : ''}`}>
                    {children}
                </div>
                {/* Desktop Right Sidebar (Right Column) */}
                {activeView === 'home' && (
                    <div className="hidden lg:block w-[320px] pt-[30px] pl-16 pr-4 mt-4">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-4 cursor-pointer">
                                <img src="https://i.pravatar.cc/150?u=developer_alex" alt="You" className="w-[44px] h-[44px] rounded-full object-cover" />
                                <div className="flex flex-col">
                                    <span className="font-semibold text-sm text-[#F5F5F5]">alex_developer</span>
                                    <span className="text-[#a8a8a8] text-[13px]">Alex</span>
                                </div>
                            </div>
                            <button className="text-[#0095f6] text-xs font-semibold hover:text-white">Switch</button>
                        </div>
                        <div className="flex items-center justify-between mb-4 mt-6">
                            <span className="text-[#a8a8a8] font-bold text-sm">Suggested for you</span>
                            <button className="text-white text-xs font-semibold hover:text-[#a8a8a8]">See all</button>
                        </div>
                        <div className="flex flex-col gap-4">
                            {[
                                { name: 'michael.codes', reason: 'Followed by tech_bro' },
                                { name: 'design_with_em', reason: 'Followed by sarah_designs' },
                                { name: 'thestartup_life', reason: 'Followed by creative_mind + 2 more' },
                                { name: 'daily.ui', reason: 'Suggested for you' },
                            ].map((user, i) => (
                                <div key={i} className="flex items-center justify-between">
                                    <div className="flex items-center gap-3 cursor-pointer">
                                        <img src={`https://i.pravatar.cc/150?u=suggest_${i}`} alt="User" className="w-[44px] h-[44px] rounded-full object-cover" />
                                        <div className="flex flex-col">
                                            <span className="font-semibold text-sm text-[#F5F5F5]">{user.name}</span>
                                            <span className="text-[#a8a8a8] text-[12px] truncate w-[140px]">{user.reason}</span>
                                        </div>
                                    </div>
                                    <button className="text-[#0095f6] text-xs font-semibold hover:text-white">Follow</button>
                                </div>
                            ))}
                        </div>

                        {/* Instagram Footer Links */}
                        <div className="mt-8 text-[#a8a8a8] text-[12px] leading-relaxed">
                            <div className="flex flex-wrap gap-x-1.5 gap-y-1">
                                <a href="#" className="hover:underline">About</a><span>·</span>
                                <a href="#" className="hover:underline">Help</a><span>·</span>
                                <a href="#" className="hover:underline">Press</a><span>·</span>
                                <a href="#" className="hover:underline">API</a><span>·</span>
                                <a href="#" className="hover:underline">Jobs</a><span>·</span>
                                <a href="#" className="hover:underline">Privacy</a><span>·</span>
                                <a href="#" className="hover:underline">Terms</a><span>·</span>
                                <a href="#" className="hover:underline">Locations</a><span>·</span>
                                <a href="#" className="hover:underline">Language</a><span>·</span>
                                <a href="#" className="hover:underline">Meta Verified</a>
                            </div>
                            <div className="mt-4 uppercase tracking-wider text-[12px]">
                                © 2026 INSTAGRAM FROM META
                            </div>
                        </div>
                    </div>
                )}

                {/* Floating Messages Bubble */}
                {activeView === 'home' && (
                    <div className="hidden lg:flex fixed bottom-6 right-6 z-50 bg-[#1a1a1a] border border-[#262626] rounded-full shadow-lg shadow-black/50 py-3 px-4 items-center gap-3 cursor-pointer hover:bg-[#262626] transition-colors">
                        <div className="relative">
                            <MessageCircle size={28} className="text-white fill-white/10" />
                            <div className="absolute -top-1.5 -right-1.5 bg-[#FF3040] text-white text-[12px] font-bold w-[18px] h-[18px] flex justify-center items-center rounded-full border-[2px] border-[#1a1a1a]">8</div>
                        </div>
                        <span className="text-white font-semibold text-[15px] pt-1 leading-none mr-2">Messages</span>
                        <div className="flex -space-x-2">
                            <img src="https://i.pravatar.cc/150?u=chat1" className="w-8 h-8 rounded-full border border-[#1a1a1a]" alt="avatar1" />
                            <img src="https://i.pravatar.cc/150?u=chat2" className="w-8 h-8 rounded-full border border-[#1a1a1a]" alt="avatar2" />
                            <img src="https://i.pravatar.cc/150?u=chat3" className="w-8 h-8 rounded-full border border-[#1a1a1a]" alt="avatar3" />
                            <div className="w-8 h-8 rounded-full bg-[#262626] border border-[#1a1a1a] flex items-center justify-center text-white text-xs font-bold shrink-0">
                                <Menu size={14} />
                            </div>
                        </div>
                    </div>
                )}
            </main>

            {/* Bottom Nav for Mobile */}
            <nav className="md:hidden fixed bottom-0 w-full h-[50px] bg-black border-t border-[#262626] flex items-center justify-around z-50 pb-safe">
                <MobileNavItem icon={<Home className={activeView === 'home' ? 'fill-white' : ''} />} onClick={() => setActiveView('home')} />
                <MobileNavItem icon={<Search />} />
                <MobileNavItem icon={<Film className={activeView === 'reels' ? 'fill-white' : ''} />} onClick={() => setActiveView('reels')} />
                <MobileNavItem icon={<PlusSquare />} onClick={() => setIsCreateModalOpen(true)} />
                <MobileNavItem icon={<User className={activeView === 'profile' ? 'fill-white' : ''} />} onClick={() => setActiveView('profile')} />
            </nav>

            {/* Create Post Modal */}
            {isCreateModalOpen && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-sm">
                    {/* Close Button */}
                    <button
                        onClick={() => setIsCreateModalOpen(false)}
                        className="absolute top-4 right-4 text-white hover:text-gray-300 p-2"
                    >
                        <X size={28} />
                    </button>

                    {/* Modal Content */}
                    <div className="bg-[#262626] w-full max-w-[350px] md:max-w-[500px] aspect-square rounded-xl flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200 shadow-2xl">
                        {/* Header */}
                        <div className="h-[42px] border-b border-[#363636] flex items-center justify-center font-semibold text-[15px]">
                            Create new post
                        </div>
                        {/* Body */}
                        <div className="flex-1 flex flex-col items-center justify-center p-6 gap-4">
                            <svg aria-label="Icon to represent media such as images or videos" className="mb-2" color="#F5F5F5" fill="#F5F5F5" height="77" role="img" viewBox="0 0 97.6 77.3" width="96"><path d="M16.3 24h.3c2.8-.2 4.9-2.6 4.8-5.4-.2-2.8-2.6-4.9-5.4-4.8s-4.9 2.6-4.8 5.4c.1 2.7 2.4 4.8 5.1 4.8zm-2.4-7.2c.5-.6 1.3-1 2.1-1h.2c1.7 0 3.1 1.4 3.1 3.1 0 1.7-1.4 3.1-3.1 3.1-1.7 0-3.1-1.4-3.1-3.1 0-.8.3-1.5.8-2.1z" fill="currentColor"></path><path d="M84.7 18.4L58 16.9l-.2-3c-.3-5.7-5.2-10.1-11-9.8L12.9 6c-5.7.3-10.1 5.3-9.8 11L5 51v.8c.7 5.2 5.1 9.1 10.3 9.1h.6l21.7-1.2v.6c-.3 5.7 4 10.7 9.8 11l34 2h.6c5.5 0 10.1-4.3 10.4-9.8l2-34c.4-5.8-4-10.7-9.7-11.1zM7.2 10.8C8.7 9.1 10.8 8.1 13 8l34-1.9c4.6-.3 8.6 3.3 8.9 7.9l.2 2.8-5.3-.3c-5.7-.3-10.7 4-11 9.8l-1.5 23.2-1.2.1v-.1c-.4-4.6-4.3-8.2-8.9-7.9l-22.1 1.2c-4.4.2-8.1 3.6-8.7 7.9l-1-17.6c-.3-4.6 3.1-8.7 7.8-9zM82.8 61c-.3 4.6-4.3 8.2-8.9 7.9l-34-2c-4.6-.3-8.2-4.3-7.9-8.9l2-34c.3-4.4 3.9-8 8.4-8h.5l26.7 1.5c4.6.3 8.2 4.3 7.9 8.9l-2 34z" fill="currentColor"></path><path d="M78.2 41.6L61.3 30.5c-2.1-1.4-4.9-.8-6.2 1.3-.4.7-.7 1.4-.7 2.2l-1.2 20.1c-.1 2.5 1.7 4.6 4.2 4.8h.3c2.5 0 4.6-1.9 4.8-4.4l.2-3.3 10.6-2.6c1.2-.3 2.2-1.2 2.7-2.3.5-1.1.4-2.4-.3-3.4zm-14.7-6.5c.3-.5.9-.8 1.5-.8.5 0 1.1.2 1.4.6l10 6.6-11.4 2.8-.2-9.2h-.1l-1.2-10zM19.1 40l6.2-11c1.2-2.1 3.8-2.9 5.9-1.7 1.1.6 1.9 1.6 2.3 2.8l2.9 8.5 1.4-1.3c1.7-1.6 4.4-1.5 6 .2.8.9 1.2 2.1 1.2 3.3H45V37h.1l-1-7.2c-.2-1.1-.8-2-1.7-2.6-2.1-1.2-4.7-.5-5.9 1.6l-6.2 11c-1.2 2.1-3.8 2.9-5.9 1.7-1.1-.6-1.9-1.6-2.3-2.8l-2.9-8.5-1.4 1.3c-1.7 1.6-4.4 1.5-6-.2-.8-.9-1.2-2.1-1.2-3.3H19v3.8l.1Z" fill="currentColor"></path></svg>
                            <span className="text-xl font-light text-[#F5F5F5]">Drag photos and videos here</span>
                            <button className="bg-[#0095f6] hover:bg-[#1877f2] text-white font-semibold text-sm px-4 py-1.5 rounded-lg mt-2 transition-colors">
                                Select from computer
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const NavItem = ({ label, icon, active = false, onClick, badge, collapsed = false, border = false }: { label: string; icon: ReactNode; active?: boolean; onClick?: () => void; badge?: ReactNode; collapsed?: boolean; border?: boolean }) => {
    return (
        <button onClick={onClick} className={`flex items-center gap-4 p-3 rounded-lg hover:bg-[#1a1a1a] transition-all group w-full ${active ? 'font-bold' : 'font-normal'} ${border ? 'border border-[#262626] bg-[#1a1a1a]' : ''}`}>
            <div className={`relative flex items-center justify-center transition-transform group-hover:scale-110 group-active:scale-95 text-[#F5F5F5]`}>
                <div className={`[&>svg]:w-6 [&>svg]:h-6 [&>svg]:stroke-[2px] transition-colors`}>
                    {icon}
                </div>
                {badge}
            </div>
            <span className={`${collapsed ? 'hidden' : 'hidden lg:block'} text-[16px] leading-[24px] pt-[2px]`}>{label}</span>
        </button>
    );
}

const MobileNavItem = ({ icon, onClick }: { icon: ReactNode; onClick?: () => void }) => {
    return (
        <button onClick={onClick} className="flex items-center justify-center w-12 h-12 active:scale-90 transition-transform">
            <div className={`transition-transform [&>svg]:w-6 [&>svg]:h-6 [&>svg]:stroke-[2px] text-[#F5F5F5]`}>
                {icon}
            </div>
        </button>
    );
}
