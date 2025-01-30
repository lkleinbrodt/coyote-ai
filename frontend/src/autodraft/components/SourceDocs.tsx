import * as React from "react";

import DocTooltip from "./DocTooltip";
import { Document } from "@/autodraft/types";

interface SourceDocsProps {
  sourceDocs: Document[];
}

const SourceDocs: React.FC<SourceDocsProps> = ({ sourceDocs }) => {
  if (!sourceDocs || sourceDocs.length === 0) return null;

  // Group documents by filename
  const groupedDocs = sourceDocs.reduce((acc, doc) => {
    const fileName = doc.file.name;
    if (!acc[fileName]) {
      acc[fileName] = [];
    }
    acc[fileName].push(doc); // Store the entire doc object instead of just the ID
    return acc;
  }, {} as Record<string, Document[]>);

  return (
    <>
      <ol className="text-sm text-muted-foreground list-decimal list-inside ml-0 pl-0">
        {Object.entries(groupedDocs).map(([fileName, docs]) => (
          <li key={fileName} className="">
            {fileName}:
            <ol className="list-disc list-inside ml-0 pl-2">
              {docs.map((doc) => (
                <li key={doc.id}>
                  <DocTooltip document={doc}>
                    <span className="cursor-all-scroll underline decoration-dotted">
                      Page: {doc.page_label}
                    </span>
                  </DocTooltip>
                </li>
              ))}
            </ol>
          </li>
        ))}
      </ol>
    </>
  );
};

export default SourceDocs;
