const LoadingPage = () => (
  <div className="flex items-center justify-center w-full h-full min-h-[400px]">
    <div className="space-y-4 w-full max-w-3xl px-6">
      <div className="h-8 bg-gray-200 rounded animate-pulse w-1/3" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-full" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" />
      <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6" />
      <div className="h-32 bg-gray-200 rounded animate-pulse w-full mt-6" />
    </div>
  </div>
);

export default LoadingPage;
