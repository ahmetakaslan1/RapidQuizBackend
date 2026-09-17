import jwt
import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Category, Question, Leaderboard, GameSession
from django.utils import timezone

def generate_ephemeral_token(session_id):
    payload = {
        'session_id': str(session_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=100),
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
        
        # Get 20 questions randomly for this category
        questions = Question.objects.filter(category=category).order_by('?')[:20]
        if not questions:
            return Response({"error": "Bu kategoride soru bulunmuyor."}, status=status.HTTP_400_BAD_REQUEST)
            
        session = GameSession.objects.create()
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
                remaining_seconds = int(5.0 - seconds_passed)
                if remaining_seconds > 0:
                    bonus = min(remaining_seconds, 4)
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
            score=session.current_score
        )
        
        session.is_active = False
        session.save()
        
        return Response({"status": "success", "final_score": session.current_score})
