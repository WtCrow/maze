from django.views.generic import TemplateView, ListView
from .models import ScoreRecord


class Index(TemplateView):
    """Main page"""
    http_method_names = ('get', )
    template_name = 'game/menu.html'


class TableScore(ListView):
    """Table with top 10 users"""
    http_method_names = ('get', )
    template_name = 'game/table.html'
    model = ScoreRecord
    context_object_name = 'records'

    def get_queryset(self):
        new_context = ScoreRecord.objects.order_by('-score', 'date_create')[:10]
        return new_context


class Game(TemplateView):
    """Page with game"""
    http_method_names = ('get', )
    template_name = 'game/maze.html'
