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
}

export const defaultResponse: Response = {
  id: "",
  text: "",
  position: 0,
  selected: false,
};

export const defaultPrompt: Prompt = {
  id: "",
  text: "",
  position: 0,
  responses: [defaultResponse],
};
