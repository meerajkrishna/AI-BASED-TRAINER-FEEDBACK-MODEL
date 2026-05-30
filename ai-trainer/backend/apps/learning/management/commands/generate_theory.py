import time
import logging
from django.core.management.base import BaseCommand
from apps.learning.models import Topic
from apps.learning.gemini_service import GeminiLearningService, ContentGenerationError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Generate comprehensive aptitude theory content using Gemini AI for active topics."

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int, default=0,
            help='Limit the number of topics to update (0 = all)',
        )
        parser.add_argument(
            '--category', type=str, default='',
            help='Only update topics in this category',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        category_filter = options['category']

        # Only fetch active topics that we actually show to the user
        queryset = Topic.objects.filter(is_archived=False).order_by('id')

        if category_filter:
            queryset = queryset.filter(category=category_filter)
            self.stdout.write(f"Filtered to category '{category_filter}'")

        if limit > 0:
            queryset = queryset[:limit]
            self.stdout.write(f"Limited to {limit} topics")

        topics = list(queryset)
        total = len(topics)
        updated = 0
        errors = 0

        self.stdout.write(self.style.SUCCESS(f"\n{'='*60}"))
        self.stdout.write(self.style.SUCCESS(f"  Generating GeeksForGeeks style theory for {total} ACTIVE topics"))
        self.stdout.write(self.style.SUCCESS(f"{'='*60}\n"))

        if total == 0:
            self.stdout.write("No active topics found. Make sure topics are seeded and not archived.")
            return

        try:
            gemini_svc = GeminiLearningService()
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Configuration Error: {e}"))
            return

        for idx, topic in enumerate(topics, start=1):
            try:
                self.stdout.write(f"  [{idx}/{total}] Generating content for: {topic.name}...")

                # Call the gemini service to get the HTML content
                content_data = gemini_svc.generate_topic_tutorial(topic.name)
                
                new_desc = content_data.get('description', '')
                if not new_desc or len(new_desc) < 100:
                    self.stdout.write(self.style.WARNING(f"    WARNING: Content too short or empty for {topic.name}"))
                    errors += 1
                    continue

                topic.definition = content_data.get('definition', topic.definition)
                topic.description = new_desc
                topic.save()

                self.stdout.write(self.style.SUCCESS(
                    f"    OK: Saved {len(new_desc)} chars of rich HTML"
                ))
                updated += 1

                # Delay between requests to not overwhelm the API (even if we rotate)
                if idx < total:
                    self.stdout.write("    Waiting 3 seconds before next request...")
                    time.sleep(3)

            except ContentGenerationError as e:
                self.stdout.write(self.style.ERROR(f"    FATAL ERROR: {e}"))
                self.stdout.write(self.style.ERROR(f"    Stopping operation. All keys exhausted or broken."))
                break
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"    ERROR generating content for {topic.name}: {e}"))
                
                # Still try to wait before next even on generic error
                if idx < total:
                    time.sleep(3)

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"  GENERATION COMPLETE"))
        self.stdout.write(f"  Updated: {updated}")
        self.stdout.write(f"  Errors:  {errors}")
        self.stdout.write(f"{'='*60}\n")
