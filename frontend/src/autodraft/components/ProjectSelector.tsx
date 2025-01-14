"use client";

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
import { Input } from "@/components/ui/input";
import { PlusIcon } from "@radix-ui/react-icons";
import { Project } from "@/autodraft/types";
import { SelectBox } from "./SelectBox";
import { useAuth } from "@/contexts/AuthContext";
import { useWork } from "@/autodraft/WorkContext";

export function ProjectSelector() {
  const [availableProjects, setAvailableProjects] = useState<Project[]>([]);
  const [newProjectName, setNewProjectName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [canCreate, setCanCreate] = useState(false);
  const closeButtonRef = useRef<HTMLButtonElement>(null);
  const {
    selectedProject,
    setSelectedProject,
    setSelectedReport,
    setSelectedTab,
  } = useWork();

  const { user } = useAuth();

  const handleChange = (value: { id: string; name: string }) => {
    //get the correct project from the available projects
    const project = availableProjects.find((p) => p.id === value.id);
    if (project) {
      setSelectedProject(project);
      setSelectedReport(null);
    } else {
      console.error("Project not found");
    }
  };

  useEffect(() => {
    if (user) {
      getProjects().then((projects) => {
        setAvailableProjects(projects);
        //set selected project to the first one
        if (projects.length > 0) {
          setSelectedProject(projects[0]);
        }
      });
    }
  }, [user, setAvailableProjects, setSelectedProject]);

  const handleSubmit = () => {
    if (!canCreate) return;
    newProject(newProjectName).then((project) => {
      setAvailableProjects([...availableProjects, project]);
      setSelectedProject(project);
      setSelectedTab("data");
      setSelectedReport(null);
    });
    closeButtonRef.current?.click();
  };

  const handleNewProjectChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const name = e.target.value;
    setNewProjectName(name);

    if (name.length === 0) {
      setCanCreate(false);
      setError("Project name cannot be empty");
      return;
    }
    setError(null);

    if (availableProjects.some((project) => project.name === name)) {
      setCanCreate(false);
      setError("Project name already taken");
      return;
    }
    setError(null);
    setCanCreate(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && canCreate) {
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-row gap-4">
      <SelectBox
        options={availableProjects}
        value={{
          id: selectedProject?.id,
          name: selectedProject?.name,
        }}
        setValue={handleChange}
      />
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon">
            <PlusIcon />
          </Button>
        </SheetTrigger>
        <SheetContent side="left">
          <SheetHeader>
            <SheetTitle>New Project</SheetTitle>
            <div className="flex flex-row gap-2">
              <Input
                placeholder="Project name"
                onChange={handleNewProjectChange}
                onKeyDown={handleKeyDown}
              />

              <SheetClose>
                <Button
                  onClick={handleSubmit}
                  disabled={!canCreate}
                  ref={closeButtonRef}
                >
                  Create
                </Button>
              </SheetClose>
            </div>
          </SheetHeader>
          {error && <p className="text-red-500">{error}</p>}
        </SheetContent>
      </Sheet>
    </div>
  );
}

export default ProjectSelector;
