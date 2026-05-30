"""
Learning API Views
──────────────────
All views serve from the local DB — no external API calls happen on reads.
Public endpoints (AllowAny) so learning content is accessible without login.
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Topic, TopicVideo

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_topics(request):
    """
    GET /api/learning/topics/
    Returns all topics grouped by category, with video count.

    Optional query params:
      ?category=arithmetic    Filter by category
      ?level=Beginner         Filter by difficulty level
      ?search=percent         Search by name
      ?include_archived=true  Include archived topics (hidden by default)
    """
    try:
        queryset = Topic.objects.all()

        # By default, exclude archived topics
        include_archived = request.query_params.get('include_archived', '').lower() == 'true'
        if not include_archived:
            queryset = queryset.filter(is_archived=False)

        # Apply filters
        category = request.query_params.get('category', '')
        if category:
            queryset = queryset.filter(category=category)

        level = request.query_params.get('level', '')
        if level:
            queryset = queryset.filter(level=level)

        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(name__icontains=search)

        topics = []
        for topic in queryset:
            topics.append({
                'id': topic.id,
                'name': topic.name,
                'slug': topic.slug,
                'category': topic.category,
                'category_display': topic.get_category_display(),
                'icon': topic.icon,
                'level': topic.level,
                'definition': topic.definition,
                'video_count': topic.video_count,
                'has_quiz': topic.has_quiz,
                'is_archived': topic.is_archived,
            })

        # Group by category for the sidebar
        categories = {}
        for t in topics:
            cat = t['category']
            if cat not in categories:
                categories[cat] = {
                    'key': cat,
                    'label': t['category_display'],
                    'topics': [],
                }
            categories[cat]['topics'].append(t)

        return Response({
            'topics': topics,
            'categories': list(categories.values()),
            'total_count': len(topics),
        })

    except Exception as e:
        logger.error("Error listing topics: %s", e)
        return Response(
            {'error': 'Failed to load topics. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def topic_detail(request, slug):
    """
    GET /api/learning/topics/<slug>/
    Returns a single topic with full description + all cached videos.
    """
    try:
        topic = Topic.objects.filter(slug=slug).first()
        if not topic:
            return Response(
                {'error': 'Topic not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        videos = TopicVideo.objects.filter(topic=topic).order_by('order')
        video_list = []
        for v in videos:
            video_list.append({
                'id': v.id,
                'youtube_id': v.youtube_id,
                'title': v.title,
                'thumbnail_url': v.thumbnail_url,
                'channel_name': v.channel_name,
                'duration': v.duration,
                'embed_url': v.embed_url,
                'watch_url': v.watch_url,
                'order': v.order,
            })

        return Response({
            'id': topic.id,
            'name': topic.name,
            'slug': topic.slug,
            'category': topic.category,
            'category_display': topic.get_category_display(),
            'icon': topic.icon,
            'level': topic.level,
            'definition': topic.definition,
            'description': topic.description,
            'wikipedia_url': topic.wikipedia_url,
            'videos': video_list,
            'video_count': len(video_list),
            'has_quiz': topic.has_quiz,
            'is_archived': topic.is_archived,
        })

    except Exception as e:
        logger.error("Error fetching topic '%s': %s", slug, e)
        return Response(
            {'error': 'Failed to load topic details. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    """
    GET /api/learning/categories/
    Returns list of all available categories with topic counts.
    Only counts non-archived topics.
    """
    try:
        categories = []
        for key, label in Topic.CATEGORY_CHOICES:
            count = Topic.objects.filter(category=key, is_archived=False).count()
            if count > 0:
                quiz_count = Topic.objects.filter(category=key, is_archived=False, has_quiz=True).count()
                categories.append({
                    'key': key,
                    'label': label,
                    'topic_count': count,
                    'quiz_count': quiz_count,
                })

        return Response({'categories': categories})

    except Exception as e:
        logger.error("Error listing categories: %s", e)
        return Response(
            {'error': 'Failed to load categories.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
