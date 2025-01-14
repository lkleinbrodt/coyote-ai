import {
  Project,
  Prompt,
  Report,
  Response,
  SourceFile,
} from "@/autodraft/types";

import axiosInstance from "@/autodraft/utils/axiosInstance";

// Fetch projects from the backend
export const getProjects = async (): Promise<Project[]> => {
  try {
    const response = await axiosInstance.get("/projects");
    return response.data; // Assuming the response contains the data you need
  } catch (error) {
    console.error("Error fetching projects:", error);
    throw error; // Throw error so you can handle it in your component
  }
};

// Fetch reports from the backend
export const getReports = async (projectID?: string): Promise<Report[]> => {
  try {
    const endpoint = projectID
      ? `/reports?project_id=${projectID}`
      : "/reports";
    const response = await axiosInstance.get(endpoint);
    console.log("reports");
    console.log(response.data);
    return response.data;
  } catch (error) {
    console.error("Error fetching reports:", error);
    throw error;
  }
};

export const newProject = async (name: string): Promise<Project> => {
  try {
    const response = await axiosInstance.post("/new-project", { name });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.status === 409) {
      throw new Error("Project already exists");
    }
    console.error("Error creating new project:", error);
    throw error;
  }
};

export const newReport = async (
  name: string,
  projectID: string
): Promise<Report> => {
  try {
    const response = await axiosInstance.post("/new-report", {
      name,
      project_id: projectID,
    });
    return response.data;
  } catch (error: any) {
    if (error.response && error.response.status === 409) {
      throw new Error("Report already exists");
    }
    console.error("Error creating new report:", error);
    throw error;
  }
};

export const getFiles = async (projectID: string): Promise<SourceFile[]> => {
  try {
    const response = await axiosInstance.get(`/files?project_id=${projectID}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching files:", error);
    throw error;
  }
};

export const uploadFile = async (
  file: File,
  projectID: string,
  overwrite: boolean = false
): Promise<SourceFile> => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("project_id", projectID.toString());
  formData.append("overwrite", overwrite.toString());
  try {
    const response = await axiosInstance.post("/upload-file", formData);

    return response.data;
  } catch (error) {
    console.error("Error uploading file:", error);
    throw error;
  }
};

export const createIndex = async (projectID: string) => {
  try {
    const response = await axiosInstance.post("/create-index", {
      project_id: projectID,
    });
    return response.data;
  } catch (error) {
    console.error("Error creating index:", error);
    throw error;
  }
};

export const generateResponse = async (
  prompt: string,
  promptID: string,
  projectID: string
): Promise<Response> => {
  try {
    const resp = await axiosInstance.post("/generate-response", {
      prompt: prompt,
      project_id: projectID,
      prompt_id: promptID,
    });
    return resp.data;
  } catch (error) {
    console.error("Error generating response:", error);
    throw error;
  }
};

export const getPrompts = async (reportID: string): Promise<Prompt[]> => {
  try {
    const response = await axiosInstance.get("/prompts", {
      params: { report_id: reportID },
    });
    const prompts: Prompt[] = response.data;
    return prompts;
  } catch (error) {
    console.error("Error fetching prompts:", error);
    throw error;
  }
};

export const newPrompt = async (
  text: string,
  reportID: string
): Promise<Prompt> => {
  try {
    const response = await axiosInstance.post("/new-prompt", {
      text,
      report_id: reportID,
    });
    return response.data;
  } catch (error) {
    console.error("Error creating new prompt:", error);
    throw error;
  }
};

export const updatePrompt = async (
  text: string,
  promptID: string
): Promise<Prompt> => {
  try {
    const response = await axiosInstance.post<Prompt>("/update-prompt", {
      text,
      prompt_id: promptID,
    });
    return response.data;
  } catch (error) {
    console.error("Error updating prompt:", error);
    throw error;
  }
};

export const indexAvailable = async (projectID: string): Promise<boolean> => {
  try {
    const response = await axiosInstance.get(
      `/index-available?project_id=${projectID}`
    );
    return response.data.exists;
  } catch (error) {
    console.error("Error checking if index is available:", error);
    throw error;
  }
};

export const deleteIndex = async (projectID: string) => {
  try {
    const response = await axiosInstance.post("/delete-index", {
      project_id: projectID,
    });
    return response.data;
  } catch (error) {
    console.error("Error deleting index:", error);
    throw error;
  }
};

export const updateResponse = async (
  text: string,
  responseID: string
): Promise<Response> => {
  try {
    const response = await axiosInstance.post("/update-response", {
      text,
      response_id: responseID,
    });
    return response.data;
  } catch (error) {
    console.error("Error updating response:", error);
    throw error;
  }
};

export const updateIndex = async (projectID: string) => {
  try {
    const response = await axiosInstance.post("/update-index", {
      project_id: projectID,
    });
    return response.data;
  } catch (error) {
    console.error("Error updating index:", error);
    throw error;
  }
};

export const updateOrCreateIndex = async (projectID: string) => {
  try {
    // First, try to update the index
    const updateResponse = await updateIndex(projectID);
    return updateResponse;
  } catch (error: any) {
    // Check if the error is due to the index not being found
    if (
      error.response &&
      error.response.status === 404 &&
      error.response.data.error === "Index not found"
    ) {
      // If the index doesn't exist, create a new one
      const createResponse = await createIndex(projectID);
      return createResponse;
    } else {
      // If it's a different error, throw it
      console.error("Error updating or creating index:", error);
      throw error;
    }
  }
};

export const deleteFile = async (fileID: string) => {
  try {
    const response = await axiosInstance.post("/delete-file", {
      file_id: fileID,
    });
    return response.data;
  } catch (error) {
    console.error("Error deleting file:", error);
    throw error;
  }
};

export const deletePrompt = async (promptID: string) => {
  try {
    const response = await axiosInstance.post("/delete-prompt", {
      prompt_id: promptID,
    });
    return response.data;
  } catch (error) {
    console.error("Error deleting prompt:", error);
    throw error;
  }
};

export const uploadTemplate = async (
  file: File,
  projectID: string,
  reportID: string
) => {
  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("project_id", projectID);
    formData.append("report_id", reportID);
    console.log(formData.get("file"));
    const response = await axiosInstance.post("/upload-template", formData);
    return response.data;
  } catch (error) {
    console.error("Error uploading template:", error);
    throw error;
  }
};

export const generateAll = async (reportID: string) => {
  try {
    const response = await axiosInstance.post("/generate-all", {
      report_id: reportID,
    });
    return response.data;
  } catch (error) {
    console.error("Error generating all:", error);
    throw error;
  }
};
