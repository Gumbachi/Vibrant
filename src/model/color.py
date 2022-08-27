from dataclasses import dataclass

import database as db
import discord
from PIL import ImageColor


@dataclass(slots=True)
class Color:
    name: str
    hexcode: str
    role: int | None = None

    def __post_init__(self):
        import utils

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
            role=data.get("role", None),
        )

    def as_dict(self):
        return {
            "name": self.name,
            "hexcode": self.hexcode,
            "role": self.role
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
            new_color = Color(self.name, hexcode=self.hexcode, role=role.id)
            db.update_color(guild.id, old=self, new=new_color)

        self.role = role.id
        return role

    def get_members(self, guild: discord.Guild) -> list[discord.Member]:
        """Fetch all the members with this color"""
        role = guild.get_role(self.role)
        return [] if not role else role.members

    def to_discord_color(self) -> discord.Colour:
        return discord.Colour.from_rgb(*self.rgb)

    async def get_role(self, guild: discord.Guild, create: bool = False, updatedb: bool = True) -> discord.Role | None:
        """Fetch the role associated to this color or None if not found."""
        # Create role if necessary or return None since no role id
        if self.role is None:
            return await self.create_role(guild, updatedb=updatedb) if create else None

        # Try to find role in cache
        if not (role := guild.get_role(self.role)):
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
