from django.apps import AppConfig


class RoadmapConfig(AppConfig):
    name = "roadmap"
    
    def ready(self):
        import roadmap.signals
