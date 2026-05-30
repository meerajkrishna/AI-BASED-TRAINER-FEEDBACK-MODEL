"""
Interview Module Serializers

Django REST Framework serializers for Interview API.
"""

from rest_framework import serializers
from .models import Resume, InterviewSession, InterviewQuestion, InterviewAnswer, InterviewFeedback


class ResumeUploadSerializer(serializers.ModelSerializer):
    """Serializer for resume upload."""
    file = serializers.FileField(required=True)
    
    class Meta:
        model = Resume
        fields = ['id', 'file', 'filename']
        read_only_fields = ['id', 'filename']

    def validate_file(self, value):
        """Validate uploaded file."""
        # Check file size (10MB max)
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("File size must be less than 10MB")
        
        # Check file type (extension)
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed")
        
        # Check MIME type (defense-in-depth against spoofed extensions)
        if hasattr(value, 'content_type') and value.content_type != 'application/pdf':
            raise serializers.ValidationError("File must be a valid PDF document")
        
        return value

    def create(self, validated_data):
        """Create resume and extract filename."""
        file = validated_data.get('file')
        validated_data['filename'] = file.name if file else 'unknown.pdf'
        return super().create(validated_data)


class ResumeDetailSerializer(serializers.ModelSerializer):
    """Detailed resume serializer with parsed data."""
    
    class Meta:
        model = Resume
        fields = [
            'id', 'filename', 'raw_text', 'skills', 'experience',
            'education', 'projects', 'summary', 'is_parsed',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class ResumeListSerializer(serializers.ModelSerializer):
    """Simplified resume serializer for lists."""
    
    class Meta:
        model = Resume
        fields = ['id', 'filename', 'skills', 'is_parsed', 'created_at']
        read_only_fields = fields


# ===========================================
# Interview Session Serializers
# ===========================================

class InterviewStartSerializer(serializers.Serializer):
    """Serializer for starting an interview session."""
    interview_type = serializers.ChoiceField(
        choices=['HR', 'Technical', 'Behavioral', 'Mixed'],
        default='Technical'
    )
    resume_id = serializers.UUIDField(required=False, allow_null=True)
    total_questions = serializers.IntegerField(min_value=3, max_value=10, default=5)
    duration_minutes = serializers.IntegerField(min_value=5, max_value=30, default=15)


class InterviewSessionSerializer(serializers.ModelSerializer):
    """Full interview session serializer."""
    questions_count = serializers.SerializerMethodField()
    answers_count = serializers.SerializerMethodField()
    resume_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'interview_type', 'status', 'total_questions',
            'duration_minutes', 'current_question_index',
            'start_time', 'end_time',
            'overall_score', 'communication_score', 'technical_score', 'confidence_score',
            'questions_count', 'answers_count', 'resume_summary',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields

    def get_questions_count(self, obj):
        return obj.questions.count()

    def get_answers_count(self, obj):
        return obj.questions.filter(answer__isnull=False).count()

    def get_resume_summary(self, obj):
        if obj.resume:
            return {
                'id': str(obj.resume.id),
                'filename': obj.resume.filename,
                'skills': obj.resume.skills[:5] if obj.resume.skills else []
            }
        return None


class InterviewSessionListSerializer(serializers.ModelSerializer):
    """Simplified session serializer for lists."""
    
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'interview_type', 'status', 'overall_score',
            'start_time', 'end_time', 'created_at'
        ]
        read_only_fields = fields


# ===========================================
# Interview Question Serializers
# ===========================================

class InterviewQuestionSerializer(serializers.ModelSerializer):
    """Interview question serializer."""
    has_answer = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewQuestion
        fields = [
            'id', 'question_text', 'question_number', 'category',
            'difficulty', 'suggested_time_seconds', 'has_answer', 'created_at'
        ]
        read_only_fields = fields

    def get_has_answer(self, obj):
        return hasattr(obj, 'answer') and obj.answer is not None


class InterviewQuestionDetailSerializer(serializers.ModelSerializer):
    """Detailed question with expected points (for admin/debug)."""
    
    class Meta:
        model = InterviewQuestion
        fields = [
            'id', 'question_text', 'question_number', 'category',
            'difficulty', 'context_used', 'expected_points',
            'suggested_time_seconds', 'created_at'
        ]
        read_only_fields = fields


# ===========================================
# Interview Answer Serializers
# ===========================================

class AnswerSubmitSerializer(serializers.Serializer):
    """Serializer for submitting an answer."""
    session_id = serializers.UUIDField()
    question_id = serializers.UUIDField()
    answer_text = serializers.CharField(min_length=10, max_length=5000)
    answer_duration_seconds = serializers.IntegerField(min_value=0, required=False)


class InterviewAnswerSerializer(serializers.ModelSerializer):
    """Interview answer serializer."""
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_number = serializers.IntegerField(source='question.question_number', read_only=True)
    
    class Meta:
        model = InterviewAnswer
        fields = [
            'id', 'question_text', 'question_number', 'answer_text',
            'answer_duration_seconds', 'score', 'ai_feedback',
            'strengths', 'improvements', 'key_points_covered', 'key_points_missed',
            'relevance_score', 'clarity_score', 'depth_score', 'created_at'
        ]
        read_only_fields = fields


# ===========================================
# Interview Feedback Serializers
# ===========================================

class InterviewFeedbackSerializer(serializers.ModelSerializer):
    """Full interview feedback serializer."""
    session_info = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewFeedback
        fields = [
            'id', 'overall_summary', 'overall_rating',
            'strengths', 'weaknesses', 'suggestions',
            'topic_scores', 'percentile',
            'recommended_resources', 'practice_areas',
            'session_info', 'created_at'
        ]
        read_only_fields = fields

    def get_session_info(self, obj):
        return {
            'id': str(obj.session.id),
            'interview_type': obj.session.interview_type,
            'overall_score': obj.session.overall_score,
            'start_time': obj.session.start_time,
            'end_time': obj.session.end_time
        }


class SessionWithFeedbackSerializer(serializers.ModelSerializer):
    """Session with nested feedback and answers."""
    feedback = InterviewFeedbackSerializer(read_only=True)
    questions = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'interview_type', 'status', 'total_questions',
            'overall_score', 'communication_score', 'technical_score', 'confidence_score',
            'start_time', 'end_time', 'feedback', 'questions', 'created_at'
        ]
        read_only_fields = fields

    def get_questions(self, obj):
        questions_with_answers = []
        for question in obj.questions.all().order_by('question_number'):
            q_data = {
                'id': str(question.id),
                'question_text': question.question_text,
                'question_number': question.question_number,
                'category': question.category,
                'difficulty': question.difficulty,
                'answer': None
            }
            if hasattr(question, 'answer') and question.answer:
                q_data['answer'] = {
                    'answer_text': question.answer.answer_text,
                    'score': question.answer.score,
                    'ai_feedback': question.answer.ai_feedback,
                    'strengths': question.answer.strengths,
                    'improvements': question.answer.improvements
                }
            questions_with_answers.append(q_data)
        return questions_with_answers


# ===========================================
# Interview History Serializers
# ===========================================

class InterviewHistorySerializer(serializers.ModelSerializer):
    """Serializer for interview history list."""
    duration_minutes_actual = serializers.SerializerMethodField()
    
    class Meta:
        model = InterviewSession
        fields = [
            'id', 'interview_type', 'status', 'total_questions',
            'overall_score', 'communication_score', 'technical_score',
            'start_time', 'end_time', 'duration_minutes_actual', 'created_at'
        ]
        read_only_fields = fields

    def get_duration_minutes_actual(self, obj):
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return round(delta.total_seconds() / 60, 1)
        return None
