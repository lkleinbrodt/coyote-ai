import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

import { Button } from "@/components/ui/button";
import { FileIcon } from "@radix-ui/react-icons";
import { Loader2 } from "lucide-react";
import { SourceFile } from "@/autodraft/types";
import { TrashIcon } from "@radix-ui/react-icons";
import { toast } from "@/hooks/use-toast";
import { useState } from "react";

interface FileCardProps {
  file: SourceFile;
  onDelete: (fileID: string) => void;
}
const FileCard = ({ file, onDelete }: FileCardProps) => {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      await onDelete(file.id);
    } catch (error) {
      console.error("Error deleting file:", error);
      setIsDeleting(false);
      toast({
        title: "Error deleting file",
        description:
          error instanceof Error ? error.message : "An unknown error occurred",
        variant: "destructive",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Card key={file.id} className="flex flex-col truncate">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="truncate flex-grow">{file.name}</CardTitle>
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 ml-2 flex-shrink-0"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <TrashIcon className="h-4 w-4" />
            )}
          </Button>
        </div>
        <CardDescription>{file.created_at}</CardDescription>
      </CardHeader>
      <CardContent className="flex items-center justify-center">
        <FileIcon className="w-10 h-10" />
      </CardContent>
    </Card>
  );
};

export default FileCard;
