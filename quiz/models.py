from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategori Adı")

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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oynanma Tarihi")

    def __str__(self):
        return f"{self.username} - {self.score}"

import uuid

class GameSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Başlangıç Zamanı")
    current_score = models.IntegerField(default=0, verbose_name="Güncel Skor")
    is_active = models.BooleanField(default=True, verbose_name="Aktif Mi?")
    
    def __str__(self):
        return str(self.session_id)
