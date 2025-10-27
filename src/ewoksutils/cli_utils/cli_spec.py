from dataclasses import dataclass
from typing import Any
from typing import List
from typing import Literal
from typing import Optional
from typing import Union


@dataclass
class CLIArg:
    """Abstract CLI argument definition."""

    dest: str  # e.g. "workflows"
    flags: List[str]  # e.g. ["-p", "--parameters"]
    help: str
    type: Any = None
    default: Any = None
    choices: Optional[List[Any]] = None
    action: Optional[str] = None  # e.g. "store_true", "append"
    metavar: Optional[str] = None
    nargs: Optional[Union[Literal["+", "*"], int]] = None
    required: Optional[bool] = None

    @property
    def is_positional(self) -> bool:
        return len(self.flags) == 0

    def __post_init__(self):
        is_positional = len(self.flags) == 0

        if self.action == "store_true":
            self.default = False
        elif self.action == "store_false":
            self.default = True
        elif self.action == "append":
            self.default = []

        if is_positional:
            if self.default is not None:
                raise ValueError("Only named CLI arguments can have a default")
            if self.action is not None:
                raise ValueError("Only named CLI arguments can have an action")
            if self.choices is not None:
                raise ValueError("Only named CLI arguments can have choices")
        else:
            if self.nargs is not None:
                raise ValueError("Only positional CLI arguments can have 'nargs'")
