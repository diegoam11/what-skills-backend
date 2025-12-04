from typing import List
from ..models.user import Recommendation, EmployabilityScore, EmployabilityData
from datetime import datetime


class RecommendationService:
    """Service to generate personalized recommendations based on employability data"""
    
    def generate_recommendations(
        self, 
        user_id, 
        employability_data: EmployabilityData, 
        employability_score: EmployabilityScore
    ) -> List[Recommendation]:
        """Generate personalized recommendations for a user"""
        recommendations = []
        
        # Skill-based recommendations
        recommendations.extend(self._get_skill_recommendations(user_id, employability_data, employability_score))
        
        # Experience-based recommendations
        recommendations.extend(self._get_experience_recommendations(user_id, employability_data, employability_score))
        
        # Education-based recommendations
        recommendations.extend(self._get_education_recommendations(user_id, employability_data, employability_score))
        
        # Networking recommendations
        recommendations.extend(self._get_networking_recommendations(user_id, employability_data))
        
        # Sort by priority and estimated impact
        recommendations.sort(key=lambda x: (x.priority, -x.estimated_impact))
        
        return recommendations[:10]  # Return top 10 recommendations
    
    def _get_skill_recommendations(self, user_id, data: EmployabilityData, score: EmployabilityScore) -> List[Recommendation]:
        """Generate skill-related recommendations"""
        recommendations = []
        
        # Check if user lacks certain high-demand technical skills
        current_skills = [skill.name.lower() for skill in data.skills if skill.category == "technical"]
        
        high_demand_skills = {
            "python": {"impact": 8.5, "courses": ["Python for Data Science", "Advanced Python Programming"]},
            "react": {"impact": 7.5, "courses": ["React Fundamentals", "Advanced React Patterns"]},
            "node.js": {"impact": 7.0, "courses": ["Node.js Backend Development", "Express.js Mastery"]},
            "sql": {"impact": 8.0, "courses": ["SQL for Data Analysis", "Database Design"]},
            "docker": {"impact": 6.5, "courses": ["Docker Fundamentals", "Container Orchestration"]},
            "aws": {"impact": 9.0, "courses": ["AWS Cloud Practitioner", "AWS Solutions Architect"]},
            "machine learning": {"impact": 9.5, "courses": ["ML Fundamentals", "Deep Learning with TensorFlow"]},
        }
        
        for skill, info in high_demand_skills.items():
            if skill not in current_skills:
                recommendations.append(Recommendation(
                    user_id=user_id,
                    type="skill",
                    title=f"Learn {skill.title()}",
                    description=f"Adding {skill} skills could significantly boost your employability. Consider taking: {', '.join(info['courses'])}",
                    priority=1 if info["impact"] > 8.0 else 2,
                    category="Technical Skills",
                    estimated_impact=info["impact"]
                ))
        
        # Recommend improving existing skills with low proficiency
        low_proficiency_skills = [skill for skill in data.skills if skill.proficiency <= 2]
        for skill in low_proficiency_skills[:3]:  # Top 3 skills to improve
            recommendations.append(Recommendation(
                user_id=user_id,
                type="skill",
                title=f"Improve {skill.name} Skills",
                description=f"Your {skill.name} proficiency is {skill.proficiency}/5. Consider advanced courses or practice projects to reach level 4+",
                priority=2,
                category="Skill Enhancement",
                estimated_impact=5.0
            ))
        
        return recommendations
    
    def _get_experience_recommendations(self, user_id, data: EmployabilityData, score: EmployabilityScore) -> List[Recommendation]:
        """Generate experience-related recommendations"""
        recommendations = []
        
        total_experience_months = sum(exp.duration_months for exp in data.experiences)
        
        if total_experience_months < 12:  # Less than 1 year
            recommendations.append(Recommendation(
                user_id=user_id,
                type="job",
                title="Seek Internship Opportunities",
                description="Gain practical experience through internships. Look for part-time or summer internship programs in your field.",
                priority=1,
                category="Experience Building",
                url="https://linkedin.com/jobs",
                estimated_impact=7.5
            ))
            
            recommendations.append(Recommendation(
                user_id=user_id,
                type="job",
                title="Start Freelance Projects",
                description="Build your portfolio and gain real-world experience by taking on small freelance projects.",
                priority=2,
                category="Experience Building",
                url="https://upwork.com",
                estimated_impact=6.0
            ))
        
        elif total_experience_months < 24:  # 1-2 years
            recommendations.append(Recommendation(
                user_id=user_id,
                type="job",
                title="Apply for Junior Positions",
                description="With your current experience, you're ready for junior-level positions. Focus on companies that value growth potential.",
                priority=1,
                category="Career Advancement",
                estimated_impact=8.0
            ))
        
        return recommendations
    
    def _get_education_recommendations(self, user_id, data: EmployabilityData, score: EmployabilityScore) -> List[Recommendation]:
        """Generate education-related recommendations"""
        recommendations = []
        
        # Check if user has certifications
        if len(data.certifications) < 2:
            recommendations.append(Recommendation(
                user_id=user_id,
                type="course",
                title="Obtain Industry Certifications",
                description="Industry certifications validate your skills and improve credibility. Consider AWS, Google Cloud, or Microsoft certifications.",
                priority=2,
                category="Certifications",
                estimated_impact=6.5
            ))
        
        # Recommend online courses based on career field
        if any("computer science" in edu.degree.lower() or "software" in edu.degree.lower() for edu in data.education):
            recommendations.append(Recommendation(
                user_id=user_id,
                type="course",
                title="Advanced Programming Course",
                description="Take advanced courses in algorithms, system design, or specialized frameworks to deepen your technical expertise.",
                priority=3,
                category="Skill Development",
                url="https://coursera.org",
                estimated_impact=5.5
            ))
        
        return recommendations
    
    def _get_networking_recommendations(self, user_id, data: EmployabilityData) -> List[Recommendation]:
        """Generate networking-related recommendations"""
        recommendations = []
        
        recommendations.append(Recommendation(
            user_id=user_id,
            type="networking",
            title="Join Professional Communities",
            description="Connect with professionals in your field through LinkedIn groups, Discord communities, or local meetups.",
            priority=2,
            category="Professional Networking",
            url="https://linkedin.com",
            estimated_impact=4.5
        ))
        
        recommendations.append(Recommendation(
            user_id=user_id,
            type="networking",
            title="Attend Tech Events",
            description="Participate in hackathons, tech conferences, or industry workshops to build your network and learn about opportunities.",
            priority=3,
            category="Professional Development",
            estimated_impact=5.0
        ))
        
        recommendations.append(Recommendation(
            user_id=user_id,
            type="networking",
            title="Build Your Online Presence",
            description="Create a strong GitHub profile, contribute to open source projects, and maintain an updated LinkedIn profile.",
            priority=2,
            category="Personal Branding",
            url="https://github.com",
            estimated_impact=6.0
        ))
        
        return recommendations