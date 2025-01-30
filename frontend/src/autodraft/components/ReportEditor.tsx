import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Download, Loader2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Prompt, Response } from "@/autodraft/types";
import { generateResponse, getPrompts } from "@/autodraft/services/api";

import { AutodraftIcon } from "./AutodraftIcon";
import { Button } from "@/components/ui/button";
import { ChevronDownIcon } from "@radix-ui/react-icons";
import Entry from "./Entry";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import NewPrompt from "./NewPrompt";
import PlaceholderMessage from "./PlaceholderMessage";
import TemplateUploader from "./TemplateUploader";
import { exportDocx } from "./exportFunctions";
import { useState } from "react";
import { useWork } from "@/autodraft/WorkContext";

const ReportEditor = () => {
  const {
    selectedProject,
    selectedReport,
    prompts,
    setPrompts,
    loading,
    error,
    availableFiles,
  } = useWork();

  const [generatingAll, setGeneratingAll] = useState<boolean>(false);
  const [generationError, setGenerationError] = useState<string | null>(null);
  const [, setResponsesGenerated] = useState<number>(0);

  function handleGenerateAll() {
    if (!selectedReport) {
      return;
    }
    setGeneratingAll(true);
    setResponsesGenerated(0);

    //instead of doing it in one route, let's do it entry by entry
    //this will allow us to update the UI as we go
    // generateAll(selectedReport.id).then(() => {
    //   getPrompts(selectedReport.id).then(setPrompts);
    //   setGeneratingAll(false);
    // });

    function requestResponse(prompt: Prompt) {
      //TODO: lots of overlap with Entry.tsx
      if (!selectedProject) {
        if (!selectedProject) return Promise.reject("No project selected");
      }

      try {
        generateResponse(prompt.text, prompt.id, selectedProject.id).then(
          (response: Response) => {
            const updatedPrompt = { ...prompt, responses: [response] };
            setPrompts((prevPrompts) =>
              prevPrompts.map((p) => (p.id === prompt.id ? updatedPrompt : p))
            );
            setResponsesGenerated((prev) => {
              const newCount = prev + 1;
              if (newCount === prompts.length) {
                setGeneratingAll(false);
              }
              return newCount;
            });
          }
        );
      } catch (error) {
        console.error("Error generating response:", error);
        setGenerationError("Error generating response");
      }
    }
    Promise.all(prompts.map((prompt) => requestResponse(prompt))).catch(
      (error) => {
        console.error("Error generating all responses:", error);
        setGenerationError("Error generating all responses");
        setGeneratingAll(false);
      }
    );
  }

  function handleExport() {
    if (!selectedProject || !selectedReport) {
      return;
    }

    exportDocx(prompts, selectedProject, selectedReport);
  }

  if (!selectedProject) {
    return (
      <div>
        <PlaceholderMessage
          title="No project selected"
          description="Select a project to get started."
        />
      </div>
    );
  }

  if (!selectedReport) {
    return (
      <div>
        <PlaceholderMessage
          title="No report selected"
          description="Select a report to get started."
        />
      </div>
    );
  }

  return (
    <div className="p-4">
      {(error || generationError) && (
        <Alert variant="destructive" className="mb-4">
          <ExclamationTriangleIcon className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error || generationError}</AlertDescription>
        </Alert>
      )}
      {availableFiles.length === 0 && (
        <Alert variant="destructive" className="mb-4">
          <ExclamationTriangleIcon className="h-4 w-4" />
          <AlertTitle>No source files available</AlertTitle>
          <AlertDescription>
            Go to the data tab to upload files related to this project.
          </AlertDescription>
        </Alert>
      )}

      <div className="mb-5 flex gap-4">
        {selectedReport && (
          <div>
            <h1 className="text-4xl font-bold tracking-tight">
              {selectedReport.name}
            </h1>
          </div>
        )}
        <div className="flex gap-4 justify-end grow">
          <Button
            onClick={handleGenerateAll}
            className="flex justify-between ml-0 pl-0"
            disabled={
              prompts.length === 0 ||
              generatingAll ||
              !selectedProject?.index_available
            }
          >
            {generatingAll ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <AutodraftIcon className="mr-2 h-6 w-6" theme="dark" />
            )}
            Generate All
          </Button>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              disabled={
                prompts.length === 0 ||
                generatingAll ||
                !selectedProject?.index_available
              }
            >
              <ChevronDownIcon className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem onClick={handleExport}>
              <Download className="mr-2 h-4 w-4" />
              Export
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      {loading ? (
        <div className="flex justify-center items-center h-[50vh]">
          <Loader2 className="h-8 w-8 animate-spin" />
        </div>
      ) : (
        <>
          {prompts.length === 0 && !error ? (
            <div className="mb-6">
              <Card>
                <CardHeader>
                  <CardTitle>Report Template</CardTitle>
                  <CardDescription>
                    Upload a template document to structure your report. The
                    template will be used as a starting point for generating
                    content.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <TemplateUploader
                    projectID={selectedProject.id}
                    reportID={selectedReport.id}
                    onUploadSuccess={() => {
                      getPrompts(selectedReport.id).then(setPrompts);
                    }}
                  />
                </CardContent>
              </Card>
            </div>
          ) : (
            <>
              {prompts.map((prompt) => (
                <div key={prompt.id} className="mb-4">
                  <Entry initialPrompt={prompt} setPrompts={setPrompts} />
                </div>
              ))}
              <div className="flex justify-center mb-10 gap-4">
                <NewPrompt
                  prompts={prompts}
                  setPrompts={setPrompts}
                  reportID={selectedReport.id}
                />
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default ReportEditor;
