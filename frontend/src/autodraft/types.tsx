export interface Prompt {
  id: string;
  text: string;
  position: number;
  responses: Response[];
}

export interface Response {
  id: string;
  text: string;
  position: number;
  selected: boolean;
  source_docs: Document[];
}

export interface SourceFile {
  id: string;
  name: string;
  project_id: string;
  created_at: string;
  last_modified: string;
}

export interface Project {
  id: string;
  name: string;
  index_id: string;
  index_available: boolean;
}

export interface Report {
  id: string;
  name: string;
  project_id: string;
  created_at: string;
  updated_at: string;
}

export const defaultResponse: Response = {
  id: "-1",
  text: "",
  position: 0,
  selected: false,
  source_docs: [],
};

export const defaultPrompt: Prompt = {
  id: "",
  text: "",
  position: 0,
  responses: [defaultResponse],
};

export interface Document {
  id: string;
  created_at: string;
  last_modified: string;
  uploaded_at: string;
  content: string;
  file_id: string;
  file: SourceFile;
  page_label: string;
}
