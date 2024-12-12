import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUser } from "@fortawesome/free-solid-svg-icons";

interface PersonPickerProps {
  onPersonSelected: (person: string) => void;
  disabled: boolean;
}

export default function PersonPicker({
  onPersonSelected,
  disabled,
}: PersonPickerProps) {
  const getPerson = async () => {
    try {
      const response = await fetch("/api/twenty-questions/get-person", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      onPersonSelected(data.person);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div
      className="d-flex align-items-center justify-content-center flex-column"
      onClick={!disabled ? getPerson : undefined}
      role="button"
      tabIndex={0}
    >
      <div className={`pick-person-icon ${disabled ? "disabled" : ""}`}>
        <FontAwesomeIcon
          icon={faUser}
          size="4x"
          color={`hsl(var(--foreground))`}
        />
      </div>
      <div className="text-muted-foreground">
        {disabled ? "Loading..." : "Pick a new person"}
      </div>
    </div>
  );
}
