import dataclasses
import typing

import src.model
import src.model as model


@dataclasses.dataclass(slots=True)
class Guild:
    id: int
    colors: list[model.Color]
    themes: list[model.Theme]

    def serialize(self):
        return {
            id: self.id,
            colors: []
        }

    @classmethod
    def deserialize(cls, data: dict[str, typing.Any]):
        return cls(
            id=data["_id"],
            colors=[model.Color.from_dict()]
        )