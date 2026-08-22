'use client';

import React from 'react';

interface BotAvatarProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
}

export default function BotAvatar({ size = 'md', className = '' }: BotAvatarProps) {
  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-12 h-12 text-xl',
    xl: 'w-16 h-16 text-3xl',
  };

  const iconSizes = {
    sm: 14,
    md: 18,
    lg: 26,
    xl: 36,
  };

  const currentSize = iconSizes[size];

  return (
    <div
      className={`relative inline-flex items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-500 to-emerald-700 text-white shadow-md border border-emerald-300/40 dark:border-emerald-500/30 overflow-hidden shrink-0 ${sizeClasses[size]} ${className}`}
    >
      {/* Subtle Background Glow Shimmer */}
      <div className="absolute inset-0 bg-gradient-to-tr from-white/20 via-transparent to-black/10" />

      {/* Modern Medical AI Icon SVG */}
      <svg
        width={currentSize}
        height={currentSize}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="relative z-10 drop-shadow-xs"
      >
        {/* Medical Cross Base with AI Pulse Nodes */}
        <path d="M12 2v20M2 12h20" strokeWidth="2.5" stroke="currentColor" />
        <circle cx="12" cy="12" r="3" fill="currentColor" fillOpacity="0.2" />
        {/* Orbiting Sparkle Stars */}
        <circle cx="12" cy="5" r="1.5" fill="#A7F3D0" />
        <circle cx="19" cy="12" r="1.5" fill="#A7F3D0" />
        <circle cx="12" cy="19" r="1.5" fill="#A7F3D0" />
        <circle cx="5" cy="12" r="1.5" fill="#A7F3D0" />
      </svg>
    </div>
  );
}
