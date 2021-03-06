from django.urls import path
from . import views


urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('score_table', views.TableScore.as_view(), name='table'),
    path('game', views.Game.as_view(), name='game'),
]
