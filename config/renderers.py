# config/renderers.py
from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    charset = 'utf-8'  # Устанавливаем кодировку для поддержки кириллицы

    def render(self, data, accepted_media_type=None, renderer_context=None):
        # Гарантируем, что данные всегда будут возвращаться в JSON формате
        return super().render(data, accepted_media_type, renderer_context)
