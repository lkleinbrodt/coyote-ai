import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser } from "@fortawesome/free-solid-svg-icons";

interface PersonPickerProps {
  onClick: () => void;
  loading: boolean;
}

export default function PersonPicker({ onClick, loading }: PersonPickerProps) {
  return (
    <div
      className="d-flex align-items-center justify-content-center flex-column z-10"
      onClick={!loading ? onClick : undefined}
      role="button"
      tabIndex={0}
    >
      <div>
        <FontAwesomeIcon
          icon={faUser}
          size="4x"
          color={`hsl(var(--foreground))`}
        />
      </div>
      <div className="text-muted-foreground">
        {loading ? "Loading..." : "Pick a new person"}
      </div>
    </div>
  );
}
