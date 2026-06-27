from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import Dict, List, Tuple


class AIMatchingEngine:
    """AI-based job matching engine"""
    
    @staticmethod
    def calculate_match_score(
        resume_text: str,
        job_description: str,
        user_skills: List[str],
        required_skills: List[str]
    ) -> Dict:
        """
        Calculate match score between resume and job
        
        Returns:
        {
            overall_score: float (0-100),
            skills_match: Dict[skill: percentage],
            missing_skills: List[str],
            strength_areas: List[str],
            weak_areas: List[str],
            explanation: str
        }
        """
        
        # Clean texts
        resume_cleaned = AIMatchingEngine._clean_text(resume_text)
        job_cleaned = AIMatchingEngine._clean_text(job_description)
        
        # Calculate text similarity
        text_similarity = AIMatchingEngine._calculate_text_similarity(resume_cleaned, job_cleaned)
        
        # Calculate skills match
        skills_match_result = AIMatchingEngine._calculate_skills_match(user_skills, required_skills)
        
        # Calculate overall score (weighted average)
        overall_score = (text_similarity * 0.4) + (skills_match_result["match_percentage"] * 0.6)
        overall_score = round(overall_score, 2)
        
        # Extract strength and weak areas
        strength_areas, weak_areas = AIMatchingEngine._extract_areas(
            resume_cleaned, job_cleaned, required_skills, user_skills
        )
        
        # Generate explanation
        explanation = AIMatchingEngine._generate_explanation(
            overall_score, skills_match_result, strength_areas, weak_areas
        )
        
        return {
            "overall_score": overall_score,
            "skills_match": skills_match_result["match_dict"],
            "missing_skills": skills_match_result["missing_skills"],
            "strength_areas": strength_areas[:3],  # Top 3
            "weak_areas": weak_areas[:3],  # Top 3
            "explanation": explanation
        }
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def _calculate_text_similarity(resume: str, job_desc: str) -> float:
        """Calculate cosine similarity between resume and job description"""
        try:
            vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
            vectors = vectorizer.fit_transform([resume, job_desc])
            similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
            return float(similarity) * 100
        except:
            return 0.0
    
    @staticmethod
    def _calculate_skills_match(user_skills: List[str], required_skills: List[str]) -> Dict:
        """Calculate skills match percentage"""
        if not required_skills:
            return {
                "match_percentage": 100,
                "match_dict": {},
                "missing_skills": []
            }
        
        user_skills_lower = [s.lower().strip() for s in user_skills]
        required_skills_lower = [s.lower().strip() for s in required_skills]
        
        matched_skills = []
        match_dict = {}
        
        for req_skill in required_skills_lower:
            # Exact match
            if req_skill in user_skills_lower:
                matched_skills.append(req_skill)
                match_dict[req_skill] = 100
            else:
                # Partial match
                for user_skill in user_skills_lower:
                    similarity = AIMatchingEngine._string_similarity(req_skill, user_skill)
                    if similarity > 0.7:
                        matched_skills.append(req_skill)
                        match_dict[req_skill] = int(similarity * 100)
                        break
        
        matched_count = len(set(matched_skills))
        match_percentage = (matched_count / len(required_skills_lower)) * 100 if required_skills_lower else 0
        
        missing_skills = [s for s in required_skills_lower if s not in match_dict]
        
        return {
            "match_percentage": match_percentage,
            "match_dict": match_dict,
            "missing_skills": missing_skills
        }
    
    @staticmethod
    def _string_similarity(s1: str, s2: str) -> float:
        """Calculate similarity between two strings using Levenshtein-like approach"""
        longer = s1 if len(s1) > len(s2) else s2
        shorter = s2 if longer == s1 else s1
        
        if len(longer) == 0:
            return 1.0
        
        edit_distance = AIMatchingEngine._levenshtein(longer, shorter)
        return (len(longer) - edit_distance) / len(longer)
    
    @staticmethod
    def _levenshtein(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance"""
        if len(s1) < len(s2):
            return AIMatchingEngine._levenshtein(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def _extract_areas(resume: str, job_desc: str, required_skills: List[str], user_skills: List[str]) -> Tuple[List[str], List[str]]:
        """Extract strength and weak areas"""
        resume_words = set(resume.split())
        job_words = set(job_desc.split())
        
        # Strength areas: words in both
        strength = list(resume_words & job_words)[:3]
        
        # Weak areas: words in job but not in resume
        weak = list(job_words - resume_words)[:3]
        
        return strength, weak
    
    @staticmethod
    def _generate_explanation(score: float, skills_match: Dict, strength: List[str], weak: List[str]) -> str:
        """Generate human-readable explanation"""
        if score >= 80:
            rating = "Excellent match"
        elif score >= 60:
            rating = "Good match"
        elif score >= 40:
            rating = "Fair match"
        else:
            rating = "Below average match"
        
        matched = len(skills_match["match_dict"])
        total = matched + len(skills_match["missing_skills"])
        
        explanation = f"{rating} ({score}%). "
        explanation += f"You have {matched} out of {total} required skills. "
        
        if skills_match["missing_skills"]:
            explanation += f"Missing skills: {', '.join(skills_match['missing_skills'][:2])}. "
        
        explanation += "Review the job description for more details."
        
        return explanation