"""
Learning Module Models
──────────────────────
Topic       — An aptitude learning topic (e.g. "Percentage", "Number Series")
TopicVideo  — A cached YouTube video associated with a topic (10 per topic)

All YouTube/Wikipedia data is fetched once by the seed_topics command and
stored locally in SQLite. The API views serve from the DB — no external
calls on read, so there is zero runtime dependency on YouTube/Wikipedia.
"""

from django.db import models
from django.utils.text import slugify


class Topic(models.Model):
    """A single aptitude learning topic."""

    CATEGORY_CHOICES = [
        ('arithmetic', 'Arithmetic'),
        ('number_system', 'Number System'),
        ('algebra', 'Algebra'),
        ('geometry', 'Geometry & Mensuration'),
        ('modern_maths', 'Modern Maths'),
        ('time_speed_work', 'Time, Speed & Work'),
        ('data_interpretation', 'Data Interpretation'),
        ('logical_reasoning', 'Logical Reasoning'),
        ('verbal_ability', 'Verbal Ability'),
        ('computer_aptitude', 'Computer Aptitude'),
        ('general_aptitude', 'General Aptitude'),
        ('quantitative', 'Quantitative Aptitude'),
    ]

    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    name        = models.CharField(max_length=200, unique=True)
    slug        = models.SlugField(max_length=220, unique=True, blank=True)
    category    = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='arithmetic')
    icon        = models.CharField(max_length=10, default='📘')
    level       = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    definition  = models.CharField(max_length=500, blank=True, default='')
    description = models.TextField(blank=True, default='')  # Wikipedia summary or Gemini fallback
    wikipedia_url = models.URLField(blank=True, default='')
    order       = models.PositiveIntegerField(default=0)  # Display order within category
    has_quiz    = models.BooleanField(default=False)  # True if quiz data exists for this topic
    is_archived = models.BooleanField(default=False)  # True if hidden from UI (no quiz data yet)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        archived = " [ARCHIVED]" if self.is_archived else ""
        return f"{self.name} ({self.get_category_display()}){archived}"

    @property
    def video_count(self):
        return self.videos.count()


class TopicVideo(models.Model):
    """A cached YouTube video for a learning topic."""

    topic         = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='videos')
    youtube_id    = models.CharField(max_length=20)
    title         = models.CharField(max_length=300)
    thumbnail_url = models.URLField(blank=True, default='')
    channel_name  = models.CharField(max_length=200, blank=True, default='')
    duration      = models.CharField(max_length=20, blank=True, default='')  # e.g. "12:34"
    order         = models.PositiveSmallIntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = [('topic', 'youtube_id')]  # No duplicate videos per topic

    def __str__(self):
        return f"{self.title} ({self.topic.name})"

    @property
    def embed_url(self):
        return f"https://www.youtube.com/embed/{self.youtube_id}"

    @property
    def watch_url(self):
        return f"https://www.youtube.com/watch?v={self.youtube_id}"
