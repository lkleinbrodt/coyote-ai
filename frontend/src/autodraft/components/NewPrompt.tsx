import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

import { AutosizeTextarea } from "./AutoSizeTextArea";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { Prompt } from "@/autodraft/types";
import { newPrompt } from "@/autodraft/services/api";
import { useState } from "react";

interface NewPromptProps {
  prompts: Prompt[];
  setPrompts: React.Dispatch<React.SetStateAction<Prompt[]>>;

  reportID: string;
}

export function NewPrompt({ prompts, setPrompts, reportID }: NewPromptProps) {
  const [promptText, setPromptText] = useState<string>("");

  const handleSubmit = async () => {
    const promptDetails = await newPrompt(promptText, reportID);

    setPrompts([...prompts, promptDetails]);
    setPromptText("");
  };
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" className="gap-2 row-auto">
          <Plus className="h-5 w-5" />
          New Prompt
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>New Prompt</DialogTitle>
          {/* <DialogDescription>
            Make changes to your profile here. Click save when you're done.
          </DialogDescription> */}
        </DialogHeader>
        <AutosizeTextarea
          value={promptText}
          onChange={(e) => setPromptText(e.target.value)}
          maxHeight={200}
        />
        <DialogFooter>
          <DialogClose asChild>
            <Button type="submit" onClick={handleSubmit}>
              Save changes
            </Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default NewPrompt;
