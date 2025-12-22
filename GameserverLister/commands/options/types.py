from typing import Any

import click
from click import Parameter, Context

from GameserverLister.common.types import ExtendedEnum


class EnumChoice(click.Choice):
    enum: type[ExtendedEnum]

    def __init__(self, enum: type[ExtendedEnum], case_sensitive: bool = False):
        self.enum = enum
        super().__init__(enum.list(), case_sensitive)

    def convert(self, value: Any, param: Parameter | None, ctx: Context | None) -> Any:
        return self.enum(super().convert(value, param, ctx))
