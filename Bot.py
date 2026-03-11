import discord
from discord.ext import commands
import random

TOKEN = "MTQ4MDE3OTUyNjQ4MjAwMjA5Nw.GPGFhp.yKN15dwBuX_acGnfUzng8wISalcTJWt0tacx34"
CREATE_CHANNEL_ID = 1480181212080246844

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

owner_channels = {}
control_channels = {}
allowed_role = None

room_names = [
"🎮 Gaming Room",
"🎧 Chill Zone",
"⚔ Squad",
"🔥 Party Room",
"🎤 Talk Room",
"🚀 Space Room"
]
async def update_channel_name(channel):

    if channel:

        name = channel.name.split("|")[0].strip()

        await channel.edit(
            name=f"{name} | {len(channel.members)}"
        )

class VoicePanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction):

        if not interaction.user.voice or not interaction.user.voice.channel:

            await interaction.response.send_message(
                "❌ Debes estar en el canal de voz",
                ephemeral=True
            )
            return False

        channel = interaction.user.voice.channel

        if owner_channels.get(channel.id) != interaction.user.id:

            await interaction.response.send_message(
                "❌ Solo el dueño del canal puede usar el panel",
                ephemeral=True
            )
            return False

        return True

    @discord.ui.button(label="🔒 Lock", style=discord.ButtonStyle.red)
    async def lock(self, interaction: discord.Interaction, button: discord.ui.Button):

        channel = interaction.user.voice.channel
        await channel.set_permissions(interaction.guild.default_role, connect=False)

        await interaction.response.send_message("🔒 Canal bloqueado", ephemeral=True)

    @discord.ui.button(label="🔓 Unlock", style=discord.ButtonStyle.green)
    async def unlock(self, interaction: discord.Interaction, button: discord.ui.Button):

        channel = interaction.user.voice.channel
        await channel.set_permissions(interaction.guild.default_role, connect=True)

        await interaction.response.send_message("🔓 Canal abierto", ephemeral=True)

    @discord.ui.button(label="👥 Limit 5", style=discord.ButtonStyle.blurple)
    async def limit(self, interaction: discord.Interaction, button: discord.ui.Button):

        channel = interaction.user.voice.channel
        await channel.edit(user_limit=5)

        await interaction.response.send_message("👥 Límite 5", ephemeral=True)

    @discord.ui.button(label="🎲 Random Name", style=discord.ButtonStyle.gray)
    async def randomname(self, interaction: discord.Interaction, button: discord.ui.Button):

        channel = interaction.user.voice.channel
        name = random.choice(room_names)

        await channel.edit(name=name)

        await interaction.response.send_message("🎲 Nombre cambiado", ephemeral=True)
    
    


@bot.event
async def on_ready():
    print(f"Bot listo {bot.user}")


@bot.event
async def on_voice_state_update(member, before, after):

    global allowed_role

    # CREAR CANAL
    if after.channel and after.channel.id == CREATE_CHANNEL_ID:

        # verificar rol permitido
        if allowed_role:
            role = member.guild.get_role(allowed_role)

            if role not in member.roles:
                await member.move_to(None)
                return

        guild = member.guild
        category = after.channel.category

        name = random.choice(room_names)

        channel = await guild.create_voice_channel(name, category=category)

        await member.move_to(channel)

        owner_channels[channel.id] = member.id

        # canal privado de control
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True),
            guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        text_channel = await guild.create_text_channel(
            name=f"control-{member.name}",
            category=category,
            overwrites=overwrites
        )

        control_channels[channel.id] = text_channel.id

        await text_channel.send(
            "🎛 **Panel de control de la sala**",
            view=VoicePanel()
        )


    # BORRAR CANAL VACIO
    if before.channel and before.channel.id in owner_channels:

        if len(before.channel.members) == 0:

            if before.channel.id in control_channels:

                text = bot.get_channel(control_channels[before.channel.id])

                if text:
                    await text.delete()

                control_channels.pop(before.channel.id)

            owner_channels.pop(before.channel.id)

            await before.channel.delete()
    if after.channel and after.channel.id in owner_channels:
        await update_channel_name(after.channel)

    if before.channel and before.channel.id in owner_channels:
     await update_channel_name(before.channel)   


# COMANDO ADMIN PARA ROL
@bot.command()
@commands.has_permissions(administrator=True)
async def setrol(ctx, role: discord.Role):

    global allowed_role
    allowed_role = role.id

    await ctx.send(f"✅ Rol permitido para crear salas: {role.name}")


@bot.command()
async def invite(ctx, member: discord.Member):

    channel = ctx.author.voice.channel

    await channel.set_permissions(member, connect=True)

    await ctx.send(f"👥 {member.mention} invitado")


@bot.command()
async def kick(ctx, member: discord.Member):

    await member.move_to(None)

    await ctx.send("🚫 Usuario expulsado")


@bot.command()
async def mute(ctx, member: discord.Member):

    await member.edit(mute=True)

    await ctx.send("🔇 Usuario muteado")


@bot.command()
async def transfer(ctx, member: discord.Member):

    channel = ctx.author.voice.channel

    owner_channels[channel.id] = member.id

    await ctx.send(f"👑 Nuevo dueño: {member.mention}")


@bot.command()
async def limit(ctx, number: int):

    channel = ctx.author.voice.channel

    await channel.edit(user_limit=number)

    await ctx.send(f"👥 Límite {number}")


@bot.command()
async def name(ctx, *, name):

    channel = ctx.author.voice.channel

    await channel.edit(name=name)

    await ctx.send("✏ Nombre cambiado")


@bot.command()
async def users(ctx):

    channel = ctx.author.voice.channel

    await ctx.send(f"📊 Usuarios: {len(channel.members)}")


bot.run("MTQ4MDE3OTUyNjQ4MjAwMjA5Nw.GPGFhp.yKN15dwBuX_acGnfUzng8wISalcTJWt0tacx34")