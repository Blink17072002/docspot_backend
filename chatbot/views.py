from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .models import ChatHistory
from .serializers import ChatHistorySerializer, UserSerializer

from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
import openai
from openai import RateLimitError 
from decouple import config


# Config to get the OpenAI API key from the environment variables
OPENAI_API_KEY = config('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

@api_view(['POST'])
def chatbot(request):
    user_query = request.data.get('user_query', '')

    try:
        # Calls OpenAI API to get bot response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a personal AI health adviser. You are not allowed to give any information unrelated to health and medical issues. You do not also serve as a replacement to professional medical practitioners."},
                {"role": "user", "content": user_query},
            ]
        )
        bot_response = response.choices[0].message['content']

        # Saves the chat history
        chat_history = ChatHistory.objects.create(
            user_query=user_query,
            bot_response=bot_response
        )

        # Serializes the chat history and sends the response
        serializer = ChatHistorySerializer(chat_history)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except RateLimitError as e:
        # Handles RateLimitError, for example, return a custom error response
        return Response({'error': 'API rate limit exceeded. Please try again later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    except Exception as e:
        # To handle other exceptions
        return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# For authentication
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

