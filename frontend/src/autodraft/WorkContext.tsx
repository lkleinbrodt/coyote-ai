"use client";

import { Project, Prompt, Report, SourceFile } from "@/autodraft/types";
import {
  ReactNode,
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import { getFiles } from "@/autodraft/services/api";
import { getPrompts } from "@/autodraft/services/api";

// Create the context
const WorkContext = createContext<{
  selectedProject: Project | null;
  setSelectedProject: React.Dispatch<React.SetStateAction<Project | null>>;
  selectedReport: Report | null;
  setSelectedReport: React.Dispatch<React.SetStateAction<Report | null>>;
  selectedTab: string;
  setSelectedTab: React.Dispatch<React.SetStateAction<string>>;
  prompts: Prompt[];
  setPrompts: React.Dispatch<React.SetStateAction<Prompt[]>>;
  availableFiles: SourceFile[];
  setAvailableFiles: React.Dispatch<React.SetStateAction<SourceFile[]>>;
} | null>(null);

// Export a provider component
export function WorkProvider({ children }: { children: ReactNode }) {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [selectedTab, setSelectedTab] = useState("report");
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [availableFiles, setAvailableFiles] = useState<SourceFile[]>([]);

  useEffect(() => {
    if (selectedReport) {
      getPrompts(selectedReport.id).then(setPrompts);
    }
  }, [selectedReport]);

  useEffect(() => {
    if (selectedProject) {
      getFiles(selectedProject.id).then((files) => {
        setAvailableFiles(files);
      });
    }
  }, [selectedProject]);

  return (
    <WorkContext.Provider
      value={{
        selectedProject,
        setSelectedProject,
        selectedReport,
        setSelectedReport,
        selectedTab,
        setSelectedTab,
        prompts,
        setPrompts,
        availableFiles,
        setAvailableFiles,
      }}
    >
      {children}
    </WorkContext.Provider>
  );
}

// Create a custom hook to use the Project context
export function useWork() {
  const context = useContext(WorkContext);
  if (!context) {
    throw new Error("useWork must be used within a WorkProvider");
  }
  return context;
}
