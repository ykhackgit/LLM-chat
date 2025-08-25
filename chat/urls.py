from django.urls import path
from .views import chat_view, send_message, get_history

urlpatterns = [
    path("", chat_view, name="chat"),
    path("api/send_message/", send_message, name="send_message"),
    path("api/history/", get_history, name="get_history"),
]
