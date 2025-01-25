import * as React from "react";
import * as TooltipPrimitive from "@radix-ui/react-tooltip";

import { Card, CardContent } from "@/components/ui/card";

import { Document } from "@/autodraft/types";

interface DocTooltipProps {
  document: Document;
  children: React.ReactNode;
}

const DocTooltip = ({ document, children }: DocTooltipProps) => {
  return (
    <TooltipPrimitive.Provider>
      <TooltipPrimitive.Root delayDuration={0}>
        <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
        <TooltipPrimitive.Content
          className="z-50 w-[32rem] max-h-[24rem] overflow-y-auto"
          sideOffset={5}
        >
          <Card>
            <CardContent className="p-4 space-y-2">
              <div className="flex items-center space-x-2 border-b pb-2">
                <span className="text-xs text-muted-foreground font-mono">
                  {document.file.name}
                </span>
              </div>
              <div className="text-sm font-mono leading-relaxed">
                <pre className="whitespace-pre-wrap break-words">
                  {document.content}
                </pre>
              </div>
            </CardContent>
          </Card>
          <TooltipPrimitive.Arrow className="fill-background" />
        </TooltipPrimitive.Content>
      </TooltipPrimitive.Root>
    </TooltipPrimitive.Provider>
  );
};

export default DocTooltip;
