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
  error: string | null;
  errors: {
    prompts: string | null;
    files: string | null;
    reportUpdate: string | null;
    reportDelete: string | null;
  };
  setErrors: React.Dispatch<
    React.SetStateAction<{
      prompts: string | null;
      files: string | null;
      reportUpdate: string | null;
      reportDelete: string | null;
    }>
  >;
} | null>(null);

// Export a provider component
export function WorkProvider({ children }: { children: ReactNode }) {
  const [errors, setErrors] = useState<{
    prompts: string | null;
    files: string | null;
    reportUpdate: string | null;
    reportDelete: string | null;
  }>({
    prompts: null,
    files: null,
    reportUpdate: null,
    reportDelete: null,
  });

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

  const error =
    errors.prompts ||
    errors.files ||
    errors.reportUpdate ||
    errors.reportDelete;

  // Initialize all state using a custom initialization function
  const initializeFromStorage = () => {
    const availableReports = storage.get(storage.keys.AVAILABLE_REPORTS);
    const availableProjects = storage.get(storage.keys.AVAILABLE_PROJECTS);

    let selectedProject = storage.get(storage.keys.SELECTED_PROJECT);
    //if no project is selected, select the first available project
    //if project is selected but its not in the available projects, select the first available project
    //
    if (!selectedProject && availableProjects.length > 0) {
      selectedProject = availableProjects[0];
    } else if (
      selectedProject &&
      availableProjects.length > 0 &&
      !availableProjects.includes(selectedProject)
    ) {
      selectedProject = availableProjects[0];
    }

    let selectedReport = storage.get(storage.keys.SELECTED_REPORT);
    if (!selectedReport && availableReports.length > 0) {
      selectedReport = availableReports[0];
    } else if (
      selectedReport &&
      availableReports.length > 0 &&
      !availableReports.includes(selectedReport)
    ) {
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
  const [availableReports, setAvailableReports] = useState<Report[]>(
    initialData.availableReports
  );
  const [availableProjects, setAvailableProjects] = useState<Project[]>(
    initialData.availableProjects
  );
  const [selectedProject, setSelectedProject] = useState<Project | null>(
    initialData.selectedProject
  );
  const [selectedReport, setSelectedReport] = useState<Report | null>(
    initialData.selectedReport
  );
  const [selectedTab, setSelectedTab] = useState(initialData.selectedTab);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [availableFiles, setAvailableFiles] = useState<SourceFile[]>(
    initialData.availableFiles
  );

  useEffect(() => {
    if (selectedReport) {
      setLoadingPrompts(true);
      setErrors((prev) => ({ ...prev, prompts: null }));
      getPrompts(selectedReport.id)
        .then(setPrompts)
        .catch((err) => {
          setErrors((prev) => ({ ...prev, prompts: "Error getting prompts" }));
          console.error(err);
        })
        .finally(() => setLoadingPrompts(false));
    }
  }, [selectedReport]);

  useEffect(() => {
    if (selectedProject) {
      setLoadingFiles(true);
      setErrors((prev) => ({ ...prev, files: null }));
      getFiles(selectedProject.id)
        .then((files) => {
          setAvailableFiles(files);
        })
        .catch((err) => {
          setErrors((prev) => ({ ...prev, files: "Error getting files" }));
          console.error(err);
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
    setErrors((prev) => ({ ...prev, reportUpdate: null }));
    try {
      await updateReportApi(reportId, updates);
      if (selectedReport && selectedReport.id === reportId) {
        setSelectedReport((prev) => (prev ? { ...prev, ...updates } : null));
      }
    } catch (err) {
      setErrors((prev) => ({ ...prev, reportUpdate: "Error updating report" }));
      console.error(err);
    } finally {
      setLoadingReportUpdate(false);
    }
  };

  const deleteReport = async (reportId: string) => {
    setLoadingReportDelete(true);
    setErrors((prev) => ({ ...prev, reportDelete: null }));
    try {
      await deleteReportApi(reportId);
      if (selectedReport && selectedReport.id === reportId) {
        setSelectedReport(null);
      }
    } catch (err) {
      setErrors((prev) => ({ ...prev, reportDelete: "Error deleting report" }));
      console.error(err);
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
        errors,
        setErrors,
        error,
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
