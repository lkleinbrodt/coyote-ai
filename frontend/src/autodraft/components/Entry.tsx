import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChevronDown, RefreshCcw, TrashIcon } from "lucide-react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Prompt, Response, defaultResponse } from "@/autodraft/types";
import React, { useEffect, useState } from "react";
import {
  addResponse,
  deletePrompt,
  generateResponse,
  updatePrompt,
  updateResponse,
} from "@/autodraft/services/api";

import { AutodraftIcon } from "./AutodraftIcon";
import { AutosizeTextarea } from "./AutoSizeTextArea";
import { Button } from "@/components/ui/button";
import { ReloadIcon } from "@radix-ui/react-icons";
import SourceDocs from "./SourceDocs";
import { Textarea } from "@/components/ui/textarea";
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
              <div className="flex flex-row">
                {response.text.length > 0 && (
                  <Popover>
                    <PopoverTrigger className="text-s text-muted-foreground hover:underline decoration-dotted flex items-center gap-1">
                      <span>{response.source_docs.length} Sources</span>
                      <ChevronDown className="h-4 w-4" />
                    </PopoverTrigger>
                    <PopoverContent>
                      <SourceDocs sourceDocs={response.source_docs} />
                    </PopoverContent>
                  </Popover>
                )}
                <Button onClick={handleDeletePrompt} variant="ghost">
                  <TrashIcon className="h-4 w-4 text-red-500 hover:text-red-700" />
                </Button>
              </div>
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

        <div className="mt-3 flex justify-end w-full">
          {generating ? (
            <Button disabled>
              <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
              Generating
            </Button>
          ) : (
            <Button onClick={() => requestResponse()}>
              {response?.text ? (
                <RefreshCcw className="mr-0 h-4 w-4" />
              ) : (
                <AutodraftIcon className="mr-0 h-5 w-5" theme="dark" />
              )}
              {response?.text ? "Regenerate" : "Generate"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default Entry;
