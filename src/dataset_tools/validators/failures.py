from dataclasses import dataclass, field
from typing import Any

from dataset_tools.validators.reason_codes import ValidationReasonCode


@dataclass
class ValidationFailure:
    reason_code: ValidationReasonCode
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
