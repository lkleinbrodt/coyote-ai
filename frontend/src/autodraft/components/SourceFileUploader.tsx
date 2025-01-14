import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { updateOrCreateIndex, uploadFile } from "@/autodraft/services/api";

import { Button } from "@/components/ui/button";
import DragDropFileInput from "@/autodraft/components/DragDropFileInput";
import { SourceFile } from "@/autodraft/types";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

export default function SourceFileUploader({
  projectID,
  setAvailableFiles,
  uploading,
  setUploading,
  updateIndexOnUpload,
}: {
  projectID: string;
  setAvailableFiles: React.Dispatch<React.SetStateAction<SourceFile[]>>;
  setUploading: React.Dispatch<React.SetStateAction<boolean>>;
  updateIndexOnUpload: boolean;
  uploading: boolean;
}) {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [fileProgress, setFileProgress] = useState<number | null>(null);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);
  const { toast } = useToast();

  const handleFileUpload = async (files: FileList) => {
    if (!files || files.length === 0) {
      setErrorMessage("Please select at least one file to upload.");
      return;
    }
    setUploading(true);
    setFileProgress(0);

    const uploadPromises = Array.from(files).map((file) =>
      uploadFile(file, projectID)
        .then((result) => {
          setFileProgress((prev) => (prev || 0) + 1 / files.length);
          return result;
        })
        .catch((error) => {
          if (error.response && error.response.status === 409) {
            const overwrite = window.confirm(
              `File ${file.name} already exists. Do you want to overwrite it?`
            );
            if (overwrite) {
              return uploadFile(file, projectID, true).then((result) => {
                setFileProgress((prev) => (prev || 0) + 1 / files.length);
                return result;
              });
            }
            throw new Error("Upload cancelled");
          }
          throw error;
        })
    );

    Promise.all(uploadPromises)
      .then((uploadedFiles) => {
        setSuccessMessage(
          `${uploadedFiles.length} file(s) uploaded successfully`
        );
        setErrorMessage(null);
        setAvailableFiles((prevFiles) => {
          const newFiles = [...prevFiles];
          uploadedFiles.forEach((file) => {
            const index = newFiles.findIndex((f) => f.name === file.name);
            if (index !== -1) {
              newFiles[index] = file;
            } else {
              newFiles.push(file);
            }
          });
          return newFiles;
        });
      })
      .catch((error) => {
        setErrorMessage("An error occurred while uploading one or more files.");
        console.error("Error uploading files:", error);
      })
      .then(() => {
        if (updateIndexOnUpload) {
          updateOrCreateIndex(projectID);
        }
      })
      .finally(() => {
        setUploading(false);
        setDrawerOpen(false);
        toast({
          title: "Files uploaded successfully",
        });
      });
  };

  return (
    <Drawer open={drawerOpen} onOpenChange={setDrawerOpen}>
      <DrawerTrigger>
        <Button onClick={() => setDrawerOpen(true)}>Upload Sources</Button>
      </DrawerTrigger>
      <DrawerContent className="mx-auto w-full max-w-6xl">
        <DrawerHeader>
          <DrawerTitle className="text-5xl">Upload Sources</DrawerTitle>
          <DrawerDescription className="text-xl">
            <div>
              Sources let AutoDraft base its answers on specific documents (like
              project updates, annual reports, financial statements, etc.)
            </div>
          </DrawerDescription>
        </DrawerHeader>
        <div className="flex flex-col gap-4 items-center p-4">
          <div className="w-full max-w-2xl">
            <DragDropFileInput
              onFileChange={handleFileUpload}
              isUploading={uploading}
              uploadProgress={fileProgress ?? undefined}
            />
            {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
            {successMessage && (
              <p style={{ color: "green" }}>{successMessage}</p>
            )}
          </div>
        </div>
        <DrawerFooter></DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}
