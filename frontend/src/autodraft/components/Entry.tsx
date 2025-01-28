import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Prompt, Response, defaultResponse } from "@/autodraft/types";
import React, { useEffect, useState } from "react";
import {
  addResponse,
  deletePrompt,
  generateResponse,
  updatePrompt,
  updateResponse,
} from "@/autodraft/services/api";

import { AutosizeTextarea } from "./AutoSizeTextArea";
import { Button } from "@/components/ui/button";
import { ReloadIcon } from "@radix-ui/react-icons";
import SourceDocs from "./SourceDocs";
import { Textarea } from "@/components/ui/textarea";
import { TrashIcon } from "lucide-react";
import { useWork } from "@/autodraft/WorkContext";

interface EntryProps {
  initialPrompt: Prompt;
  setPrompts: React.Dispatch<React.SetStateAction<Prompt[]>>;
}

const Entry: React.FC<EntryProps> = ({ initialPrompt, setPrompts }) => {
  const [prompt, setPrompt] = useState<Prompt>(initialPrompt);

  const [previousPromptText, setPreviousPromptText] = useState<string>();
  const [response, setResponse] = useState<Response>(
    initialPrompt.responses && initialPrompt.responses.length > 0
      ? initialPrompt.responses[0]
      : defaultResponse
  );

  const [previousResponseText, setPreviousResponseText] = useState<string>("");
  const [isEditingPrompt, setIsEditingPrompt] = useState<boolean>(false);
  const { selectedProject } = useWork();
  const [generating, setGenerating] = useState<boolean>(false);

  useEffect(() => {
    setPrompt(initialPrompt);
    if (initialPrompt.responses && initialPrompt.responses.length > 0) {
      setResponse(initialPrompt.responses[0]);
    } else {
      setResponse(defaultResponse);
    }
  }, [initialPrompt]);

  function handleDeletePrompt() {
    if (prompt) {
      deletePrompt(prompt.id).then(() => {
        setPrompts((prevPrompts) =>
          prevPrompts.filter((p) => p.id !== prompt.id)
        );
      });
    }
  }

  function savePrompt() {
    setIsEditingPrompt(false);
    if (prompt) {
      if (prompt?.text !== previousPromptText) {
        updatePrompt(prompt.text, prompt.id).then((promptDetails) => {
          setPreviousPromptText(promptDetails.text);
          setPrompt(promptDetails);
        });
      }
    }
  }

  function saveResponse(text: string, id: string) {
    if (text !== previousResponseText) {
      if (id == "-1") {
        // this is the default id, aka no response has been created yet
        addResponse(text, prompt.id).then((response: Response) => {
          setResponse(response);
        });
      } else {
        updateResponse(text, id).then((response: Response) => {
          setPreviousResponseText(response.text);
          setResponse(response);
        });
      }
    }
  }

  function requestResponse() {
    if (selectedProject && prompt) {
      setGenerating(true);
      generateResponse(prompt.text, prompt.id, selectedProject.id)
        .then((response: Response) => {
          setResponse(response);
        })
        .finally(() => {
          setGenerating(false);
        });
    }
  }

  return (
    <Card>
      <CardHeader>
        <div>
          {isEditingPrompt ? (
            <Textarea
              value={prompt?.text}
              onChange={(e) =>
                //update the current prompt with new text
                setPrompt({ ...prompt, text: e.target.value })
              }
              onBlur={savePrompt}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  savePrompt();
                }
              }}
              autoFocus
            />
          ) : (
            <div className="flex flex-row justify-between">
              <CardTitle
                onClick={() => setIsEditingPrompt(true)}
                className="cursor-pointer mr-10"
              >
                {prompt?.text}
              </CardTitle>
              <Button onClick={handleDeletePrompt} variant="ghost">
                <TrashIcon className="h-4 w-4 text-red-500 hover:text-red-700" />
              </Button>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        <AutosizeTextarea
          value={response.text}
          onChange={(e) => setResponse({ ...response, text: e.target.value })}
          onBlur={() => saveResponse(response.text, response.id)}
          className="w-full mb-4"
        />
        <SourceDocs sourceDocs={response.source_docs} />
        <div className="mt-3">
          {generating ? (
            <Button disabled>
              <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
              Generating
            </Button>
          ) : (
            <Button onClick={() => requestResponse()}>
              {response?.text ? "Regenerate" : "Generate"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default Entry;
