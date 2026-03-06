import type { FC } from 'react';
import { Reel } from './Reel';
import { mockReels } from '../data/mock';

export const ReelsView: FC = () => {
    return (
        <div className="w-full h-[calc(100dvh-50px)] md:h-[calc(100vh-40px)] md:flex md:justify-center bg-black md:pt-4">
            <div className="w-full md:max-w-[470px] h-full overflow-y-scroll snap-y snap-mandatory scrollbar-none relative">
                {mockReels.map((reel) => (
                    <Reel key={reel.id} reel={reel} />
                ))}
            </div>
        </div>
    );
};
