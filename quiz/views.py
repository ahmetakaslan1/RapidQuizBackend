import jwt
import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from datetime import date
from .models import Category, Question, Leaderboard, GameSession, GameSettings, DailyQuestionCache
from django.utils import timezone

from django.db.models import Count

class GetCategoriesView(APIView):
    def get(self, request):
        settings_obj = GameSettings.load()
        limit = settings_obj.max_home_categories
        
        # Sadece içinde soru olan aktif kategorileri getir
        valid_categories = Category.objects.annotate(q_count=Count('questions')).filter(is_active=True, q_count__gt=0)
        
        daily = valid_categories.filter(is_daily_challenge=True).first()
        others = valid_categories.filter(is_daily_challenge=False).order_by('id')
        
        categories = []
        if daily:
            categories.append(daily)
        categories.extend(list(others))
        
        data = [{"id": c.id, "name": c.name, "is_daily_challenge": c.is_daily_challenge} for c in categories]
        return Response(data)

class GetLeaderboardView(APIView):
    def get(self, request):
        category_id = request.query_params.get('category_id')
        if category_id:
            top_scores = Leaderboard.objects.filter(category_id=category_id).order_by('-score')[:50]
        else:
            top_scores = Leaderboard.objects.order_by('-score')[:50]
            
        data = [
            {"username": s.username, "score": s.score, "date": s.created_at.strftime("%Y-%m-%d %H:%M"), "category": s.category.name if s.category else "Genel"} 
            for s in top_scores
        ]
        return Response(data)

def generate_ephemeral_token(session_id):
    payload = {
        'session_id': str(session_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=300),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def get_session_from_request(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        session_id = payload.get('session_id')
        session = GameSession.objects.get(session_id=session_id, is_active=True)
        return session
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, GameSession.DoesNotExist):
        return None

class StartGameView(APIView):
    def post(self, request):
        category_id = request.data.get('category_id')
        category = get_object_or_404(Category, id=category_id)
        
        settings_obj = GameSettings.load()
        reset_time = settings_obj.daily_reset_time
        now = timezone.localtime(timezone.now())
        
        logical_date = now.date()
        if now.time() < reset_time:
            logical_date = logical_date - datetime.timedelta(days=1)
            
        cache = DailyQuestionCache.objects.filter(category=category, date=logical_date).first()
        
        if not cache:
            qs = list(Question.objects.filter(category=category).order_by('?')[:20])
            if qs:
                cache = DailyQuestionCache.objects.create(category=category, date=logical_date)
                cache.questions.set(qs)
                
        if cache and cache.questions.exists():
            questions = list(cache.questions.all()[:20])
        else:
            questions = list(Question.objects.filter(category=category).order_by('?')[:20])
            
        if not questions:
            return Response({"error": "Bu kategoride soru bulunmuyor."}, status=status.HTTP_400_BAD_REQUEST)
            
        session = GameSession.objects.create(category=category)
        token = generate_ephemeral_token(session.session_id)
        
        question_data = [{
            "id": q.id,
            "text": q.text,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d,
        } for q in questions]
        
        return Response({
            "token": token,
            "questions": question_data
        })

class SubmitAnswerView(APIView):
    def post(self, request):
        session = get_session_from_request(request)
        if not session:
            return Response({"error": "Geçersiz veya süresi dolmuş token (Hile tespiti veya süre sonu)."}, status=status.HTTP_403_FORBIDDEN)
            
        question_id = request.data.get('question_id')
        selected_option = request.data.get('selected_option') # A, B, C, D veya TIMEOUT
        action_ms = request.data.get('islem_yapilan_milisaniye') 
        
        if not all([question_id, selected_option, action_ms is not None]):
            return Response({"error": "Eksik parametre."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            action_ms = int(action_ms)
            question = Question.objects.get(id=question_id)
        except (ValueError, Question.DoesNotExist):
            return Response({"error": "Geçersiz veri."}, status=status.HTTP_400_BAD_REQUEST)
            
        points_to_add = 0
        seconds_passed = action_ms / 1000.0
        
        if selected_option.upper() == 'TIMEOUT':
            points_to_add = -10
        else:
            is_correct = (selected_option.upper() == question.correct_option)
            if is_correct:
                points_to_add = 10 
                remaining_seconds = int(10.0 - seconds_passed)
                if remaining_seconds > 0:
                    bonus = min(remaining_seconds, 9)
                    points_to_add += bonus
            else:
                if seconds_passed <= 2.0:
                    points_to_add = -15
                else:
                    points_to_add = -5
                    
        session.current_score += points_to_add
        session.save()
        
        return Response({
            "status": "success",
            "points_awarded": points_to_add,
            "current_score": session.current_score,
            "correct_option": question.correct_option 
        })

class SubmitScoreView(APIView):
    def post(self, request):
        session = get_session_from_request(request)
        if not session:
            return Response({"error": "Oyun oturumu bulunamadı."}, status=status.HTTP_403_FORBIDDEN)
            
        # Honey Pot Check
        honey_pot = request.data.get('website_url', '')
        if honey_pot != '':
            session.is_active = False
            session.save()
            return Response({"error": "Bot detected."}, status=status.HTTP_403_FORBIDDEN)
            
        username = request.data.get('username')
        if not username:
            return Response({"error": "Kullanıcı adı zorunludur."}, status=status.HTTP_400_BAD_REQUEST)
            
        Leaderboard.objects.create(
            username=username,
            score=session.current_score,
            category=session.category
        )
        
        session.is_active = False
        session.save()
        
        return Response({"status": "success", "final_score": session.current_score})
