from typing import List
from ..schema.lead_schema import Lead

class BaseCollector:
    def collect(self) -> List[Lead]:
        raise NotImplementedError
