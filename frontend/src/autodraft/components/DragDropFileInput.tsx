import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { UploadIcon } from "@radix-ui/react-icons";
import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface DragDropFileInputProps {
  onFileChange: (files: FileList) => void;
  isUploading?: boolean;
  uploadProgress?: number;
}

const DragDropFileInput: React.FC<DragDropFileInputProps> = ({
  onFileChange,
  isUploading,
  uploadProgress,
}) => {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const fileList = Object.assign(acceptedFiles, {
        item: (index: number) => acceptedFiles[index],
        length: acceptedFiles.length,
      }) as unknown as FileList;
      onFileChange(fileList);
    },
    [onFileChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div
      {...getRootProps()}
      className={`p-6 border-2 border-dashed rounded-lg text-center cursor-pointer ${
        isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300"
      }`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center">
        {isUploading ? (
          <>
            <Loader2 className="w-20 h-20 mb-4 animate-spin" />
            {uploadProgress !== undefined && (
              <>
                {uploadProgress < 0.99 && (
                  <Progress
                    value={uploadProgress * 100}
                    className="w-full mt-2"
                  />
                )}
              </>
            )}
          </>
        ) : (
          <UploadIcon className="w-20 h-20 mb-4" />
        )}
        <Label className="text-xl mb-0">
          {isUploading
            ? uploadProgress !== undefined && uploadProgress >= 0.99
              ? "Updating Index..."
              : "Uploading..."
            : "Drag and drop files here"}
        </Label>
        {!isUploading && (
          <Label className="text-sm mb-0 text-muted-foreground">
            (or click to select files)
          </Label>
        )}
      </div>
    </div>
  );
};

export default DragDropFileInput;

{
  /* <div className="flex flex-col items-center gap-4">
        {uploading ? (
          <Loader2 className="w-20 h-20 animate-spin" />
        ) : (
          
        )}
      </div> */
}
