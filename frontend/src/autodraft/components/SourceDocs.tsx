import * as React from "react";

import { Card, CardContent } from "@/components/ui/card";

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
    <Card>
      <CardContent className="pt-4">
        <h4 className="text-sm font-semibol">{sourceDocs.length} Sources:</h4>
        <ul className="text-sm text-muted-foreground ">
          {Object.entries(groupedDocs).map(([fileName, docs]) => (
            <li key={fileName} className="mr-4 ml-4">
              {docs.map((doc, index) => (
                <React.Fragment key={doc.id}>
                  {index > 0 && ", "}
                  <DocTooltip document={doc}>
                    <span className="cursor-all-scroll underline decoration-dotted">
                      {doc.id}
                    </span>
                  </DocTooltip>
                </React.Fragment>
              ))}{" "}
              ({fileName})
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
};

export default SourceDocs;
