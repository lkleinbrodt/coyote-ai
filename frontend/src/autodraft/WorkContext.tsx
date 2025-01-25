"use client";

import { Project, Prompt, Report, SourceFile } from "@/autodraft/types";
import {
  ReactNode,
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";
import {
  deleteReport as deleteReportApi,
  updateReport as updateReportApi,
} from "./services/api";

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
  updateReport: (reportId: string, updates: Partial<Report>) => Promise<void>;
  deleteReport: (reportId: string) => Promise<void>;
  availableReports: Report[];
  setAvailableReports: React.Dispatch<React.SetStateAction<Report[]>>;
  availableProjects: Project[];
  setAvailableProjects: React.Dispatch<React.SetStateAction<Project[]>>;
  loading: boolean;
} | null>(null);

// Export a provider component
export function WorkProvider({ children }: { children: ReactNode }) {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [selectedTab, setSelectedTab] = useState("report");
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [availableFiles, setAvailableFiles] = useState<SourceFile[]>([]);
  const [availableReports, setAvailableReports] = useState<Report[]>([]);
  const [availableProjects, setAvailableProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedReport) {
      setLoading(true);
      getPrompts(selectedReport.id)
        .then(setPrompts)
        .finally(() => setLoading(false));
    }
  }, [selectedReport]);

  useEffect(() => {
    if (selectedProject) {
      setLoading(true);
      getFiles(selectedProject.id)
        .then((files) => {
          setAvailableFiles(files);
        })
        .finally(() => setLoading(false));
    }
  }, [selectedProject]);

  const updateReport = async (reportId: string, updates: Partial<Report>) => {
    await updateReportApi(reportId, updates);
    if (selectedReport && selectedReport.id === reportId) {
      setSelectedReport((prev) => (prev ? { ...prev, ...updates } : null));
    }
  };

  const deleteReport = async (reportId: string) => {
    await deleteReportApi(reportId);
    if (selectedReport && selectedReport.id === reportId) {
      setSelectedReport(null);
    }
  };

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
        updateReport,
        deleteReport,
        availableReports,
        setAvailableReports,
        availableProjects,
        setAvailableProjects,
        loading,
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
