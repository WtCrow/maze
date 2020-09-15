from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.shortcuts import render


@require_http_methods(["GET"])
def custom_handler404(request, *args, **kwargs):
    return render(request, '404.html', status=404)
