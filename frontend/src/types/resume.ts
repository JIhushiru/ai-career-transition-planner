export interface ExtractedSkill {
  name: string;
  category: string;
  confidence: number;
  source: string;
}

export interface ParsedSections {
  contact: Record<string, string>;
  summary: string;
  experience: Array<{
    title: string;
    dates: string;
    details: string[];
  }>;
  education: Array<{
    text: string;
  }>;
  skills_section: string[];
}

export interface ResumeUploadResponse {
  resume_id: number;
  raw_text: string;
  skills: ExtractedSkill[];
  parsed_sections: ParsedSections;
}

export interface SkillsResponse {
  skills: ExtractedSkill[];
  categories: Record<string, ExtractedSkill[]>;
}

export interface SessionResponse {
  session_id: string;
  user_id: number;
}
