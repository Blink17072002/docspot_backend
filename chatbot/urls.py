from django.urls import path
from .views import chatbot, signup, user_login

urlpatterns = [
    path('', chatbot, name='chatbot'),
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
]


