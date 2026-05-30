interface VideoPlayerProps {
  videoUrl: string;
  videoTitle?: string;
}

export const VideoPlayer = ({ videoUrl, videoTitle }: VideoPlayerProps) => {
  // Extract video ID from YouTube URL or use placeholder
  const getEmbedUrl = (url: string): string => {
    // Check if it's already an embed URL
    if (url.includes('embed')) return url;
    
    // Try to extract video ID from various YouTube URL formats
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})/,
      /youtube\.com\/results\?search_query=([^&]+)/  // Search query URL
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        // If it's a search query, redirect to YouTube search
        if (url.includes('search_query')) {
          return `https://www.youtube.com/embed/videoseries?list=PLB5F618CBD2F29F4D`; // Placeholder
        }
        return `https://www.youtube.com/embed/${match[1]}`;
      }
    }
    
    return url;
  };

  const embedUrl = getEmbedUrl(videoUrl);

  return (
    <div className="bg-gray-900 rounded-xl overflow-hidden shadow-lg">
      <div className="relative aspect-video">
        <iframe
          src={embedUrl}
          title={videoTitle || 'Video Tutorial'}
          className="absolute inset-0 w-full h-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
      {videoTitle && (
        <div className="p-4 bg-gray-800">
          <p className="text-white text-sm font-medium">{videoTitle}</p>
        </div>
      )}
    </div>
  );
};
