"""
Resume Parser Service

Extracts and parses information from PDF resumes.
"""

import PyPDF2
import io
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Service for extracting and parsing resume data from PDF files.
    """
    
    # Common technical skills to look for
    TECH_SKILLS = [
        # Programming Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'go', 
        'rust', 'php', 'swift', 'kotlin', 'scala', 'r', 'matlab',
        # Web Technologies
        'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django',
        'flask', 'fastapi', 'spring', 'rails', 'laravel', 'next.js', 'nuxt',
        # Databases
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
        'oracle', 'sqlite', 'dynamodb', 'cassandra',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
        'ansible', 'ci/cd', 'git', 'github', 'gitlab', 'linux',
        # Data Science & ML
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras',
        'pandas', 'numpy', 'scikit-learn', 'nltk', 'opencv',
        # Others
        'rest api', 'graphql', 'microservices', 'agile', 'scrum', 'jira'
    ]
    
    # Education keywords
    EDUCATION_KEYWORDS = [
        'bachelor', 'master', 'phd', 'b.tech', 'b.e.', 'm.tech', 'm.e.',
        'b.sc', 'm.sc', 'bca', 'mca', 'mba', 'diploma', 'degree',
        'university', 'college', 'institute', 'school'
    ]
    
    # Experience keywords
    EXPERIENCE_KEYWORDS = [
        'experience', 'work history', 'employment', 'career', 'professional',
        'internship', 'intern', 'developer', 'engineer', 'analyst', 'manager',
        'lead', 'senior', 'junior', 'associate'
    ]

    def extract_text_from_pdf(self, file) -> str:
        """
        Extract raw text from a PDF file.
        
        Args:
            file: File object or file path
            
        Returns:
            Extracted text as string
        """
        try:
            # Handle both file objects and file paths
            if hasattr(file, 'read'):
                pdf_file = file
            else:
                pdf_file = open(file, 'rb')
            
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []
            
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            
            full_text = "\n".join(text_parts)
            
            # Clean up the text
            full_text = self._clean_text(full_text)
            
            return full_text
            
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep common punctuation
        text = re.sub(r'[^\w\s\.\,\-\@\:\;\(\)\[\]\/\+\#]', '', text)
        return text.strip()

    def parse_skills(self, text: str) -> list:
        """
        Extract technical skills from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of identified skills
        """
        text_lower = text.lower()
        found_skills = []
        
        for skill in self.TECH_SKILLS:
            # Use word boundaries for accurate matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill.title() if len(skill) > 3 else skill.upper())
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found_skills))

    def parse_experience(self, text: str) -> list:
        """
        Extract work experience from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of experience entries
        """
        experience_entries = []
        text_lower = text.lower()
        
        # Common job title patterns
        job_patterns = [
            r'(software|senior|junior|lead|principal|staff)?\s*(developer|engineer|architect|analyst|manager|intern)',
            r'(full[- ]?stack|front[- ]?end|back[- ]?end|devops|data|ml|ai)\s*(developer|engineer)',
        ]
        
        # Duration patterns
        duration_patterns = [
            r'(\d{4})\s*[-–]\s*(present|\d{4})',
            r'(\d+)\s*(year|month)s?\s*(experience)?',
        ]
        
        # Find job titles
        for pattern in job_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    title = ' '.join([m for m in match if m]).strip().title()
                else:
                    title = match.title()
                if title and len(title) > 3:
                    experience_entries.append({
                        "title": title,
                        "company": "Company",
                        "duration": "Experience",
                        "highlights": []
                    })
        
        # Deduplicate by title
        seen_titles = set()
        unique_entries = []
        for entry in experience_entries:
            if entry['title'] not in seen_titles:
                seen_titles.add(entry['title'])
                unique_entries.append(entry)
        
        return unique_entries[:5]  # Limit to 5 entries

    def parse_education(self, text: str) -> list:
        """
        Extract education information from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of education entries
        """
        education_entries = []
        text_lower = text.lower()
        
        # Degree patterns
        degree_patterns = [
            r"(bachelor'?s?|master'?s?|phd|doctorate|b\.?tech|m\.?tech|b\.?e\.?|m\.?e\.?|b\.?sc|m\.?sc|bca|mca|mba)\s*(of|in)?\s*(\w+\s*\w*)?",
        ]
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    degree = ' '.join([m for m in match if m]).strip()
                else:
                    degree = match
                
                if degree and len(degree) > 2:
                    education_entries.append({
                        "degree": degree.title(),
                        "institution": "University",
                        "year": ""
                    })
        
        # Deduplicate
        seen_degrees = set()
        unique_entries = []
        for entry in education_entries:
            if entry['degree'] not in seen_degrees:
                seen_degrees.add(entry['degree'])
                unique_entries.append(entry)
        
        return unique_entries[:3]  # Limit to 3 entries

    def parse_projects(self, text: str) -> list:
        """
        Extract project information from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of project entries
        """
        projects = []
        
        # Look for project section
        project_section_pattern = r'projects?\s*[:.]?\s*([\s\S]*?)(?=experience|education|skills|$)'
        match = re.search(project_section_pattern, text.lower())
        
        if match:
            project_text = match.group(1)
            # Split by common delimiters
            project_items = re.split(r'\n\s*[-•]\s*|\n\d+[\.\)]\s*', project_text)
            
            for item in project_items[:5]:
                if len(item.strip()) > 10:
                    projects.append({
                        "name": item.strip()[:50],
                        "description": item.strip()[:200],
                        "technologies": self.parse_skills(item)[:5]
                    })
        
        return projects

    def create_resume_summary(self, text: str) -> dict:
        """
        Create a complete summary of the resume.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary with all parsed information
        """
        return {
            "raw_text": text,
            "skills": self.parse_skills(text),
            "experience": self.parse_experience(text),
            "education": self.parse_education(text),
            "projects": self.parse_projects(text),
            "is_parsed": True
        }

    def get_context_for_interview(self, resume_data: dict) -> str:
        """
        Create a context string for interview question generation.
        
        Args:
            resume_data: Parsed resume dictionary
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        if resume_data.get('skills'):
            context_parts.append(f"Skills: {', '.join(resume_data['skills'][:10])}")
        
        if resume_data.get('experience'):
            exp_titles = [e.get('title', '') for e in resume_data['experience'] if e.get('title')]
            if exp_titles:
                context_parts.append(f"Experience: {', '.join(exp_titles[:3])}")
        
        if resume_data.get('education'):
            edu_degrees = [e.get('degree', '') for e in resume_data['education'] if e.get('degree')]
            if edu_degrees:
                context_parts.append(f"Education: {', '.join(edu_degrees[:2])}")
        
        if resume_data.get('projects'):
            proj_names = [p.get('name', '') for p in resume_data['projects'] if p.get('name')]
            if proj_names:
                context_parts.append(f"Projects: {', '.join(proj_names[:3])}")
        
        return ". ".join(context_parts) if context_parts else "General candidate"
