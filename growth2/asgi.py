"""
ASGI config for growth2 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "growth2.settings")

application = get_asgi_application()

openai.api_key = "sk-g-RLTZrCZeV9ya0AkIDlyCT3BlbkFJXPawA3nD87SkDvwCTc0p"