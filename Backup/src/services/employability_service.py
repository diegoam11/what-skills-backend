from typing import List
from ..models.user import EmployabilityData, EmployabilityScore, Skill, Experience, Education
from datetime import datetime


class EmployabilityCalculator:
    """Service to calculate employability scores based on user data"""
    
    def calculate_score(self, data: EmployabilityData) -> EmployabilityScore:
        """Calculate overall employability score"""
        technical_score = self._calculate_technical_score(data.skills)
        experience_score = self._calculate_experience_score(data.experiences)
        education_score = self._calculate_education_score(data.education)
        soft_skills_score = self._calculate_soft_skills_score(data.skills)
        
        # Weighted average (adjust weights as needed)
        overall_score = (
            technical_score * 0.35 +
            experience_score * 0.30 +
            education_score * 0.20 +
            soft_skills_score * 0.15
        )
        
        return EmployabilityScore(
            user_id=data.user_id,
            overall_score=min(100.0, overall_score),
            technical_score=technical_score,
            experience_score=experience_score,
            education_score=education_score,
            soft_skills_score=soft_skills_score
        )
    
    def _calculate_technical_score(self, skills: List[Skill]) -> float:
        """Calculate technical skills score (0-100)"""
        if not skills:
            return 0.0
        
        technical_skills = [s for s in skills if s.category == "technical"]
        if not technical_skills:
            return 0.0
        
        # Calculate average proficiency and apply multipliers
        avg_proficiency = sum(skill.proficiency for skill in technical_skills) / len(technical_skills)
        skill_count_bonus = min(len(technical_skills) * 2, 20)  # Max 20 points for having many skills
        
        base_score = (avg_proficiency / 5.0) * 80  # 80% from proficiency
        final_score = base_score + skill_count_bonus
        
        return min(100.0, final_score)
    
    def _calculate_experience_score(self, experiences: List[Experience]) -> float:
        """Calculate work experience score (0-100)"""
        if not experiences:
            return 0.0
        
        total_months = sum(exp.duration_months for exp in experiences)
        experience_count = len(experiences)
        
        # Score based on total experience (2+ years = high score)
        months_score = min(total_months / 24.0, 1.0) * 70  # Max 70 points for 2+ years
        
        # Bonus for multiple experiences (shows versatility)
        variety_bonus = min(experience_count * 5, 20)  # Max 20 points
        
        # Bonus for detailed descriptions
        detail_bonus = sum(5 if len(exp.description) > 100 else 2 for exp in experiences)
        detail_bonus = min(detail_bonus, 10)  # Max 10 points
        
        return min(100.0, months_score + variety_bonus + detail_bonus)
    
    def _calculate_education_score(self, education: List[Education]) -> float:
        """Calculate education score (0-100)"""
        if not education:
            return 0.0
        
        base_score = 60.0  # Base score for having education
        
        # GPA bonus
        gpa_scores = [edu.gpa for edu in education if edu.gpa is not None]
        if gpa_scores:
            avg_gpa = sum(gpa_scores) / len(gpa_scores)
            gpa_bonus = (avg_gpa / 4.0) * 30  # Max 30 points for perfect GPA
            base_score += gpa_bonus
        
        # Multiple degrees bonus
        if len(education) > 1:
            base_score += 10
        
        return min(100.0, base_score)
    
    def _calculate_soft_skills_score(self, skills: List[Skill]) -> float:
        """Calculate soft skills score (0-100)"""
        if not skills:
            return 0.0
        
        soft_skills = [s for s in skills if s.category == "soft"]
        language_skills = [s for s in skills if s.category == "language"]
        
        if not soft_skills and not language_skills:
            return 0.0
        
        # Soft skills component
        soft_score = 0.0
        if soft_skills:
            avg_soft_proficiency = sum(skill.proficiency for skill in soft_skills) / len(soft_skills)
            soft_score = (avg_soft_proficiency / 5.0) * 60  # Max 60 points
        
        # Language skills component
        language_score = 0.0
        if language_skills:
            language_count = len(language_skills)
            language_score = min(language_count * 10, 40)  # Max 40 points for multiple languages
        
        return min(100.0, soft_score + language_score)


# Sample data generator for testing
def generate_sample_employability_data(user_id) -> EmployabilityData:
    """Generate sample employability data for testing"""
    sample_skills = [
        Skill(name="Python", category="technical", proficiency=4),
        Skill(name="JavaScript", category="technical", proficiency=3),
        Skill(name="React", category="technical", proficiency=3),
        Skill(name="Communication", category="soft", proficiency=4),
        Skill(name="Teamwork", category="soft", proficiency=5),
        Skill(name="English", category="language", proficiency=4),
        Skill(name="Spanish", category="language", proficiency=5),
    ]
    
    sample_experiences = [
        Experience(
            title="Frontend Developer Intern",
            company="Tech Startup",
            duration_months=6,
            description="Developed React components and implemented responsive designs for web applications. Collaborated with UX team to improve user experience.",
            skills_used=["React", "JavaScript", "CSS"]
        ),
        Experience(
            title="Freelance Web Developer",
            company="Self-employed",
            duration_months=12,
            description="Built websites for small businesses using modern web technologies. Managed client relationships and project timelines.",
            skills_used=["Python", "JavaScript", "Communication"]
        )
    ]
    
    sample_education = [
        Education(
            degree="Computer Science",
            institution="Universidad Nacional Mayor de San Marcos",
            gpa=3.7,
            graduation_year=2025
        )
    ]
    
    return EmployabilityData(
        user_id=user_id,
        skills=sample_skills,
        experiences=sample_experiences,
        education=sample_education,
        projects=["E-commerce website", "Task management app", "Data visualization dashboard"],
        certifications=["AWS Cloud Practitioner", "Google Analytics"],
        languages=["Spanish (Native)", "English (Advanced)", "Portuguese (Intermediate)"]
    )