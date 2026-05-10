from sqlalchemy.orm import Session

from app.core.config import settings
from app.domain.history.provider import HistoryProvider
from app.domain.history.slidingwindow import SlidingWindowProvider

# extend this for user customization 
def create_history_provider(db: Session, strategy: str = settings.history_strategy) -> HistoryProvider:
    if strategy == "sliding_window":
        return SlidingWindowProvider(db, window_size=settings.last_n_messages)
    raise ValueError(f"Unknown history strategy: {strategy}")
