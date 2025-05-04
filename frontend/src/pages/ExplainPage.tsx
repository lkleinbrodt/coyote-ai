import { ExplanationLevel, streamExplanation } from "../explain/services/api";
import React, { useState } from "react";

import { Button } from "../components/ui/button";
import { ExplanationCard } from "../components/ui/explanation-card";
import { Input } from "../components/ui/input";
import { useToast } from "../hooks/use-toast";

interface Explanations {
  child: string;
  student: string;
  professional: string;
  expert: string;
}

// Status for each explanation
type ExplanationStatus = "waiting" | "loading" | "complete" | "error";

interface ExplanationStatuses {
  child: ExplanationStatus;
  student: ExplanationStatus;
  professional: ExplanationStatus;
  expert: ExplanationStatus;
}

const ExplainPage: React.FC = () => {
  const { toast } = useToast();

  // State variables as per PRD 4.1.4
  const [topic, setTopic] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [explanations, setExplanations] = useState<Explanations>({
    child: "",
    student: "",
    professional: "",
    expert: "",
  });
  const [statuses, setStatuses] = useState<ExplanationStatuses>({
    child: "complete",
    student: "complete",
    professional: "complete",
    expert: "complete",
  });
  const [error, setError] = useState<string | null>(null);
  const [currentLevel, setCurrentLevel] = useState<ExplanationLevel | null>(
    null
  );

  // Handle input change
  const handleTopicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTopic(e.target.value);
    // Clear any previous errors when user starts typing
    if (error) setError(null);
  };

  // Process a single explanation level
  const processLevel = async (level: ExplanationLevel): Promise<boolean> => {
    setCurrentLevel(level);
    setStatuses((prev) => ({
      ...prev,
      [level]: "loading",
    }));

    try {
      await streamExplanation(
        topic,
        level,
        (content) => {
          setExplanations((prev) => ({
            ...prev,
            [level]: prev[level] + content,
          }));
        },
        () => {
          setStatuses((prev) => ({
            ...prev,
            [level]: "complete",
          }));
          return true;
        },
        (errorMessage) => {
          toast({
            title: `Error (${level})`,
            description:
              errorMessage || `Failed to generate ${level} explanation.`,
            variant: "destructive",
          });
          setExplanations((prev) => ({
            ...prev,
            [level]: `Error: ${errorMessage}`,
          }));
          setStatuses((prev) => ({
            ...prev,
            [level]: "error",
          }));
          return false;
        }
      );
      return true;
    } catch (err) {
      console.error(`Error in ${level} stream:`, err);
      setStatuses((prev) => ({
        ...prev,
        [level]: "error",
      }));
      return false;
    }
  };

  // Handle form submission
  const handleExplainSubmit = async () => {
    if (!topic.trim()) {
      setError("Please enter a topic");
      return;
    }

    setIsLoading(true);
    setError(null);
    setExplanations({
      child: "",
      student: "",
      professional: "",
      expert: "",
    });

    // Set all to waiting initially
    setStatuses({
      child: "waiting",
      student: "waiting",
      professional: "waiting",
      expert: "waiting",
    });

    // Process levels sequentially
    const levels: ExplanationLevel[] = [
      "child",
      "student",
      "professional",
      "expert",
    ];

    for (const level of levels) {
      const success = await processLevel(level);
      if (!success) {
        // If one fails, we still continue with the rest
        continue;
      }
    }

    setIsLoading(false);
    setCurrentLevel(null);
  };

  // Get content for display based on status
  const getDisplayContent = (level: ExplanationLevel): string => {
    const status = statuses[level];
    if (status === "waiting") {
      return "Waiting for my turn...";
    } else if (status === "loading" && !explanations[level]) {
      return "Generating explanation...";
    } else if (
      status === "error" &&
      !explanations[level].startsWith("Error:")
    ) {
      return "An error occurred while generating this explanation.";
    } else {
      return explanations[level];
    }
  };

  return (
    <div className="p-1">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center py-10">
          <h1 className="text-4xl sm:text-6xl font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-br from-primary to-secondary pb-1">
            Explain Like I'm ___
          </h1>
          <p className="text-xl sm:text-2xl text-muted-foreground">
            Get explanations at different complexity levels
          </p>
        </div>
      </div>

      {/* Input Section */}
      <div className="max-w-3xl mx-auto px-4 mb-12">
        <div className="flex flex-col sm:flex-row gap-4">
          <Input
            placeholder="Enter a topic..."
            className="flex-1 text-lg"
            value={topic}
            onChange={handleTopicChange}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !isLoading && topic.trim()) {
                handleExplainSubmit();
              }
            }}
            disabled={isLoading}
          />
          <Button
            onClick={handleExplainSubmit}
            disabled={isLoading || !topic.trim()}
            className="text-lg px-8"
          >
            {isLoading ? "Explaining..." : "Explain It!"}
          </Button>
        </div>
        {error && (
          <p className="text-sm text-destructive mt-2 text-center">{error}</p>
        )}
      </div>

      {/* Explanations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 px-4 max-w-7xl mx-auto">
        <ExplanationCard
          title="Curious Child"
          content={getDisplayContent("child")}
          status={statuses.child}
          isActive={currentLevel === "child"}
        />
        <ExplanationCard
          title="Student"
          content={getDisplayContent("student")}
          status={statuses.student}
          isActive={currentLevel === "student"}
        />
        <ExplanationCard
          title="Professional"
          content={getDisplayContent("professional")}
          status={statuses.professional}
          isActive={currentLevel === "professional"}
        />
        <ExplanationCard
          title="World-Class Expert"
          content={getDisplayContent("expert")}
          status={statuses.expert}
          isActive={currentLevel === "expert"}
        />
      </div>
    </div>
  );
};

export default ExplainPage;
