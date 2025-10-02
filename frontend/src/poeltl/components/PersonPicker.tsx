interface PersonPickerProps {
  onClick: () => void;
  loading: boolean;
}

export default function PersonPicker({ onClick, loading }: PersonPickerProps) {
  return (
    <button
      className="flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-dashed border-slate-300 dark:border-white/30 hover:border-blue-500 hover:bg-slate-50 dark:hover:bg-white/10 backdrop-blur-sm transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed group transform hover:scale-105 active:scale-95"
      onClick={!loading ? onClick : undefined}
      disabled={loading}
    >
      <div className="mb-4">
        <img
          src="icons/AI Basketball.png"
          alt="AI Assistant"
          className={`h-16 w-16 transition-all duration-300 ${
            loading ? "animate-pulse" : ""
          } group-hover:scale-110`}
        />
      </div>
      <div className="text-lg font-bold text-slate-700 dark:text-white/80 group-hover:text-blue-700 dark:group-hover:text-blue-400 transition-colors">
        {loading ? "Loading..." : "Pick a new person"}
      </div>
      <div className="text-xs text-slate-500 dark:text-white/60 mt-1 group-hover:text-blue-600 dark:group-hover:text-blue-300 transition-colors">
        {loading ? "Getting ready..." : "Click to start a new game"}
      </div>
    </button>
  );
}
