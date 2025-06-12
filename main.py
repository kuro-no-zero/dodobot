import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button, Select
from discord import Interaction, Embed
import os
from flask import Flask
from threading import Thread
from pymongo import MongoClient
from dotenv import load_dotenv

# === Lista degli ID dei ruoli autorizzati ===

AUTHORIZED_ROLE_IDS = [1380464896520486922, 1380514524871786607]

# === Lista Dinos ===

redeemable_dinos = {
    "Blood Crystal Wyvern": {"livello": 115, "punti": 300},
    "Bloodstalker": {"livello": 150, "punti": 150},
    "Ember Crystal Wyvern": {"livello": 115, "punti": 300},
    "Enforcer": {"livello": 150, "punti": 100},
    "Managarmr": {"livello": 150, "punti": 320},
    "Noglin": {"livello": 150, "punti": 450},
    "Phoenix": {"livello": 150, "punti": 300},
    "Reaper-King": {"livello": 150, "punti": 400},
    "Tek Stryder (random)": {"livello": 150, "punti": 270},
    "Tropical Crystal Wyvern": {"livello": 115, "punti": 300},
    "Voidwyrm": {"livello": 115, "punti": 400},
    "Zombie-Wyvern": {"livello": 115, "punti": 350},
    "Rock Drake": {"livello": 115, "punti": 300},
    "Andrewsarchus": {"livello": 150, "punti": 170},
    "Desmodus": {"livello": 150, "punti": 270},
    "Fjordhawk": {"livello": 150, "punti": 100},
    "Deinonychus": {"livello": 75, "punti": 200},
    "Gacha (Random)": {"livello": 150, "punti": 150},
    "Gasbags": {"livello": 150, "punti": 100},
    "Velonasaur": {"livello": 150, "punti": 170},
    "Desert Titan": {"livello": "-", "punti": 1000},
    "Forest Titan": {"livello": "-", "punti": 900},
    "Ice Titan": {"livello": "-", "punti": 1200},
    "Bulbdog": {"livello": 150, "punti": 30},
    "Featherlight": {"livello": 150, "punti": 30},
    "Glowtail": {"livello": 150, "punti": 30},
    "Shinehorn": {"livello": 150, "punti": 30},
    "Karkinos": {"livello": 150, "punti": 250},
    "Roll Rat": {"livello": 150, "punti": 150},
    "Shadowmane": {"livello": 150, "punti": 350},
    "Megachelon": {"livello": 150, "punti": 150},
    "Carcharodontosaurus": {"livello": 150, "punti": 400}
}

# === Liste Achievements ===

achievements_oneshot = {
    "Primo Passo": {"punti": 50, "descrizione": "Completa il tutorial iniziale."},
    "Esploratore": {"punti": 100, "descrizione": "Visita 10 diverse aree del server."},
    "Campione": {"punti": 250, "descrizione": "Vinci 5 partite consecutive."},
}

achievements_infiniti = {
    "Mangia 'na foglia": {"punti": 50, "descrizione": "Hai bisogno di altri dettagli, coglione?"},
    "Uccidi Alessia": {"punti": 100, "descrizione": "Uccidi Alessia in maniera creativa"},
    "Tortura Patata": {"punti": 250, "descrizione": "Fai provare le pene dell'inferno a quello schifo di listrosauro"},
}

all_achievement_lists = {
    "OneShot": (achievements_oneshot, True, discord.Color.green()),
    "Infiniti": (achievements_infiniti, False, discord.Color.blue()),
}

sent_messages = []
sent_messages_redeem = []
PAGE_SIZE = 25
ITEMS_PER_PAGE = 25

# === FLASK: mini server web per Replit/UptimeRobot ===
app = Flask('')

@app.route('/')
def home():
    return "Il bot è attivo!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_web).start()

# === VARIABILI AMBIENTE ===

load_dotenv()

TOKEN = os.getenv("TOKEN")         # Token bot Discord
MONGO_URI = os.getenv("MONGO_URI") # URI MongoDB Atlas
print("MONGO_URI:", MONGO_URI)

# === CONNESSIONE MONGODB ===
client = MongoClient(MONGO_URI)
db = client["ark_bot_db"]              # Nome database
punti_collection = db["punti"]         # Collezione per i punti
redeemed_collection = db["redeemed"]   # Nuova collezione per tracciare i redeem
achievements_collection = db["achievements"]

# === FUNZIONI DB ===
def get_punti(user_id):
    doc = punti_collection.find_one({"_id": str(user_id)})
    return doc["punti"] if doc else 0

def set_punti(user_id, valore):
    punti_collection.update_one(
        {"_id": str(user_id)},
        {"$set": {"punti": valore}},
        upsert=True  # Se non esiste, crea
    )

# === FUNZIONI DI CONTROLLO ===

def is_authorized(interaction: discord.Interaction) -> bool:
    """Verifica se l'utente ha uno dei ruoli autorizzati."""
    return any(role.id in AUTHORIZED_ROLE_IDS for role in interaction.user.roles)

# VISTA con bottoni per ogni dinosauro
class DinoRedeemSelect(discord.ui.Select):
    def __init__(self, user_id, dinos, page):
        self.user_id = user_id
        # Ordina alfabeticamente i dinosauri per nome
        items = sorted(dinos.items(), key=lambda x: x[0])
        self.dinos = dict(items)
        self.page = page

        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        current_slice = items[start:end]

        options = [
            discord.SelectOption(
                label=dino_name,
                description=f"Costa {dino_info['punti']} punti",
                value=dino_name
            ) for dino_name, dino_info in current_slice
        ]

        super().__init__(
            placeholder="Scegli un dinosauro da riscattare...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        chosen_dino = self.values[0]
        dino_info = self.dinos.get(chosen_dino)

        if dino_info is None:
            await interaction.response.send_message("Errore: dinosauro non trovato.", ephemeral=True)
            return

        punti_utente = get_punti(interaction.user.id)
        if punti_utente < dino_info["punti"]:
            await interaction.response.send_message(
                "Non hai abbastanza punti per riscattare questa creatura.",
                ephemeral=True
            )
            return

        # Aggiorna i punti
        set_punti(interaction.user.id, punti_utente - dino_info["punti"])

        # Inserisci il record del redeem
        user_id_str = str(interaction.user.id)
        redeemed_collection.insert_one({
            "_id": f"{user_id_str}_{chosen_dino}_{interaction.id}",
            "user_id": user_id_str,
            "nome": chosen_dino,
            "punti": dino_info["punti"],
            "timestamp": interaction.created_at
        })

        # Rispondi all'interazione per evitare timeout (no messaggio visibile)
        await interaction.response.defer()

        # Manda il messaggio pubblico nel canale dell'interazione
        await interaction.channel.send(
            f"**{interaction.user.display_name}** ha riscattato **{chosen_dino}** per {dino_info['punti']} punti!"
        )

class DinoRedeemView(discord.ui.View):
    def __init__(self, user_id, dinos):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.dinos = dinos
        self.page = 0

        # Aggiungo il select per la pagina 0
        self.add_item(DinoRedeemSelect(user_id, dinos, self.page))

    async def update_select(self, interaction):
        # Rimuovo il vecchio select e aggiungo uno nuovo per la pagina aggiornata
        self.clear_items()
        # Se non siamo alla prima pagina, aggiungo il bottone indietro
        if self.page > 0:
            self.add_item(self.prev_button)
        # Se non siamo all'ultima pagina, aggiungo il bottone avanti
        if (self.page + 1) * PAGE_SIZE < len(self.dinos):
            self.add_item(self.next_button)

        # Aggiungo il nuovo select
        self.add_item(DinoRedeemSelect(self.user_id, self.dinos, self.page))
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Indietro", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Non puoi usare questo pulsante.", ephemeral=True)
            return
        if self.page > 0:
            self.page -= 1
            await self.update_select(interaction)

    @discord.ui.button(label="Avanti", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Non puoi usare questo pulsante.", ephemeral=True)
            return
        if (self.page + 1) * PAGE_SIZE < len(self.dinos):
            self.page += 1
            await self.update_select(interaction)

class AchievementsMenuView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.list_names = list(all_achievement_lists.keys())
        self.list_page = 0  # pagina tra le liste
        self.ach_page = 0   # pagina tra gli achievement nella lista selezionata

        self.selected_list_name = self.list_names[self.list_page]
        self.selected_ach_name = None  # inizialmente nessun achievement selezionato

        # Menu dropdown per scegliere lista (paginato)
        self.list_select = Select(
            placeholder="Seleziona categoria achievement",
            options=self.get_list_options(),
            custom_id="select_list"
        )
        self.list_select.callback = self.list_select_callback
        self.add_item(self.list_select)

        # Menu dropdown per scegliere achievement
        self.ach_select = Select(
            placeholder="Seleziona achievement",
            options=self.get_achievement_options(),
            custom_id="select_achievement"
        )
        self.ach_select.callback = self.ach_select_callback
        self.add_item(self.ach_select)

        # Bottoni di navigazione pagine liste e achievement
        self.prev_list_btn = Button(label="← Lista prec.", style=discord.ButtonStyle.secondary, custom_id="prev_list")
        self.prev_list_btn.callback = self.prev_list_callback
        self.next_list_btn = Button(label="Lista succ. →", style=discord.ButtonStyle.secondary, custom_id="next_list")
        self.next_list_btn.callback = self.next_list_callback

        self.prev_ach_btn = Button(label="← Ach prec.", style=discord.ButtonStyle.secondary, custom_id="prev_ach")
        self.prev_ach_btn.callback = self.prev_ach_callback
        self.next_ach_btn = Button(label="Ach succ. →", style=discord.ButtonStyle.secondary, custom_id="next_ach")
        self.next_ach_btn.callback = self.next_ach_callback

        self.complete_btn = Button(label="Completato", style=discord.ButtonStyle.success, custom_id="complete_achievement")
        self.complete_btn.callback = self.complete_callback

        self.add_item(self.prev_list_btn)
        self.add_item(self.next_list_btn)
        self.add_item(self.prev_ach_btn)
        self.add_item(self.next_ach_btn)
        self.add_item(self.complete_btn)

    def get_list_options(self):
        # Paginazione liste
        start = self.list_page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        options = []
        for nome in self.list_names[start:end]:
            options.append(discord.SelectOption(label=nome, value=nome))
        return options

    def get_achievement_options(self):
        ach_dict, _, _ = all_achievement_lists[self.selected_list_name]
        ach_names = sorted(ach_dict.keys())
        start = self.ach_page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE
        options = []
        for nome in ach_names[start:end]:
            options.append(discord.SelectOption(label=nome, value=nome))
        # Se non ci sono achievement per la pagina, metti opzione vuota
        if not options:
            options.append(discord.SelectOption(label="Nessun achievement", value="none", default=True))
        return options

    async def update_view(self, interaction: Interaction):
        # Aggiorna le options dei dropdown
        self.list_select.options = self.get_list_options()
        self.ach_select.options = self.get_achievement_options()

        # Aggiorna selezione corrente dropdown
        # Se l'achievement selezionato non è nella pagina aggiorna a primo della pagina o none
        ach_options = [opt.value for opt in self.ach_select.options]
        if self.selected_ach_name not in ach_options:
            self.selected_ach_name = ach_options[0] if ach_options else None
        self.list_select.default_values = [self.selected_list_name]
        self.ach_select.default_values = [self.selected_ach_name] if self.selected_ach_name else []

        # Aggiorna embed per mostrare info achievement selezionato
        ach_dict, one_shot, color = all_achievement_lists[self.selected_list_name]
        if self.selected_ach_name in ach_dict:
            dati = ach_dict[self.selected_ach_name]
            embed = Embed(title=self.selected_ach_name, color=color)
            embed.add_field(name="Descrizione", value=dati["descrizione"], inline=False)
            embed.add_field(name="Punti", value=str(dati["punti"]), inline=True)
        else:
            embed = Embed(title="Seleziona un achievement", description="Nessun achievement selezionato", color=discord.Color.dark_gray())

        await interaction.response.edit_message(embed=embed, view=self)

    async def list_select_callback(self, interaction: Interaction):
        self.selected_list_name = interaction.data["values"][0]
        self.ach_page = 0  # reset pagina achievement
        self.selected_ach_name = None
        await self.update_view(interaction)

    async def ach_select_callback(self, interaction: Interaction):
        self.selected_ach_name = interaction.data["values"][0]
        await self.update_view(interaction)

    async def prev_list_callback(self, interaction: Interaction):
        if self.list_page > 0:
            self.list_page -= 1
            self.selected_list_name = self.list_names[self.list_page * ITEMS_PER_PAGE]  # seleziona primo della pagina
            self.ach_page = 0
            self.selected_ach_name = None
            await self.update_view(interaction)
        else:
            await interaction.response.defer()  # no action

    async def next_list_callback(self, interaction: Interaction):
        max_page = (len(self.list_names) - 1) // ITEMS_PER_PAGE
        if self.list_page < max_page:
            self.list_page += 1
            self.selected_list_name = self.list_names[self.list_page * ITEMS_PER_PAGE]
            self.ach_page = 0
            self.selected_ach_name = None
            await self.update_view(interaction)
        else:
            await interaction.response.defer()

    async def prev_ach_callback(self, interaction: Interaction):
        if self.ach_page > 0:
            self.ach_page -= 1
            self.selected_ach_name = None
            await self.update_view(interaction)
        else:
            await interaction.response.defer()

    async def next_ach_callback(self, interaction: Interaction):
        ach_dict, _, _ = all_achievement_lists[self.selected_list_name]
        max_page = (len(ach_dict) - 1) // ITEMS_PER_PAGE
        if self.ach_page < max_page:
            self.ach_page += 1
            self.selected_ach_name = None
            await self.update_view(interaction)
        else:
            await interaction.response.defer()

    async def complete_callback(self, interaction: Interaction):
        if not self.selected_ach_name or self.selected_ach_name == "none":
            await interaction.response.send_message("Seleziona un achievement valido prima di completarlo.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        ach_dict, one_shot, _ = all_achievement_lists[self.selected_list_name]
        dati = ach_dict[self.selected_ach_name]
        punti_utente = get_punti(interaction.user.id)

        if one_shot:
            # Verifica se già completato
            if achievements_collection.find_one({"user_id": user_id, "achievement": self.selected_ach_name}):
                await interaction.response.send_message(
                    f"Hai già completato l'achievement **{self.selected_ach_name}**!",
                    ephemeral=True
                )
                return

        set_punti(interaction.user.id, punti_utente + dati["punti"])

        achievements_collection.insert_one({
            "user_id": user_id,
            "achievement": self.selected_ach_name,
            "punti": dati["punti"],
            "timestamp": interaction.created_at,
            "one_shot": one_shot
        })

        await interaction.response.send_message(
            f"Hai completato l'achievement **{self.selected_ach_name}** e guadagnato {dati['punti']} punti! 🎉",
            ephemeral=True
        )

        
# === BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === COMANDI SLASH ===
@bot.command()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("Comandi sincronizzati con successo!")

@bot.tree.command(name="punti", description="Mostra i punti di un utente")
@app_commands.describe(membro="L'utente da controllare")
async def punti(interaction: discord.Interaction, membro: discord.Member = None):
    membro = membro or interaction.user
    punti = get_punti(membro.id)
    await interaction.response.send_message(f"{membro.display_name} ha {punti} punti.")

@bot.tree.command(name="aggiungi", description="Aggiungi punti a un utente")
@app_commands.describe(membro="L'utente a cui aggiungere punti", quantita="Numero di punti da aggiungere")
async def aggiungi(interaction: discord.Interaction, membro: discord.Member, quantita: int):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return
    attuali = get_punti(membro.id)
    set_punti(membro.id, attuali + quantita)
    await interaction.response.send_message(f"{quantita} punti aggiunti a {membro.display_name}.")

@bot.tree.command(name="togli", description="Togli punti a un utente")
@app_commands.describe(membro="L'utente a cui togliere punti", quantita="Numero di punti da togliere")
async def togli(interaction: discord.Interaction, membro: discord.Member, quantita: int):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return
    attuali = get_punti(membro.id)
    nuovi = max(attuali - quantita, 0)
    set_punti(membro.id, nuovi)
    await interaction.response.send_message(f"{quantita} punti rimossi da {membro.display_name}.")

@bot.tree.command(name="classifica", description="Mostra la classifica dei punti")
async def classifica(interaction: discord.Interaction):
    top = punti_collection.find().sort("punti", -1).limit(10)
    embed = discord.Embed(title="Classifica Punti", color=discord.Color.gold())

    posizione = 1
    for doc in top:
        user_id = int(doc["_id"])
        punti = doc["punti"]
        membro = interaction.guild.get_member(user_id)
        if membro:
            nome = membro.display_name
        else:
            try:
                user = await bot.fetch_user(user_id)
                nome = user.name
            except:
                nome = f"Utente ID {user_id}"
        embed.add_field(name=f"{posizione}. {nome}", value=f"{punti} punti", inline=False)
        posizione += 1

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rimuovi", description="Rimuove un utente dalla classifica")
@app_commands.describe(membro="L'utente da rimuovere")
async def rimuovi(interaction: discord.Interaction, membro: discord.Member):
    # Verifica se l'utente ha i permessi di amministratore
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    # Rimuove il documento dal database
    result = punti_collection.delete_one({"_id": str(membro.id)})

    if result.deleted_count == 1:
        await interaction.response.send_message(f"{membro.display_name} è stato rimosso dalla classifica.")
    else:
        await interaction.response.send_message(f"{membro.display_name} non era presente nella classifica.")

    # Comando per far scegliere il dinosauro
@bot.tree.command(name="lista_redeem")
async def lista_redeem(interaction: discord.Interaction):
    user_id = interaction.user.id
    view = DinoRedeemView(user_id, redeemable_dinos)
    await interaction.response.send_message("Scegli il dinosauro da redeemare:", view=view, ephemeral=True)
    

@bot.tree.command(name="mostra_redeem", description="Mostra log redeem dinosauri (solo admin)")
async def mostra_redeem(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    docs = list(redeemed_collection.find().sort("timestamp", 1))
    if not docs:
        await interaction.response.send_message("Nessun redeem registrato.", ephemeral=True)
        return

    lines = []
    for doc in docs:
        user = await bot.fetch_user(int(doc["user_id"]))
        lines.append(f"- {user.name} ha riscattato **{doc['nome']}** per {doc['punti']} pt")

    message = "📋 **Log Redeem:**\n" + "\n".join(lines)
    await interaction.response.send_message(message, ephemeral=True)

@bot.tree.command(name="clear_redeem", description="Pulisce la lista dei redeem (solo admin)")
async def clear_redeem(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    result = redeemed_collection.delete_many({})  # Cancella tutti i record
    deleted = result.deleted_count

    await interaction.response.send_message(
        f"✅ Eliminati **{deleted}** record di redeem.",
        ephemeral=True
    )

@bot.tree.command(name="patata", description="Inutile")
async def patata(interaction: discord.Interaction):
    
    # URL dell'immagine
    image_url = "https://www.dododex.com/media/creature/lystrosaurus.png"

    # Crea l'embed
    embed = discord.Embed(
        title="In memory of Patata",
        description="11/09/2024",
        color=discord.Color.blue()
    )
    embed.set_image(url=image_url)

    # Invia il messaggio con l'embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="regole_1vs1", description="Le regole per le sfide 1vs1")
async def regole_1vs1(interaction: discord.Interaction):
    
    # Crea l'embed
    embed = discord.Embed(
        title="Regole per le sfide 1vs1",
        description="TBA",
        color=discord.Color.green()
    )

    # Invia il messaggio con l'embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="regole_achievement", description="Come ottenere punti attraverso gli achievement custom")
async def regole_achievement(interaction: discord.Interaction):

    # Crea l'embed
    embed = discord.Embed(
        title="Come usare il file di spreadheets",
        description="TBA",
        color=discord.Color.green()
    )

    # Invia il messaggio con l'embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="lista_achievements_infiniti", description="Mostra gli achievement infiniti")
async def lista_achievements_infiniti(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    for nome, dati in sorted(achievements_infiniti.items()):
        embed = discord.Embed(title=nome, color=discord.Color.blue())
        embed.add_field(name="Descrizione", value=dati["descrizione"], inline=False)
        embed.add_field(name="Punti", value=str(dati["punti"]), inline=True)
        view = InfiniteAchievementView(nome, dati["punti"], dati["descrizione"], False)
        msg = await interaction.followup.send(embed=embed, view=view)
        sent_messages.append(msg)

@bot.tree.command(name="lista_achievements_oneshot", description="Mostra gli achievement one-shot")
async def lista_achievements_oneshot(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=True)
    for nome, dati in sorted(achievements_oneshot.items()):
        embed = discord.Embed(title=nome, color=discord.Color.green())
        embed.add_field(name="Descrizione", value=dati["descrizione"], inline=False)
        embed.add_field(name="Punti", value=str(dati["punti"]), inline=True)
        view = OneShotAchievementView(nome, dati["punti"], dati["descrizione"], True)
        msg = await interaction.followup.send(embed=embed, view=view)
        sent_messages.append(msg)

@bot.tree.command(name="lista_achievement", description="Naviga tra le liste e achievement")
async def lista_achievement(interaction: Interaction):
    view = AchievementsMenuView()
    # Embed iniziale della prima lista e primo achievement
    ach_dict, one_shot, color = all_achievement_lists[view.selected_list_name]
    first_ach_name = sorted(ach_dict.keys())[0] if ach_dict else None

    if first_ach_name:
        dati = ach_dict[first_ach_name]
        embed = Embed(title=first_ach_name, color=color)
        embed.add_field(name="Descrizione", value=dati["descrizione"], inline=False)
        embed.add_field(name="Punti", value=str(dati["punti"]), inline=True)
    else:
        embed = Embed(title="Nessun achievement", description="Non ci sono achievement da mostrare.", color=discord.Color.dark_gray())

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="achievements_history", description="Mostra gli achievement completati (solo admin)")
async def mostra_achievements(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    docs = list(achievements_collection.find().sort("timestamp", 1))
    if not docs:
        await interaction.response.send_message("Nessun achievement registrato.", ephemeral=True)
        return

    lines = []
    for doc in docs:
        user = await bot.fetch_user(int(doc["user_id"]))
        lines.append(f"- {user.name} ha completato **{doc['achievement']}** per {doc['punti']} pt")

    message = "📋 **Log Achievement:**\n" + "\n".join(lines)
    await interaction.response.send_message(message, ephemeral=True)

@bot.tree.command(name="clear_achievements", description="Elimina tutti gli achievement completati (solo admin)")
async def clear_achievements(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    # Elimina tutti i documenti dalla collezione "achievements"
    result = achievements_collection.delete_many({})

    # Verifica se sono stati eliminati dei documenti
    if result.deleted_count > 0:
        await interaction.response.send_message(f"✅ Eliminati **{result.deleted_count}** achievement completati.", ephemeral=True)
    else:
        await interaction.response.send_message("Nessun achievement da eliminare.", ephemeral=True)

# === AVVIO BOT ===
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sincronizza i comandi slash
    print(f'Bot online come {bot.user}!')

bot.run(TOKEN)
