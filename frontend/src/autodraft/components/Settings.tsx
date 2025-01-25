import PlaceholderMessage from "./PlaceholderMessage";
import ProjectSettings from "./ProjectSettings";
import ReportSettings from "./ReportSettings";
import { useWork } from "../WorkContext";

function Settings() {
  const { selectedProject } = useWork();

  if (!selectedProject) {
    return (
      <div>
        <PlaceholderMessage
          title="No project selected"
          description="Select a project to get started."
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-8">
      <ProjectSettings />
      <ReportSettings />
    </div>
  );
}

export default Settings;
