from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategori Adı")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")
    is_daily_challenge = models.BooleanField(default=False, verbose_name="Günün Kategorisi Mi?")
    daily_challenge_date = models.DateField(null=True, blank=True, verbose_name="Günün Kategorisi Olma Tarihi")

    def __str__(self):
        return self.name

class Question(models.Model):
    OPTION_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField(verbose_name="Soru Metni")
    option_a = models.CharField(max_length=255, verbose_name="A Seçeneği")
    option_b = models.CharField(max_length=255, verbose_name="B Seçeneği")
    option_c = models.CharField(max_length=255, verbose_name="C Seçeneği")
    option_d = models.CharField(max_length=255, verbose_name="D Seçeneği")
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES, verbose_name="Doğru Cevap")

    def __str__(self):
        return f"[{self.category.name}] {self.text[:50]}"

class Leaderboard(models.Model):
    username = models.CharField(max_length=50, verbose_name="Kullanıcı Adı")
    score = models.IntegerField(verbose_name="Skor")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Kategori")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oynanma Tarihi")

    def __str__(self):
        return f"{self.username} - {self.score}"

import uuid
import datetime

class GameSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Seçilen Kategori")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Başlangıç Zamanı")
    current_score = models.IntegerField(default=0, verbose_name="Güncel Skor")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")
    
    def __str__(self):
        return str(self.session_id)

class GameSettings(models.Model):
    max_home_categories = models.IntegerField(default=4, verbose_name="Ana Sayfa Maksimum Kategori Sayısı")
    daily_challenge_duration_days = models.IntegerField(default=1, verbose_name="Günün Kategorisi Süresi (Gün)")
    daily_reset_time = models.TimeField(default=datetime.time(0, 0), verbose_name="Günlük Soruların Yenilenme Saati")
    
    class Meta:
        verbose_name = "Oyun Ayarları"
        verbose_name_plural = "Oyun Ayarları"

    def save(self, *args, **kwargs):
        self.pk = 1 # Singleton
        super(GameSettings, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class DailyQuestionCache(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    questions = models.ManyToManyField(Question)
    date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Günlük Sorular - {self.category.name} ({self.date})"
