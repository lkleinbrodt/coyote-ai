import { Card, CardContent, CardHeader, CardTitle } from "./card";

import { ExplanationModal } from "./explanation-modal";
import ReactMarkdown from "react-markdown";
import { useState } from "react";

interface ExplanationCardProps {
  title: string;
  content: string;
  placeholder?: string;
}

export function ExplanationCard({
  title,
  content,
  placeholder = "Enter a topic above to get started!",
}: ExplanationCardProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <>
      <Card
        className="group hover:border-primary/50 transition-all cursor-pointer"
        onClick={() => content && setIsModalOpen(true)}
      >
        <CardHeader>
          <CardTitle className="text-xl">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          {content ? (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <ReactMarkdown>{content}</ReactMarkdown>
            </div>
          ) : (
            <p className="text-muted-foreground text-sm">{placeholder}</p>
          )}
        </CardContent>
      </Card>

      <ExplanationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={title}
        content={content}
      />
    </>
  );
}
