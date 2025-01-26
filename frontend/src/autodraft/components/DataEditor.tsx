import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import FileCard from "./FileCard";
import PlaceholderMessage from "./PlaceholderMessage";
import { ReloadIcon } from "@radix-ui/react-icons";
import { Skeleton } from "@/components/ui/skeleton";
import { SourceFile } from "@/autodraft/types";
import SourceFileUploader from "./SourceFileUploader";
import { deleteFile } from "@/autodraft/services/api";
import { useState } from "react";
import { useWork } from "@/autodraft/WorkContext";

const DataEditor = () => {
  const { selectedProject, availableFiles, setAvailableFiles } = useWork();

  const [uploading, setUploading] = useState<boolean>(false);
  const [creatingIndex] = useState<boolean>(false);

  // const handleCreateIndex = () => {
  //   if (!selectedProject) {
  //     return;
  //   }
  //   setCreatingIndex(true);
  //   const createIndexWithConfirmation = () => {
  //     createIndex(selectedProject.id)
  //       .then(() => {
  //         console.log("Index created");
  //       })
  //       .catch((error) => {
  //         if (error.response && error.response.status === 409) {
  //           const overwrite = window.confirm(
  //             "Index already exists. Do you want to overwrite it?"
  //           );
  //           if (overwrite) {
  //             // First, delete the existing index
  //             deleteIndex(selectedProject.id)
  //               .then(() => {
  //                 return createIndex(selectedProject.id);
  //               })
  //               .then(() => {
  //                 console.log("Index overwritten and recreated");
  //               })
  //               .catch((error) => {
  //                 console.error("Error overwriting index:", error);
  //               });
  //           }
  //         } else {
  //           console.error("Error creating index:", error);
  //         }
  //       })
  //       .finally(() => {
  //         setCreatingIndex(false);
  //         setSelectedProject((prevProject) => {
  //           if (!prevProject) return null;
  //           return {
  //             ...prevProject,
  //             index_available: true,
  //           };
  //         });
  //       });
  //   };

  //   createIndexWithConfirmation();
  // };

  const handleDeleteFile = async (fileId: string): Promise<void> => {
    try {
      await deleteFile(fileId);
      setAvailableFiles((prevFiles) =>
        prevFiles.filter((file) => file.id !== fileId)
      );
    } catch (error) {
      console.error("Error deleting file:", error);
      // Optionally, you could re-throw the error here if you want to handle it in the FileCard component
      throw error;
    }
  };

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

  return (
    <div className="p-4">
      <div className="flex flex-col gap-4">
        <div className="flex flex-row gap-4 justify-between">
          <SourceFileUploader
            projectID={selectedProject?.id}
            setAvailableFiles={setAvailableFiles}
            setUploading={setUploading}
            updateIndexOnUpload={true}
            uploading={uploading}
          />
          <div>
            {creatingIndex ? (
              <Button disabled>
                <ReloadIcon className="mr-2 h-4 w-4 animate-spin" />
                Creating Index
              </Button>
            ) : (
              // <Button
              //   onClick={handleCreateIndex}
              //   disabled={availableFiles.length === 0}
              // >
              //   Create Index
              // </Button>
              <></>
            )}
          </div>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">Source Files</h2>
          <div className="grid grid-cols-4 gap-4">
            {availableFiles.map((file: SourceFile) => (
              <FileCard key={file.id} file={file} onDelete={handleDeleteFile} />
            ))}
            {uploading && (
              <Card>
                <Skeleton className="h-5 grow m-2" />
                <Skeleton className="h-5 grow m-2 mr-10" />
                <div className="flex items-center justify-center h-20">
                  <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-gray-900"></div>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataEditor;
