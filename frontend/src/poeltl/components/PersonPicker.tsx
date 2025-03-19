import { User } from "lucide-react";

interface PersonPickerProps {
  onClick: () => void;
  loading: boolean;
}

export default function PersonPicker({ onClick, loading }: PersonPickerProps) {
  return (
    <div
      className="flex flex-col items-center justify-center z-10"
      onClick={!loading ? onClick : undefined}
      role="button"
      tabIndex={0}
    >
      <div>
        <User className="h-16 w-16 text-foreground" />
      </div>
      <div className="text-muted-foreground">
        {loading ? "Loading..." : "Pick a new person"}
      </div>
    </div>
  );
}
