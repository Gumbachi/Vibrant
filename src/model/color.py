from dataclasses import dataclass
from typing import Self, TypedDict

import discord
from PIL import ImageColor

import src.common.exceptions as exceptions
import src.database as db
import src.utils as utils


class ColorDict(TypedDict):
    name: str
    hexcode: str
    role: int | None
    members: list[int]


class NewColor:
    def __init__(self, name: str, value: str, role: discord.Role | None = None) -> None:

        if 1 > len(name) > 99:
            raise exceptions.InvalidColorName("Name must be within 1 and 99 characters")

        hexcode = utils.parse_color_or_none(value)

        if hexcode is None:
            raise exceptions.InvalidColorValue()

        # #000 is transparent in discord so black can be best represented by #010101
        if hexcode in ("#000", "#000000"):
            hexcode = "#010101"

        self.name = name
        self.hexcode = hexcode
        self.role = role
        self._members: list[discord.Member] = []

    def serialize(self, include_members: bool = False) -> ColorDict:
        """Serialize the class to a dict/json. Include members is optional."""

        role = None if role is None else role.id

        dict = {
            "name": self.name,
            "hexcode": self.hexcode,
            "role": role,
        }

        if include_members:
            dict.update({"members": [member.id for member in self.get_members()]})

        return dict

    @classmethod
    def deserialize(cls, data: ColorDict, guild: discord.Guild) -> Self:
        """Convert dict/json to class. Guild instance to resolve member/role ids"""

        if data["role"] != None:
            role = guild.get_role(data["role"])
        else:
            role = None

        color = cls(
            name=data["name"],
            hexcode=data["hexcode"],
            role=role
        )

        # Add Member data if exists
        if "members" in data:
            members = [guild.get_member(id) for id in data["members"]]
            members = [m for m in members if m is not None]
            color._members = members

        return color

    @property
    def rgb(self) -> tuple[int, int, int]:
        return ImageColor.getrgb(self.hexcode)

    def to_discord_color(self) -> discord.Colour:
        return discord.Colour.from_rgb(*self.rgb)

    @property
    def optimal_text_color(self) -> tuple[int, int, int]:
        r, g, b = self.rgb
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return (0, 0, 0) if luminance > 0.5 else (240, 240, 240)

    def get_members(self) -> list[discord.Member]:
        """Fetch the members of this role based on the associated role."""
        if self.role is None:
            self._members = []
        else:
            self._members = self.role.members

        return self._members

    async def create_role(self, guild: discord.Guild) -> discord.Role:
        """Create and associate a role with this color."""
        role = await guild.create_role(name=self.name, color=self.to_discord_color())
        self.role = role
        return role

    async def delete_role(self) -> None:
        """Delete and dissociate a role with this color."""
        if self.role:
            await self.role.delete()
            self.role = None

    async def apply_to(self, target: discord.Member) -> None:
        """Apply the role representing this color to somebody."""
        if self.role is None:
            await self.create_role(guild=target.guild)

        await target.add_roles(self.role)

    async def remove_from(self, target: discord.Member) -> None:
        """Remove the role representing this color from someone."""
        if self.role:
            await target.remove_roles(self.role)


@dataclass(slots=True)
class Color:
    name: str
    hexcode: str
    role_id: int | None = None

    def __post_init__(self):

        self.hexcode = utils.parse_string_to_hex(self.hexcode)

        if len(self.name) > 99:
            raise utils.InvalidColorName()

        # 000 is transparent in discord not black
        if self.hexcode in ("#000", "#000000"):
            self.hexcode = "#010101"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data["name"],
            hexcode=data["hexcode"],
            role_id=data.get("role", None),
        )

    def as_dict(self):
        return {
            "name": self.name,
            "hexcode": self.hexcode,
            "role": self.role_id
        }

    @property
    def rgb(self):
        return ImageColor.getrgb(self.hexcode)

    @property
    def optimal_text_color(self) -> tuple:
        r, g, b = self.rgb
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return (0, 0, 0) if luminance > 0.5 else (240, 240, 240)

    async def create_role(self, guild: discord.Guild, updatedb: bool = True) -> discord.Role:
        """Create a role from this color"""
        role = await guild.create_role(name=self.name, color=self.to_discord_color())

        if updatedb:
            new_color = Color(self.name, hexcode=self.hexcode, role_id=role.id)
            db.update_color(guild.id, old=self, new=new_color)

        self.role_id = role.id
        return role

    def get_members(self, guild: discord.Guild) -> list[discord.Member]:
        """Fetch all the members with this color"""
        role = guild.get_role(self.role_id)
        return [] if not role else role.members

    def to_discord_color(self) -> discord.Colour:
        return discord.Colour.from_rgb(*self.rgb)

    async def get_role(self, guild: discord.Guild, create: bool = False, updatedb: bool = True) -> discord.Role | None:
        """Fetch the role associated to this color or None if not found."""
        # Create role if necessary or return None since no role id
        if self.role_id is None:
            return await self.create_role(guild, updatedb=updatedb) if create else None

        # Try to find role in cache
        if not (role := guild.get_role(self.role_id)):
            return await self.create_role(guild, updatedb=updatedb) if create else None
        return role

    async def apply_to(self, target: discord.Member, updatedb: bool = True) -> None:
        """Apply the role representing this color to somebody."""
        role = await self.get_role(target.guild, create=True, updatedb=updatedb)
        await target.add_roles(role)

    async def remove_from(self, target: discord.Member) -> None:
        """Remove a role representing a color from someone."""
        role = await self.get_role(target.guild)
        if role:
            await target.remove_roles(role)

            if not role.members:
                await role.delete()

    async def erase(self, guild: discord.Guild):
        """Remove the color from existence."""
        role = await self.get_role(guild=guild)
        if role:
            await role.delete()
