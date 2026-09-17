import random
from datetime import date
from django.core.management.base import BaseCommand
from quiz.models import Category, GameSettings, DailyQuestionCache

class Command(BaseCommand):
    help = 'Rotates the daily challenge category and caches 20 questions for fairness.'

    def handle(self, *args, **options):
        settings = GameSettings.load()
        today = date.today()

        # Check if there is an active daily challenge that is still valid
        current_daily = Category.objects.filter(is_daily_challenge=True).first()
        
        if current_daily and current_daily.daily_challenge_date:
            days_passed = (today - current_daily.daily_challenge_date).days
            if days_passed < settings.daily_challenge_duration_days:
                self.stdout.write(self.style.SUCCESS(f"Current daily challenge '{current_daily.name}' is still valid. No rotation needed."))
                return
            else:
                # Expire the old daily challenge
                current_daily.is_daily_challenge = False
                current_daily.is_active = False # Move it to passive pool
                current_daily.save()
                self.stdout.write(self.style.WARNING(f"Expired old daily challenge '{current_daily.name}'."))

        # Pick a new category from the passive pool (is_active=False) that has at least 20 questions
        # We filter categories that have >= 20 questions (using a simple loop or annotation)
        passive_categories = Category.objects.filter(is_active=False, is_daily_challenge=False)
        
        valid_candidates = []
        for cat in passive_categories:
            if cat.questions.count() >= 20:
                valid_candidates.append(cat)
                
        if not valid_candidates:
            self.stdout.write(self.style.ERROR("No passive categories with at least 20 questions found! Cannot rotate."))
            return

        # Pick a random candidate
        new_daily = random.choice(valid_candidates)
        new_daily.is_daily_challenge = True
        new_daily.is_active = True
        new_daily.daily_challenge_date = today
        new_daily.save()

        # Cache 20 exact questions for everyone to see today
        questions = list(new_daily.questions.order_by('?')[:20])
        
        cache, _ = DailyQuestionCache.objects.get_or_create(category=new_daily, date=today)
        cache.questions.set(questions)

        self.stdout.write(self.style.SUCCESS(f"Successfully rotated daily challenge to '{new_daily.name}' and locked 20 questions."))
