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
import { storage } from "@/utils/storage";

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
  loadingPrompts: boolean;
  loadingFiles: boolean;
  loadingReportUpdate: boolean;
  loadingReportDelete: boolean;
} | null>(null);

// Export a provider component
export function WorkProvider({ children }: { children: ReactNode }) {
  const [loadingPrompts, setLoadingPrompts] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [loadingReportUpdate, setLoadingReportUpdate] = useState(false);
  const [loadingReportDelete, setLoadingReportDelete] = useState(false);

  // Compute overall loading state
  const loading =
    loadingPrompts ||
    loadingFiles ||
    loadingReportUpdate ||
    loadingReportDelete;

  // Initialize all state using a custom initialization function
  const initializeFromStorage = () => {
    const availableReports = storage.get(storage.keys.AVAILABLE_REPORTS);
    const availableProjects = storage.get(storage.keys.AVAILABLE_PROJECTS);

    let selectedProject = storage.get(storage.keys.SELECTED_PROJECT);
    if (!selectedProject && availableProjects.length > 0) {
      selectedProject = availableProjects[0];
    }

    let selectedReport = storage.get(storage.keys.SELECTED_REPORT);
    if (!selectedReport && availableReports.length > 0) {
      selectedReport = availableReports[0];
    }

    return {
      availableReports,
      availableProjects,
      selectedProject,
      selectedReport,
      selectedTab: storage.get(storage.keys.SELECTED_TAB),
      availableFiles: storage.get(storage.keys.AVAILABLE_FILES),
    };
  };

  // Keep separate useState calls for better maintainability
  const initialData = initializeFromStorage();
  const [availableReports, setAvailableReports] = useState(
    initialData.availableReports
  );
  const [availableProjects, setAvailableProjects] = useState(
    initialData.availableProjects
  );
  const [selectedProject, setSelectedProject] = useState(
    initialData.selectedProject
  );
  const [selectedReport, setSelectedReport] = useState(
    initialData.selectedReport
  );
  const [selectedTab, setSelectedTab] = useState(initialData.selectedTab);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [availableFiles, setAvailableFiles] = useState(
    initialData.availableFiles
  );

  useEffect(() => {
    if (selectedReport) {
      setLoadingPrompts(true);
      getPrompts(selectedReport.id)
        .then(setPrompts)
        .finally(() => setLoadingPrompts(false));
    }
  }, [selectedReport]);

  useEffect(() => {
    if (selectedProject) {
      setLoadingFiles(true);
      getFiles(selectedProject.id)
        .then((files) => {
          setAvailableFiles(files);
        })
        .finally(() => setLoadingFiles(false));
    }
  }, [selectedProject]);

  useEffect(() => {
    storage.set(storage.keys.SELECTED_PROJECT, selectedProject);
  }, [selectedProject]);

  useEffect(() => {
    storage.set(storage.keys.SELECTED_REPORT, selectedReport);
  }, [selectedReport]);

  useEffect(() => {
    storage.set(storage.keys.SELECTED_TAB, selectedTab);
  }, [selectedTab]);

  const updateReport = async (reportId: string, updates: Partial<Report>) => {
    setLoadingReportUpdate(true);
    try {
      await updateReportApi(reportId, updates);
      if (selectedReport && selectedReport.id === reportId) {
        setSelectedReport((prev) => (prev ? { ...prev, ...updates } : null));
      }
    } finally {
      setLoadingReportUpdate(false);
    }
  };

  const deleteReport = async (reportId: string) => {
    setLoadingReportDelete(true);
    try {
      await deleteReportApi(reportId);
      if (selectedReport && selectedReport.id === reportId) {
        setSelectedReport(null);
      }
    } finally {
      setLoadingReportDelete(false);
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
        loadingPrompts,
        loadingFiles,
        loadingReportUpdate,
        loadingReportDelete,
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
