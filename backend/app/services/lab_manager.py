from typing import Dict, Optional
import logging
from models import base
from database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LabManager:
    def __init__(self):
        pass

    def get_lab_by_id(self, lab_id: int, db=None) -> Optional[Dict]:
        close_db = False
        if db is None:
            db = next(get_db())
            close_db = True
        try:
            lab = (
                db.query(
                    base.Lab.id,
                    base.Lab.name,
                    base.Lab.description,
                    base.Lab.external_url,
                )
                .filter(base.Lab.id == lab_id)
                .first()
            )
            if lab:
                return lab._asdict()
            return None
        finally:
            if close_db:
                db.close()

    def start_lab(self, lab_id: int) -> bool:
        """External labs are always active."""
        return True

    def stop_lab(self, lab_id: int) -> bool:
        """External labs are always active."""
        return True

    def reset_lab(self, lab_id: int) -> bool:
        return True

    def delete_lab(self, lab_id: int) -> bool:
        return True
