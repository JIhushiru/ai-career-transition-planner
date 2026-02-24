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
  events: string[];
}

export interface ResumeUploadResponse {
  user_id: number;
  resume_id: number;
  raw_text: string;
  skills: ExtractedSkill[];
  parsed_sections: ParsedSections;
}

export interface SkillsResponse {
  skills: ExtractedSkill[];
  categories: Record<string, ExtractedSkill[]>;
}

export interface ResumeListItem {
  id: number;
  filename: string | null;
  source_type: string;
  created_at: string;
  skill_count: number;
}

export interface ResumeListResponse {
  resumes: ResumeListItem[];
}

export interface SessionResponse {
  session_id: string;
  user_id: number;
}
