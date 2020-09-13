from django.views.generic import TemplateView, ListView
from django.shortcuts import render
from .models import ScoreRecord


class Index(TemplateView):
    template_name = 'game/menu.html'


class TableScore(ListView):
    template_name = 'game/table.html'
    model = ScoreRecord
    context_object_name = 'records'

    def get_queryset(self):
        new_context = ScoreRecord.objects.order_by('-score')[:10]
        return new_context
