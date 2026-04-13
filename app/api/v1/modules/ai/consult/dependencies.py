from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db


from app.api.v1.modules.ai.consult.repositories.ai_consult_sessions_repository import AIConsultSessionsRepository
from app.api.v1.modules.ai.consult.services.ai_consult_sessions_service import AIConsultSessionsService


from app.api.v1.modules.ai.consult.repositories.ai_topic_categories_repository import (
    AITopicCategoriesRepository,
)
from app.api.v1.modules.ai.consult.services.ai_topic_categories_service import (
    AITopicCategoriesService,
)


from app.api.v1.modules.ai.consult.repositories.ai_topic_services_repository import (
    AITopicServicesRepository,
)
from app.api.v1.modules.ai.consult.services.ai_topic_services_service import (
    AITopicServicesService,
)


from app.api.v1.modules.ai.consult.repositories.ai_topics_repository import (
    AITopicsRepository,
)
from app.api.v1.modules.ai.consult.services.ai_consult_service import (
    AITopicsService,
)

from app.api.v1.modules.ai.consult.services.ai_consult_actions_service import (
    AIConsultActionsService,
)

from app.api.v1.modules.ai.consult.repositories.ai_consult_actions_repository import (
    AIConsultActionsRepository,
)


##### consult_sessions
def get_ai_consult_sessions_repository(db: AsyncSession = Depends(get_db)) -> AIConsultSessionsRepository:
    return AIConsultSessionsRepository(db)

def get_ai_consult_sessions_service(
    repo: AIConsultSessionsRepository = Depends(get_ai_consult_sessions_repository),
) -> AIConsultSessionsService:
    return AIConsultSessionsService(repo)


##### topic_categories
def get_ai_topic_categories_repository(
    db: AsyncSession = Depends(get_db),
) -> AITopicCategoriesRepository:
    return AITopicCategoriesRepository(db)

def get_ai_topic_categories_service(
    repo: AITopicCategoriesRepository = Depends(get_ai_topic_categories_repository),
) -> AITopicCategoriesService:
    return AITopicCategoriesService(repo)


##### topic_services
def get_ai_topic_services_repository(
    db: AsyncSession = Depends(get_db),
) -> AITopicServicesRepository:
    return AITopicServicesRepository(db)

def get_ai_topic_services_service(
    repo: AITopicServicesRepository = Depends(get_ai_topic_services_repository),
) -> AITopicServicesService:
    return AITopicServicesService(repo)


##### topics
def get_ai_topics_repository(
    db: AsyncSession = Depends(get_db),
) -> AITopicsRepository:
    return AITopicsRepository(db)

def get_ai_topics_service(
    repo: AITopicsRepository = Depends(get_ai_topics_repository),
) -> AITopicsService:
    return AITopicsService(repo)


##### actions
def get_ai_consult_actions_repository(
    db: AsyncSession = Depends(get_db),
) -> AIConsultActionsRepository:
    return AIConsultActionsRepository(db)


def get_ai_consult_actions_service(
    repo: AIConsultActionsRepository = Depends(get_ai_consult_actions_repository),
) -> AIConsultActionsService:
    return AIConsultActionsService(repo)