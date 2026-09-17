from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import Category, Question, Leaderboard, GameSession, GameSettings, DailyQuestionCache
from .ai_service import generate_questions

@admin.register(GameSettings)
class GameSettingsAdmin(admin.ModelAdmin):
    list_display = ('max_home_categories', 'daily_challenge_duration_days')
    
    def has_add_permission(self, request):
        # Allow adding only if no settings exist
        return not GameSettings.objects.exists()

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'correct_option')
    list_filter = ('category',)
    search_fields = ('text',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_daily_challenge', 'daily_challenge_date', 'question_count')
    list_filter = ('is_active', 'is_daily_challenge')
    search_fields = ('name',)
    actions = ['generate_ai_questions']

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = "Soru Sayısı"

    @admin.action(description='Seçili Kategorilere Yapay Zeka ile 100 Soru Üret')
    def generate_ai_questions(self, request, queryset):
        for category in queryset:
            try:
                # If category name is "Sürpriz", "Süpriz" or "Rastgele", let AI decide the topic
                is_surprise = category.name.strip().lower() in ["sürpriz", "süpriz", "rastgele"]
                topic = None if is_surprise else category.name
                
                result = generate_questions(topic=topic, num_questions=100)
                
                # If it was surprise, rename the category
                if topic is None:
                    category.name = result['category_name']
                    category.save()

                for q_data in result['questions']:
                    Question.objects.create(
                        category=category,
                        text=q_data['text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_option=q_data['correct_option']
                    )
                messages.success(request, f"{category.name} için 100 soru başarıyla üretildi!")
            except Exception as e:
                messages.error(request, f"{category.name} için hata oluştu: {str(e)}")

admin.site.register(Leaderboard)
admin.site.register(GameSession)
admin.site.register(DailyQuestionCache)
