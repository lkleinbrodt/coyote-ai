import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { getProjects, newProject } from "@/autodraft/services/api";
import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/ui/button";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { Input } from "@/components/ui/input";
import { PlusIcon } from "@radix-ui/react-icons";
import { SelectBox } from "./SelectBox";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/contexts/AuthContext";
import { useWork } from "@/autodraft/WorkContext";

export function ProjectSelector() {
  const [newProjectName, setNewProjectName] = useState("");
  const [createError, setCreateError] = useState<string | null>(null);
  const [canCreate, setCanCreate] = useState(false);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const {
    selectedProject,
    setSelectedProject,
    setSelectedReport,
    setSelectedTab,
    availableProjects,
    setAvailableProjects,
    loading,
  } = useWork();
  const { user } = useAuth();
  const [loadingError, setLoadingError] = useState<string | null>(null);

  useEffect(() => {
    getProjects()
      .then((projects) => {
        setAvailableProjects(projects);
        if (projects.length > 0 && !selectedProject) {
          setSelectedProject(projects[0]);
        }
        setLoadingError(null);
      })
      .catch((err) => {
        console.error("Failed to load projects:", err);
        setLoadingError("Failed to load projects.");
      });
  }, [setAvailableProjects, setSelectedProject, selectedProject]);

  const handleChange = (value: { id: string; name: string }) => {
    const project = availableProjects.find((p) => p.id === value.id);
    if (project) {
      setSelectedProject(project);
      setSelectedReport(null);
    }
  };

  const handleSubmit = async () => {
    if (!canCreate) return;
    try {
      const project = await newProject(newProjectName);
      setAvailableProjects([...availableProjects, project]);
      setSelectedProject(project);
      setSelectedTab("data");
      setSelectedReport(null);
      // Reset state
      setNewProjectName("");
      setCreateError(null);
      setCanCreate(false);
    } catch (err) {
      console.error("Failed to create new project:", err);
    }
  };

  const handleNewProjectChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name = e.target.value;
    setNewProjectName(name);

    if (name.length === 0) {
      setCanCreate(false);
      setCreateError("Project name cannot be empty");
      return;
    }
    setCreateError(null);

    if (availableProjects.some((project) => project.name === name)) {
      setCanCreate(false);
      setCreateError("Project name already taken");
      return;
    }
    setCreateError(null);
    setCanCreate(true);
  };

  if (loadingError) {
    return (
      <Alert variant="destructive">
        <ExclamationTriangleIcon className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{loadingError}</AlertDescription>
      </Alert>
    );
  }

  if (loading) {
    return (
      <div className="flex flex-row gap-4">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-10 w-10" />
      </div>
    );
  }

  return (
    <div className="flex flex-row gap-4">
      <SelectBox
        options={availableProjects}
        value={{
          id: selectedProject?.id,
          name: selectedProject?.name,
        }}
        setValue={handleChange}
        emptyMessage="Press + to create a new project."
      />
      {/* account for the navbar height */}
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon">
            <PlusIcon />
          </Button>
        </SheetTrigger>
        <SheetContent side="left">
          <SheetHeader>
            <SheetTitle>New Project</SheetTitle>
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (canCreate) {
                  handleSubmit();
                }
              }}
              className="flex w-full gap-2 mt-2"
            >
              <Input
                placeholder="Project name"
                onChange={handleNewProjectChange}
                value={newProjectName}
              />
              <SheetClose>
                <Button
                  type="submit"
                  disabled={!canCreate}
                  ref={closeButtonRef}
                >
                  Create
                </Button>
              </SheetClose>
            </form>
          </SheetHeader>
          {createError && <p className="text-red-500 mt-2">{createError}</p>}
        </SheetContent>
      </Sheet>
    </div>
  );
}

export default ProjectSelector;
