import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Prompt, Response } from "@/autodraft/types";
import { generateResponse, getPrompts } from "@/autodraft/services/api";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import Entry from "./Entry";
import { ExclamationTriangleIcon } from "@radix-ui/react-icons";
import { Loader2 } from "lucide-react";
import NewPrompt from "./NewPrompt";
import PlaceholderMessage from "./PlaceholderMessage";
import TemplateUploader from "./TemplateUploader";
import { exportDocx } from "./exportFunctions";
import { useWork } from "@/autodraft/WorkContext";

const ReportEditor = () => {
  const { selectedProject, selectedReport, prompts, setPrompts, loading } =
    useWork();
  const [indexAvailable, setIndexAvailable] = useState<boolean>(true);
  const [generatingAll, setGeneratingAll] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [, setResponsesGenerated] = useState<number>(0);

  useEffect(() => {
    if (selectedProject) {
      setIndexAvailable(selectedProject.index_available);
    }
  }, [selectedProject]);

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
        setError("Error generating response");
      }
    }
    Promise.all(prompts.map((prompt) => requestResponse(prompt))).catch(
      (error) => {
        console.error("Error generating all responses:", error);
        setError("Error generating all responses");
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

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[50vh]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
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
      {error && (
        <Alert variant="destructive" className="mb-4">
          <ExclamationTriangleIcon className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}
      {!indexAvailable && (
        <Alert variant="destructive" className="mb-4">
          <ExclamationTriangleIcon className="h-4 w-4" />
          <AlertTitle>Index not available</AlertTitle>
          <AlertDescription>
            Go to the data tab to create an index.
          </AlertDescription>
        </Alert>
      )}

      {prompts.length === 0 && (
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
      )}
      <div className="flex justify-center mb-10 gap-4">
        <Button
          className="w-1/5 text-xl font-bold py-4 bg-blue-500 hover:bg-blue-600 text-white shadow-lg"
          onClick={handleGenerateAll}
          disabled={prompts.length === 0 || generatingAll || !indexAvailable}
        >
          {generatingAll ? (
            <Loader2 className="animate-spin" />
          ) : (
            "Generate All"
          )}
        </Button>
        <Button
          className="w-1/5 text-xl font-bold py-4"
          onClick={handleExport}
          disabled={prompts.length === 0}
        >
          Export
        </Button>
      </div>

      {prompts.map((prompt) => (
        <div key={prompt.id} className="mb-4">
          <Entry initialPrompt={prompt} setPrompts={setPrompts} />
        </div>
      ))}
      <NewPrompt
        prompts={prompts}
        setPrompts={setPrompts}
        reportID={selectedReport.id}
      />
    </div>
  );
};

export default ReportEditor;
