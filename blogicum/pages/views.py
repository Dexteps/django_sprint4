from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


class AboutView(TemplateView):
    """Класс вызова шаблона (про нас)."""

    template_name = 'pages/about.html'


class RulesView(TemplateView):
    """Класс вызова шаблона (наши правила)."""

    template_name = 'pages/rules.html'


def page_not_found(request, exception) -> HttpResponse:
    """Функция вызова представления ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason='') -> HttpResponse:
    """функция вызова представления ошибки 403."""
    return render(request, 'pages/403csrf.html', status=403)


def server_error(request) -> HttpResponse:
    """Функция вызова представления ошибки 500."""
    return render(request, 'pages/500.html', status=500)
