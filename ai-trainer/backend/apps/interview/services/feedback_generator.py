"""
Feedback Generator Service

Generates comprehensive feedback and analytics for interview sessions.
"""

import logging
from typing import List, Dict, Optional
from statistics import mean, stdev

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """
    Service for generating interview feedback and analytics.
    """
    
    # Rating thresholds
    RATING_THRESHOLDS = {
        'excellent': 85,
        'good': 70,
        'average': 50,
        'needs_improvement': 30,
        'poor': 0
    }
    
    # Score weights for different interview types
    SCORE_WEIGHTS = {
        'Technical': {
            'relevance': 0.35,
            'depth': 0.40,
            'clarity': 0.25
        },
        'HR': {
            'relevance': 0.30,
            'depth': 0.25,
            'clarity': 0.45
        },
        'Behavioral': {
            'relevance': 0.35,
            'depth': 0.30,
            'clarity': 0.35
        },
        'Mixed': {
            'relevance': 0.33,
            'depth': 0.34,
            'clarity': 0.33
        }
    }

    def calculate_overall_score(
        self,
        answer_scores: List[Dict],
        interview_type: str = 'Technical'
    ) -> Dict:
        """
        Calculate weighted overall score from individual answer scores.
        
        Args:
            answer_scores: List of answer evaluations
            interview_type: Type of interview
            
        Returns:
            Dictionary with overall and component scores
        """
        if not answer_scores:
            return {
                'overall_score': 0,
                'communication_score': 0,
                'technical_score': 0,
                'confidence_score': 0
            }
        
        weights = self.SCORE_WEIGHTS.get(interview_type, self.SCORE_WEIGHTS['Mixed'])
        
        # Extract individual scores
        relevance_scores = [a.get('relevance_score', 50) for a in answer_scores]
        depth_scores = [a.get('depth_score', 50) for a in answer_scores]
        clarity_scores = [a.get('clarity_score', 50) for a in answer_scores]
        overall_scores = [a.get('score', 50) for a in answer_scores]
        
        # Calculate means
        avg_relevance = mean(relevance_scores) if relevance_scores else 50
        avg_depth = mean(depth_scores) if depth_scores else 50
        avg_clarity = mean(clarity_scores) if clarity_scores else 50
        avg_overall = mean(overall_scores) if overall_scores else 50
        
        # Calculate weighted overall
        weighted_overall = (
            avg_relevance * weights['relevance'] +
            avg_depth * weights['depth'] +
            avg_clarity * weights['clarity']
        )
        
        return {
            'overall_score': round(weighted_overall, 1),
            'communication_score': round(avg_clarity, 1),
            'technical_score': round(avg_depth, 1),
            'confidence_score': round((avg_relevance + avg_clarity) / 2, 1)
        }

    def get_rating(self, score: float) -> str:
        """
        Convert numeric score to rating label.
        
        Args:
            score: Numeric score (0-100)
            
        Returns:
            Rating string
        """
        for rating, threshold in self.RATING_THRESHOLDS.items():
            if score >= threshold:
                return rating
        return 'poor'

    def identify_strengths(self, answer_data: List[Dict]) -> List[str]:
        """
        Identify strengths from answer evaluations.
        
        Args:
            answer_data: List of answer evaluations
            
        Returns:
            List of identified strengths
        """
        all_strengths = []
        
        for answer in answer_data:
            strengths = answer.get('strengths', [])
            all_strengths.extend(strengths)
        
        # Count occurrences and rank
        strength_counts = {}
        for s in all_strengths:
            strength_counts[s] = strength_counts.get(s, 0) + 1
        
        # Sort by frequency and return top strengths
        sorted_strengths = sorted(
            strength_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [s[0] for s in sorted_strengths[:5]]

    def identify_weaknesses(self, answer_data: List[Dict]) -> List[str]:
        """
        Identify weaknesses/improvement areas from answer evaluations.
        
        Args:
            answer_data: List of answer evaluations
            
        Returns:
            List of identified weaknesses
        """
        all_improvements = []
        
        for answer in answer_data:
            improvements = answer.get('improvements', [])
            all_improvements.extend(improvements)
        
        # Count occurrences and rank
        improvement_counts = {}
        for i in all_improvements:
            improvement_counts[i] = improvement_counts.get(i, 0) + 1
        
        # Sort by frequency
        sorted_improvements = sorted(
            improvement_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [i[0] for i in sorted_improvements[:5]]

    def generate_suggestions(
        self,
        weaknesses: List[str],
        interview_type: str,
        overall_score: float
    ) -> List[str]:
        """
        Generate actionable improvement suggestions.
        
        Args:
            weaknesses: Identified weaknesses
            interview_type: Type of interview
            overall_score: Overall score achieved
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Score-based suggestions
        if overall_score < 50:
            suggestions.extend([
                "Practice answering questions out loud to improve fluency",
                "Research common interview questions for your field",
                "Consider taking mock interviews with peers"
            ])
        elif overall_score < 70:
            suggestions.extend([
                "Focus on providing more specific examples",
                "Structure your answers using the STAR method"
            ])
        else:
            suggestions.extend([
                "Keep refining your answers for even more impact",
                "Practice handling unexpected questions"
            ])
        
        # Interview type specific
        if interview_type == 'Technical':
            suggestions.append("Review core concepts and practice coding problems")
        elif interview_type == 'Behavioral':
            suggestions.append("Prepare more STAR method examples from your experience")
        elif interview_type == 'HR':
            suggestions.append("Research the company culture and values")
        
        # Weakness-based suggestions
        if 'examples' in str(weaknesses).lower():
            suggestions.append("Prepare 5-6 specific examples from your experience")
        if 'structure' in str(weaknesses).lower():
            suggestions.append("Practice organizing your thoughts before answering")
        
        return suggestions[:6]

    def calculate_topic_scores(self, questions_answers: List[Dict]) -> Dict[str, float]:
        """
        Calculate scores by topic/category.
        
        Args:
            questions_answers: List of questions with their answers
            
        Returns:
            Dictionary of category -> score
        """
        category_scores = {}
        category_counts = {}
        
        for qa in questions_answers:
            category = qa.get('category', 'general')
            score = qa.get('score', 50)
            
            if category not in category_scores:
                category_scores[category] = 0
                category_counts[category] = 0
            
            category_scores[category] += score
            category_counts[category] += 1
        
        # Calculate averages
        return {
            cat: round(category_scores[cat] / category_counts[cat], 1)
            for cat in category_scores
        }

    def calculate_percentile(
        self,
        current_score: float,
        historical_scores: List[float]
    ) -> float:
        """
        Calculate percentile ranking compared to historical scores.
        
        Args:
            current_score: Current interview score
            historical_scores: List of past scores
            
        Returns:
            Percentile (0-100)
        """
        if not historical_scores:
            return 50.0  # Default to median
        
        scores_below = sum(1 for s in historical_scores if s < current_score)
        percentile = (scores_below / len(historical_scores)) * 100
        
        return round(percentile, 1)

    def get_recommended_resources(
        self,
        weaknesses: List[str],
        interview_type: str
    ) -> List[str]:
        """
        Generate list of recommended learning resources.
        
        Args:
            weaknesses: Identified weaknesses
            interview_type: Type of interview
            
        Returns:
            List of resource recommendations
        """
        resources = []
        
        # General resources
        resources.append("Interview preparation on Pramp or Interviewing.io")
        resources.append("STAR method guide for behavioral questions")
        
        # Type-specific
        if interview_type == 'Technical':
            resources.extend([
                "LeetCode or HackerRank for coding practice",
                "System design resources on Educative.io"
            ])
        elif interview_type == 'HR':
            resources.extend([
                "Common HR interview questions guide",
                "Company research templates"
            ])
        elif interview_type == 'Behavioral':
            resources.extend([
                "Behavioral interview prep on LinkedIn Learning",
                "STAR method examples library"
            ])
        
        return resources[:5]

    def get_practice_areas(
        self,
        topic_scores: Dict[str, float],
        threshold: float = 70
    ) -> List[str]:
        """
        Identify areas that need more practice.
        
        Args:
            topic_scores: Scores by topic
            threshold: Score below which topic needs practice
            
        Returns:
            List of practice areas
        """
        practice_areas = []
        
        for topic, score in topic_scores.items():
            if score < threshold:
                practice_areas.append(f"{topic.replace('_', ' ').title()} (Score: {score})")
        
        if not practice_areas:
            practice_areas.append("Keep practicing all areas to maintain performance")
        
        return practice_areas

    def generate_complete_feedback(
        self,
        session_data: Dict,
        questions_answers: List[Dict]
    ) -> Dict:
        """
        Generate complete feedback for an interview session.
        
        Args:
            session_data: Interview session information
            questions_answers: List of questions with answers and scores
            
        Returns:
            Complete feedback dictionary
        """
        interview_type = session_data.get('interview_type', 'Mixed')
        
        # Calculate scores
        answer_data = [qa.get('answer_data', {}) for qa in questions_answers]
        scores = self.calculate_overall_score(answer_data, interview_type)
        
        # Identify patterns
        strengths = self.identify_strengths(answer_data)
        weaknesses = self.identify_weaknesses(answer_data)
        
        # Calculate topic scores
        topic_scores = self.calculate_topic_scores(questions_answers)
        
        # Generate suggestions and resources
        suggestions = self.generate_suggestions(
            weaknesses, interview_type, scores['overall_score']
        )
        resources = self.get_recommended_resources(weaknesses, interview_type)
        practice_areas = self.get_practice_areas(topic_scores)
        
        # Get rating
        rating = self.get_rating(scores['overall_score'])
        
        return {
            'overall_score': scores['overall_score'],
            'communication_score': scores['communication_score'],
            'technical_score': scores['technical_score'],
            'confidence_score': scores['confidence_score'],
            'overall_rating': rating,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'suggestions': suggestions,
            'topic_scores': topic_scores,
            'recommended_resources': resources,
            'practice_areas': practice_areas
        }
