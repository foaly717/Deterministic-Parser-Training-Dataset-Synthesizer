from abc import ABC, abstractmethod
from pathlib import Path

from dataset_tools.evidence.schema import NormalizedEvidenceDocument


class EvidenceLoader(ABC):
    @abstractmethod
    def supports(self, path: Path) -> bool:
        pass

    @abstractmethod
    def load(self, path: Path) -> NormalizedEvidenceDocument:
        pass
