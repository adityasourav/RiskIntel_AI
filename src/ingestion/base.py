import abc
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class DataRecord:
    """Represents a standardized data record from any source."""
    source: str
    timestamp: str
    text: str
    title: str
    entity: str
    url: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataSource(abc.ABC):
    """Abstract base class for data sources."""
    
    @abc.abstractmethod
    def fetch(self, keyword: str, max_results: int) -> List[DataRecord]:
        """Fetch records from the source matching the keyword."""
        pass
        
    @abc.abstractmethod
    def load_sample(self) -> List[DataRecord]:
        """Load sample records for fallback/testing."""
        pass
