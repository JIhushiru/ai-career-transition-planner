"use client";

import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface TextPasteFormProps {
  onSubmit: (text: string) => Promise<void>;
  isLoading: boolean;
}

export function TextPasteForm({ onSubmit, isLoading }: TextPasteFormProps) {
  const [text, setText] = useState("");

  const handleSubmit = () => {
    if (text.trim().length >= 10) {
      onSubmit(text.trim());
    }
  };

  return (
    <div className="space-y-4">
      <Textarea
        placeholder="Paste your resume text here... (minimum 10 characters)"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={12}
        disabled={isLoading}
        className="resize-none font-mono text-sm"
      />
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">
          {text.length} characters
        </span>
        <Button
          onClick={handleSubmit}
          disabled={isLoading || text.trim().length < 10}
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Parsing...
            </>
          ) : (
            "Parse Resume"
          )}
        </Button>
      </div>
    </div>
  );
}
