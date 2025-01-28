import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";

import { Button } from "@/components/ui/button";
import DragDropFileInput from "@/autodraft/components/DragDropFileInput";
import { uploadTemplate } from "@/autodraft/services/api";
import { useState } from "react";

export default function TemplateUploader({
  projectID,
  reportID,
  onUploadSuccess,
}: {
  projectID: string;
  reportID: string;
  onUploadSuccess?: () => void;
}) {
  //TODO: a lot of overlap with SourceFileUploader...
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [fileProgress] = useState<number | null>(null);
  const [drawerOpen, setDrawerOpen] = useState<boolean>(false);
  const [uploading, setUploading] = useState<boolean>(false);

  const handleFileUpload = async (files: FileList) => {
    if (files.length !== 1) {
      setErrorMessage("Please select only one file to upload.");
      return;
    }

    if (!reportID) {
      setErrorMessage("No report selected.");
      return;
    }

    if (!projectID) {
      setErrorMessage("No project selected.");
      return;
    }

    setUploading(true);
    try {
      console.log("Uploading template...");
      console.log(files[0]);
      await uploadTemplate(files[0], projectID, reportID);
      setSuccessMessage("Template uploaded successfully");
      if (onUploadSuccess) {
        onUploadSuccess();
      }
      setErrorMessage(null);
      setDrawerOpen(false);
    } catch (error) {
      setErrorMessage("Error uploading template.");
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <Drawer open={drawerOpen} onOpenChange={setDrawerOpen}>
      <DrawerTrigger asChild>
        <Button onClick={() => setDrawerOpen(true)}>Upload Template</Button>
      </DrawerTrigger>
      <DrawerContent className="mx-auto w-full max-w-6xl">
        <DrawerHeader>
          <DrawerTitle className="text-5xl">Upload Template</DrawerTitle>
          <DrawerDescription className="text-xl">
            <div className="mb-2 text-2xl">
              Upload a document with the structure you want to use for your
              report.
            </div>
            <div className="text-lg text-muted-foreground italic">
              (This will overwrite all existing prompts in this report)
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
