import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

import { ProjectSelector } from "@/autodraft/components/ProjectSelector";
import { ReportSelector } from "@/autodraft/components/ReportSelector";
import { useWork } from "@/autodraft/WorkContext";

function Sidebar() {
  const { selectedProject } = useWork();
  return (
    <div className="fixed flex flex-col gap-4 w-[300px] min-w-[300px] border-r min-h-screen p-4 z-1000">
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

        <Card className="mt-4">
          <CardHeader className="mb-0">
            <CardTitle>How to use AutoDraft</CardTitle>
          </CardHeader>

          <CardContent>
            <ol className="list-decimal list-inside pl-0 space-y-2 pt-0 mt-0 mb-0">
              <li>
                Create projects to organize your work, and upload source files
                related to each project so the AI can use them as context.
              </li>
              <li>
                All reports under the same project share the same source files
              </li>
              <li>Let AutoDraft generate a first draft of your report</li>
              <li>Make sure to review its responses; AIs can make mistakes</li>
            </ol>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default Sidebar;
