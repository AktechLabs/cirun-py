from typer.core import TyperGroup

from click import Context


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order appear."""
        return list(self.commands)
