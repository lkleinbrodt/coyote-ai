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
  const [error, setError] = useState<string | null>(null);
  const [streamsCompleted, setStreamsCompleted] = useState<number>(0);
  const [streamsErrored, setStreamsErrored] = useState<number>(0);
  const [totalStreams, setTotalStreams] = useState<number>(0);

  // Handle input change
  const handleTopicChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTopic(e.target.value);
    // Clear any previous errors when user starts typing
    if (error) setError(null);
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

    const levels: ExplanationLevel[] = [
      "child",
      "student",
      "professional",
      "expert",
    ];
    setStreamsCompleted(0);
    setStreamsErrored(0);
    setTotalStreams(levels.length);

    // Start all streams concurrently
    const streamPromises = levels.map((level) => {
      return streamExplanation(
        topic,
        level,
        (content) => {
          setExplanations((prev) => {
            const newText = prev[level] + content;
            return {
              ...prev,
              [level]: newText,
            };
          });
        },
        () => {
          setStreamsCompleted((prev) => prev + 1);
          if (streamsCompleted + streamsErrored === totalStreams) {
            setIsLoading(false);
          }
        },
        (errorMessage) => {
          setStreamsErrored((prev) => prev + 1);
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
          if (streamsCompleted + streamsErrored === totalStreams) {
            setIsLoading(false);
          }
        }
      ).catch((err) => {
        console.error(`Error in ${level} stream:`, err);
        setStreamsErrored((prev) => prev + 1);
        if (streamsCompleted + streamsErrored === totalStreams) {
          setIsLoading(false);
        }
      });
    });

    try {
      await Promise.all(streamPromises);
    } catch (error) {
      console.error("Error in explanation streams:", error);
      toast({
        title: "Error",
        description: "An unexpected error occurred",
        variant: "destructive",
      });
      setIsLoading(false);
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
        <ExplanationCard title="Curious Child" content={explanations.child} />
        <ExplanationCard title="Student" content={explanations.student} />
        <ExplanationCard
          title="Professional"
          content={explanations.professional}
        />
        <ExplanationCard
          title="World-Class Expert"
          content={explanations.expert}
        />
      </div>
    </div>
  );
};

export default ExplainPage;
