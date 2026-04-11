# Proxy para compatibilidad con migraciones de Django.
# Las entidades reales viven en questions/entities/
from questions.entities.question_entity import Question  # noqa: F401
from questions.entities.video_entity import Video, Subtitle  # noqa: F401
