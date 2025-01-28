import { ProjectSelector } from "@/autodraft/components/ProjectSelector";
import { ReportSelector } from "@/autodraft/components/ReportSelector";
import UserItem from "@/autodraft/components/UserItem";
import { useWork } from "@/autodraft/WorkContext";

function Sidebar() {
  const { selectedProject } = useWork();
  return (
    <div className="fixed flex flex-col gap-4 w-[300px] min-w-[300px] border-r min-h-screen p-4 z-1000">
      <UserItem />

      <div className="grow">
        <div className="text-muted-foreground font-semibold mb-2">
          Current Project
        </div>

        <ProjectSelector />
        {selectedProject && (
          <>
            <div className="text-muted-foreground font-semibold mt-2 mb-2">
              Current Report
            </div>
            <ReportSelector />
          </>
        )}
      </div>
    </div>
  );
}

export default Sidebar;
