import discord
from discord.ext import commands
from discord import app_commands
from discord import SelectOption
from discord.ui import View, Button, Select
from discord import Interaction, Embed
import os
from flask import Flask
from threading import Thread
from pymongo import MongoClient
from dotenv import load_dotenv
from discord import ButtonStyle
from discord.app_commands import CommandTree
import io
import math
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from typing import Optional, List, Dict
from typing import Literal
import aiohttp
import base64
import logging
import pytz
from discord import ui

# === Lista degli ID dei ruoli autorizzati ===

AUTHORIZED_ROLE_IDS = [1380464896520486922, 1380514524871786607]

# === Lista Dinos ===

redeemable_dinos = {
    "Blood Crystal Wyvern": {
        "livello": 115, 
        "punti": 300, 
        "img": "https://i.ebayimg.com/00/s/OTAwWDE2MDA=/z/gV0AAOSwLpNjFBVI/$_57.JPG?set_id=8800005007"
    },
    "Bloodstalker": {
        "livello": 150, 
        "punti": 150, 
        "img": "https://ark.wiki.gg/images/thumb/0/09/Mod_Ark_Eternal_Elemental_Poison_Bloodstalker_Image.jpg/1120px-Mod_Ark_Eternal_Elemental_Poison_Bloodstalker_Image.jpg?5d28dd"
    },
    "Ember Crystal Wyvern": {
        "livello": 115, 
        "punti": 300, 
        "img": "https://i.ytimg.com/vi/jKOerbUz1Hg/maxresdefault.jpg"
    },
    "Enforcer": {
        "livello": 150, 
        "punti": 100, 
        "img": "https://pbs.twimg.com/media/Eknf-gkW0AYZ7L6?format=jpg&name=large"
    },
    "Managarmr": {
        "livello": 150, 
        "punti": 320, 
        "img": "https://i.ytimg.com/vi/TbVFs6y9ilg/maxresdefault.jpg"
    },
    "Noglin": {
        "livello": 150, 
        "punti": 450, 
        "img": "https://i.ytimg.com/vi/YeYQfVg1YZs/maxresdefault.jpg"
    },
    "Phoenix": {
        "livello": 150, 
        "punti": 300, 
        "img": "https://steamuserimages-a.akamaihd.net/ugc/856103154384245641/0CB31FB17AB3D46BF1DCC9854DF7D05664C12B54/"
    },
    "Reaper-King": {
        "livello": 150, 
        "punti": 400, 
        "img": "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/c/c6/Mod_Primal_Fear_Apex_Reaper_King_Image.jpg/revision/latest?cb=20190103234958"
    },
    "Tek Stryder (random)": {
        "livello": 150, 
        "punti": 270, 
        "img": "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/3/31/Tek_Stryder_image.png/revision/latest?cb=20210604204304"
    },
    "Tropical Crystal Wyvern": {
        "livello": 115, 
        "punti": 300, 
        "img": "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/7/7c/Crystal_Wyvern_Image.jpg/revision/latest?cb=20200614011556"
    },
    "Voidwyrm": {
        "livello": 115, 
        "punti": 400, 
        "img": "https://static0.gamerantimages.com/wordpress/wp-content/uploads/2021/09/ark-survival-evolved-voidwyrm.jpg"
    },
    "Zombie-Wyvern": {
        "livello": 115, 
        "punti": 350, 
        "img": "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/3/30/FearEvolved2_ZombieWyvern.jpg/revision/latest?cb=20161028192348"
    },
    "Rock Drake": {
        "livello": 115, 
        "punti": 300, 
        "img": "https://i.ebayimg.com/images/g/eowAAOSwBAlnRjAZ/s-l1200.png"
    },
    "Andrewsarchus": {
        "livello": 150, 
        "punti": 170, 
        "img": "https://progametalk.com/wp-content/uploads/2022/06/AKANDREW-1.png"
    },
    "Desmodus": {
        "livello": 150, 
        "punti": 270, 
        "img": "https://clan.fastly.steamstatic.com/images/8729288/e43a622433366d5965501ddb9a031465e093a2d7.png"
    },
    "Fjordhawk": {
        "livello": 150, 
        "punti": 100, 
        "img": "https://static1.srcdn.com/wordpress/wp-content/uploads/2025/02/fjordhawk-sitting-on-white-snow-from-ark-survival-ascended.jpg"
    },
    "Deinonychus": {
        "livello": 75, 
        "punti": 200, 
        "img": "https://ark.wiki.gg/images/thumb/2/29/Mod_Ark_Eternal_Elemental_Ice_DeinoNychus_Image.jpg/1008px-Mod_Ark_Eternal_Elemental_Ice_DeinoNychus_Image.jpg?79bb0e"
    },
    "Gacha (Random)": {
        "livello": 150, 
        "punti": 150, 
        "img": "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/e/ef/GachaThumbnail.png/revision/latest?cb=20181017121726"
    },
    "Gasbags": {
        "livello": 150, 
        "punti": 100, 
        "img": "https://static.deltiasgaming.com/2024/12/Gasbag-Ark-Survival-Ascended.png"
    },
    "Velonasaur": {
        "livello": 150, 
        "punti": 170, 
        "img": "https://www.ruletheark.com/media/2018/11/ark-velonasaur.png"
    },
    "Desert Titan": {
        "livello": "-", 
        "punti": 1000, 
        "img": "https://pbs.twimg.com/media/FlJ48rcWQAIL4Nm?format=jpg&name=4096x4096"
    },
    "Forest Titan": {
        "livello": "-", 
        "punti": 900, 
        "img": "https://images.steamusercontent.com/ugc/781854647701046233/E4D7CE7954493D5AA3D7AB789B9572D54CA4DEBB/?imw=637&imh=358&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true"
    },
    "Ice Titan": {
        "livello": "-", 
        "punti": 1200, 
        "img": "https://images.steamusercontent.com/ugc/796491253696633468/F9C76ADA2C49B384F43A03BA136C55C8D779E5FA/?imw=637&imh=358&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=true"
    },
    "Bulbdog": {
        "livello": 150, 
        "punti": 30, 
        "img": "https://www.ruletheark.com/media/2018/01/pug.png"
    },
    "Featherlight": {
        "livello": 150, 
        "punti": 30, 
        "img": "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/6/64/Mod_Primal_Fear_Fabled_Featherlight_Image.jpg/revision/latest/scale-to-width-down/1200?cb=20190225211224"
    },
    "Glowtail": {
        "livello": 150, 
        "punti": 30, 
        "img": "https://www.ruletheark.com/media/2018/04/lantern_lizard.jpg"
    },
    "Shinehorn": {
        "livello": 150, 
        "punti": 30, 
        "img": "https://ark.wiki.gg/images/thumb/9/90/Pris_shinehorn.png/1120px-Pris_shinehorn.png?cba0ed"
    },
    "Karkinos": {
        "livello": 150, 
        "punti": 250, 
        "img": "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/7/7b/Mod_Primal_Fear_Apex_Karkinos_Image.jpg/revision/latest?cb=20190103233928"
    },
    "Roll Rat": {
        "livello": 150, 
        "punti": 150, 
        "img": "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/5/50/Saddled_Roll_rat.png/revision/latest?cb=20201008181841"
    },
    "Shadowmane": {
        "livello": 150, 
        "punti": 350, 
        "img": "https://images.saymedia-content.com/.image/ar_4:3%2Cc_fill%2Ccs_srgb%2Cfl_progressive%2Cq_auto:eco%2Cw_1200/MTgyODA2ODAzMzQ2NzYxMDU2/ark-survival-evolved-the-ultimate-hunter-shadowmane.jpg"
    },
    "Megachelon": {
        "livello": 150, 
        "punti": 150, 
        "img": "https://static.wikia.nocookie.net/arksurvivalevolved_gamepedia/images/4/48/Genesis_3.jpg/revision/latest/scale-to-width-down/1120?cb=20190807211131"
    }
}

# === Lista Tribes ===

tribe_members = {
    "drake_tribe": [
        143237899603804161, #radu
        284988139011964928, #dodo
        804262403394502677  #sara
    ],
    "alessia_tribe": [
        693906313729802301, #alessia
        901090228792590346  #laura
    ],
    "lus_tribe": [
        285024740421402624  #lus
    ],
    "simonik_tribe": [
        522441364831469568, #nick
        254590376201945090  #simo
    ]
}

# === Liste Achievements ===

achievements_survival = {
    "Non è granchè, ma è casa": {
        "punti": 10,
        "descrizione": "Costruisci una struttura chiusa con un letto all'interno",
        "ripetibile": False
    },
    "Grazie coperte": {
        "punti": 10,
        "descrizione": "Indossa un indumento in ogni slot armatura",
        "ripetibile": False
    },
    "Età del metallo": {
        "punti": 20,
        "descrizione": "Ottieni il tuo primo oggetto in metallo",
        "ripetibile": False
    },
    "Come sei umano per essere un ark": {
        "punti": 10,
        "descrizione": "Ottieni del bottino dai beacons",
        "ripetibile": False
    },
    "Pollice verde": {
        "punti": 30,
        "descrizione": "Coltiva tutte le piante coltivabili",
        "ripetibile": False
    },
    "Ape maia": {
        "punti": 30,
        "descrizione": "Ottieni un alveare di api amichevoli",
        "ripetibile": False
    },
    "Asilo nido": {
        "punti": 50,
        "descrizione": "Breeda con successo un dino (no wyv eggs)",
        "ripetibile": False
    },
    "Scienziato della InGen": {
        "punti": 60,
        "descrizione": "Breeda con successo un ibrido",
        "ripetibile": False
    },
    "Questo non mi sembra normale": {
        "punti": 100,
        "descrizione": "Ottieni una mutazione su un dino",
        "ripetibile": False
    },
    "Mutante mutato": {
        "punti": 120,
        "descrizione": "Ottieni una mutazione su un ibrido",
        "ripetibile": False
    },
    "Modern Warfare": {
        "punti": 20,
        "descrizione": "Ottieni la tua prima arma da fuoco",
        "ripetibile": False
    },
    "100 lingotti a barile": {
        "punti": 30,
        "descrizione": "Piazza la tua prima pompa petrolifera",
        "ripetibile": False
    },
    "Lumiere": {
        "punti": 30,
        "descrizione": "Alimenta delle luci elettriche con un generatore",
        "ripetibile": False
    },
    "Brute Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Clever Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Cunning Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Devious Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Devourer Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Hunter Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Immune Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Massive Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Pack Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Skylord Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Strong Artifact": {
        "punti": 50,
        "descrizione": "Ottieni l'artefatto",
        "ripetibile": False
    },
    "Dinopithecus King Gamma": {
        "punti": 100,
        "descrizione": "Sconfiggi il boss a difficoltà gamma",
        "ripetibile": False
    },
    "Dinopithecus King Beta": {
        "punti": 150,
        "descrizione": "Sconfiggi il boss a difficoltà beta",
        "ripetibile": False
    },
    "Dinopithecus King Alpha": {
        "punti": 200,
        "descrizione": "Sconfiggi il boss a difficoltà alpha",
        "ripetibile": False
    },
    "Acro Selvaggio": {
        "punti": 200,
        "descrizione": "Sconfiggi il boss Acro Selvaggio",
        "ripetibile": False
    },
    "Back to the future": {
        "punti": 100,
        "descrizione": "Costruisci il tuo primo oggetto tek",
        "ripetibile": False
    },
    "Abominio Definitivo": {
        "punti": 400,
        "descrizione": "Sconfiggi e ottieni EelBoss",
        "ripetibile": False
    },
    "Cyber Dinosauro": {
        "punti": 400,
        "descrizione": "Sconfiggi e ottieni il Cyber Macrocercodraco",
        "ripetibile": False
    }
}

achievements_combat = {
    "Puoi usarlo come tagliaerba": {
        "punti": 10,
        "descrizione": "Tama il tuo primo erbivoro",
        "ripetibile": False
    },
    "Ogni tanto morde": {
        "punti": 10,
        "descrizione": "Tama il tuo primo carnivoro",
        "ripetibile": False
    },
    "Blue, Charlie, Delta, Echo": {
        "punti": 15,
        "descrizione": "Tama un branco di almeno 4 raptor",
        "ripetibile": False
    },
    "3 metri sopra il cielo": {
        "punti": 10,
        "descrizione": "Tama il tuo primo volatile",
        "ripetibile": False
    },
    "Aquila di Manwë": {
        "punti": 15,
        "descrizione": "Tama un argentavis",
        "ripetibile": False
    },
    "Diego": {
        "punti": 10,
        "descrizione": "Tama uno smilodonte",
        "ripetibile": False
    },
    "Horizon Zero Dawn": {
        "punti": 10,
        "descrizione": "Tama un dino tek",
        "ripetibile": False
    },
    "Amico inseparabile": {
        "punti": 5,
        "descrizione": "Tama un dino da spalla",
        "ripetibile": False
    },
    "Come un vero Targaryen": {
        "punti": 50,
        "descrizione": "Ottieni la tua prima viverna da un uovo",
        "ripetibile": False
    },
    "\"Me lo dica ancora...\" \"Ho un Tirannosaurus Rex.\"": {
        "punti": 20,
        "descrizione": "Tama un rex",
        "ripetibile": False
    },
    "Palla da demolizione": {
        "punti": 15,
        "descrizione": "Tama un dedicuro",
        "ripetibile": False
    },
    "Ma è una cosa aberrante!": {
        "punti": 10,
        "descrizione": "Tama un dino abberrante",
        "ripetibile": False
    },
    "In fondo al mar": {
        "punti": 10,
        "descrizione": "Tama un dino acquatico",
        "ripetibile": False
    },
    "A shark tale": {
        "punti": 15,
        "descrizione": "Tama un megalodonte",
        "ripetibile": False
    },
    "Hai provato con una carcassa di squalo?": {
        "punti": 50,
        "descrizione": "Tama un mosasauro",
        "ripetibile": False
    },
    "It's Fabulous!!": {
        "punti": 20,
        "descrizione": "Tama un unicorno",
        "ripetibile": False
    },
    "Lucertola infernale": {
        "punti": 50,
        "descrizione": "Ottieni un magmasauro da un uovo",
        "ripetibile": False
    },
    "Evoca il kraken": {
        "punti": 70,
        "descrizione": "Tama un tusoteutide",
        "ripetibile": False
    },
    "\"Il pubblico vuole 'più denti'\"": {
        "punti": 100,
        "descrizione": "Tama un giganotosauro",
        "ripetibile": False
    },
    "Non è brutalità ma sopravvivenza": {
        "punti": 5,
        "descrizione": "Uccidi il tuo primo dino",
        "ripetibile": False
    },
    "Addio venti freddi": {
        "punti": 30,
        "descrizione": "Uccidi una viverna (ghiaccio)",
        "ripetibile": False
    },
    "Dragon Slayer": {
        "punti": 50,
        "descrizione": "Uccidi una viverna per tipo (fuoco, veleno, fulmine)",
        "ripetibile": False
    },
    "Aspè...davvero?": {
        "punti": 200,
        "descrizione": "Uccidi un titanosauro",
        "ripetibile": False
    },
    "La prossima volta prova con il passo del deserto": {
        "punti": 50,
        "descrizione": "Uccidi un deathworm",
        "ripetibile": False
    },
    "Tu si che hai le palle": {
        "punti": 150,
        "descrizione": "Uccidi un giganotosauro",
        "ripetibile": False
    },
    "Sono io l'alpha": {
        "punti": 30,
        "descrizione": "Uccidi un raptor alpha",
        "ripetibile": False
    },
    "Diavolo rosso": {
        "punti": 50,
        "descrizione": "Uccidi un carnotauro alpha",
        "ripetibile": False
    },
    "Demone sovrano": {
        "punti": 70,
        "descrizione": "Uccidi un rex alpha",
        "ripetibile": False
    },
    "Lo squalo più grosso": {
        "punti": 50,
        "descrizione": "Uccidi un meg alpha",
        "ripetibile": False
    },
    "Mostro marino": {
        "punti": 70,
        "descrizione": "Uccidi un mosa alpha",
        "ripetibile": False
    },
    "Leggenda degli abissi": {
        "punti": 100,
        "descrizione": "Uccidi un tuso alpha",
        "ripetibile": False
    },
    "Ammazzadraghi leggendario": {
        "punti": 100,
        "descrizione": "Uccidi una viverna del fuoco alpha",
        "ripetibile": False
    },
    "Ma quindi esiste davvero!": {
        "punti": 100,
        "descrizione": "Tama un Liopleuridon",
        "ripetibile": False
    },
    "Dragon Trainer": {
        "punti": 100,
        "descrizione": "Ottieni una viverna per tipo (fuoco, elettro, veleno, ghiaccio)",
        "ripetibile": False
    },
    "Tuta alare vivente": {
        "punti": 10,
        "descrizione": "Tama un sinomacrops",
        "ripetibile": False
    },
    "Babbuino dispettoso": {
        "punti": 15,
        "descrizione": "Tama un Dinophitecus",
        "ripetibile": False
    },
    "Lanciarazzi preistorico": {
        "punti": 15,
        "descrizione": "Tama un Amargasauro",
        "ripetibile": False
    },
    "I bulletti al completo": {
        "punti": 20,
        "descrizione": "Ottieni un branco almeno 3 allosauri",
        "ripetibile": False
    },
    "Pare le sia piaciuto il pesce": {
        "punti": 5,
        "descrizione": "Tama una lontra",
        "ripetibile": False
    },
    "Siamo sicuri non sia malato?": {
        "punti": 10,
        "descrizione": "Tama un R dino",
        "ripetibile": False
    },
    "Sage mode unlocked": {
        "punti": 5,
        "descrizione": "Tama un belzebufo",
        "ripetibile": False
    },
    "Carro armato in miniatura": {
        "punti": 15,
        "descrizione": "Tama un ankylosauro",
        "ripetibile": False
    },
    "Leone preistorico": {
        "punti": 20,
        "descrizione": "Tama un leone marsupiale",
        "ripetibile": False
    },
    "Il WWF lo verrà a sapere": {
        "punti": 20,
        "descrizione": "Uccidi una balena",
        "ripetibile": False
    },
    "Moby Dick sconfitta": {
        "punti": 30,
        "descrizione": "Uccidi una balena alpha",
        "ripetibile": False
    },
    "Il cammello che non ti aspettavi": {
        "punti": 10,
        "descrizione": "Tama un morellatops",
        "ripetibile": False
    },
    "\"Allora cosa facciamo?\" \"Non lo so, tu cosa vuoi fare?\"": {
        "punti": 15,
        "descrizione": "Tama uno stormo di voltures (almeno 5)",
        "ripetibile": False
    },
    "Crocodile Dundee": {
        "punti": 15,
        "descrizione": "Tama un coccodrillo-like dino",
        "ripetibile": False
    },
    "Sardegna is coming": {
        "punti": 15,
        "descrizione": "Tama un ovis",
        "ripetibile": False
    },
    "Carne Gourmet": {
        "punti": 5,
        "descrizione": "Uccidi un ovis",
        "ripetibile": False
    },
    "Il tank furioso": {
        "punti": 50,
        "descrizione": "Tama un acrocanthosauro",
        "ripetibile": False
    },
    "\"Segui la corrente bwello!\"": {
        "punti": 10,
        "descrizione": "Tama un archelon",
        "ripetibile": False
    },
    "Da qui si vede casa mia!": {
        "punti": 15,
        "descrizione": "Tama un brachiosauro",
        "ripetibile": False
    },
    "Non mi serve l'acqua per nuotare": {
        "punti": 10,
        "descrizione": "Tama un concavenator",
        "ripetibile": False
    },
    "Ho avuto tanta paura": {
        "punti": 20,
        "descrizione": "Tama un deinosuco",
        "ripetibile": False
    },
    "Dunbo": {
        "punti": 10,
        "descrizione": "Tama un deinotherium",
        "ripetibile": False
    },
    "Meglio portarlo dal dentista": {
        "punti": 10,
        "descrizione": "Tama un xiphactinus",
        "ripetibile": False
    },
    "\"Metti la cera, togli la cera\"": {
        "punti": 15,
        "descrizione": "Tama un ceratosauro",
        "ripetibile": False
    },
    "Jigsaw": {
        "punti": 10,
        "descrizione": "Tama un Helicoprion",
        "ripetibile": False
    },
    "E' stato elettrizzante!": {
        "punti": 20,
        "descrizione": "Tama un Draconis Glaucus",
        "ripetibile": False
    },
    "Dalla wiki sembrava più facile": {
        "punti": 20,
        "descrizione": "Tama un basilosauro",
        "ripetibile": False
    },
    "Una scoperta scientifica incredibile": {
        "punti": 10,
        "descrizione": "Ottieni della biotossina",
        "ripetibile": False
    },
    "Ritorno alla lava": {
        "punti": 50,
        "descrizione": "Uccidi un magmasauro",
        "ripetibile": False
    },
    "Scoiattolo volante": {
        "punti": 15,
        "descrizione": "Tama un maewing",
        "ripetibile": False
    },
    "Edward mani di forbice": {
        "punti": 20,
        "descrizione": "Tama un terizinosauro",
        "ripetibile": False
    },
    "Come Timon e Pumba": {
        "punti": 10,
        "descrizione": "Tama un deodonte",
        "ripetibile": False
    },
    "Edvige": {
        "punti": 15,
        "descrizione": "Tama un gufo delle nevi",
        "ripetibile": False
    },
    "Duro come la roccia": {
        "punti": 100,
        "descrizione": "Tama un rock elemental",
        "ripetibile": False
    },
    "La vela della paura": {
        "punti": 20,
        "descrizione": "Tama uno spino",
        "ripetibile": False
    },
    "Il volo di Fierobecco": {
        "punti": 30,
        "descrizione": "Tama un grifone",
        "ripetibile": False
    },
    "Come una falena verso la fiamma": {
        "punti": 5,
        "descrizione": "Tama una limantria",
        "ripetibile": False
    },
    "Il pet di Salazar Serpeverde": {
        "punti": 50,
        "descrizione": "Uccidi un basilisco",
        "ripetibile": False
    },
    "Non fidarti della luce": {
        "punti": 15,
        "descrizione": "Tama un anglefish",
        "ripetibile": False
    },
    "Il ruggito del signore dei ghiacci": {
        "punti": 30,
        "descrizione": "Tama uno yutiranno",
        "ripetibile": False
    },
    "Dottor Jekyll & Mr. Hyde": {
        "punti": 70,
        "descrizione": "Tama un ferox",
        "ripetibile": False
    },
    "Grazie per aver volato con Ryanair": {
        "punti": 30,
        "descrizione": "Tama un quetzal",
        "ripetibile": False
    },
    "Abbiamo trovato Nessie": {
        "punti": 30,
        "descrizione": "Tama un plesiosauro",
        "ripetibile": False
    },
    "Ma quanto caghi?": {
        "punti": 5,
        "descrizione": "Tama una phioma",
        "ripetibile": False
    },
    "Supersonic-Ice-Jet Beast": {
        "punti": 50,
        "descrizione": "Tama un managarm",
        "ripetibile": False
    },
    "Il sacro appallottola merda": {
        "punti": 5,
        "descrizione": "Tama uno scarabeo stercorario",
        "ripetibile": False
    },
    "Furia sanguigna sbloccata": {
        "punti": 100,
        "descrizione": "Tama un Carcha",
        "ripetibile": False
    },
    "L'eroe che non sapevamo di meritare": {
        "punti": 150,
        "descrizione": "Uccidi un Carcha",
        "ripetibile": False
    },
    "Allora esistono davvero!": {
        "punti": 200,
        "descrizione": "Ottieni un ibrido Rogue",
        "ripetibile": False
    }
}

achievements_crafting = {
    "Utensili del mestiere": {
        "punti": 5,
        "descrizione": "Crafta ascia e piccone in pietra",
        "ripetibile": False
    },
    "Si spezza come un grissino": {
        "punti": 5,
        "descrizione": "Crafta una lancia",
        "ripetibile": False
    },
    "Come da bambini": {
        "punti": 5,
        "descrizione": "Crafta una fionda",
        "ripetibile": False
    },
    "Acchiappacavalli, ma più grandi": {
        "punti": 5,
        "descrizione": "Crafta dei bola",
        "ripetibile": False
    },
    "Robin Hood": {
        "punti": 5,
        "descrizione": "Crafta l'arco",
        "ripetibile": False
    },
    "Meglio di niente": {
        "punti": 5,
        "descrizione": "Crafta il set armatura in fibra",
        "ripetibile": False
    },
    "Camping all'aperto": {
        "punti": 5,
        "descrizione": "Crafta un sacco a pelo",
        "ripetibile": False
    },
    "Sembra comodo": {
        "punti": 5,
        "descrizione": "Crafta un letto",
        "ripetibile": False
    },
    "Spero non arrivi il lupo": {
        "punti": 5,
        "descrizione": "Crafta una casa in paglia",
        "ripetibile": False
    },
    "Fa un po prurito": {
        "punti": 15,
        "descrizione": "Crafta il set armatura in pelle",
        "ripetibile": False
    },
    "Il lupo fa fatica": {
        "punti": 15,
        "descrizione": "Crafta una casa in legno",
        "ripetibile": False
    },
    "Il lupo si fotte": {
        "punti": 10,
        "descrizione": "Crafta una casa in pietra",
        "ripetibile": False
    },
    "Ci puoi fare anche la pizza": {
        "punti": 5,
        "descrizione": "Crafta una fornace",
        "ripetibile": False
    },
    "Apothecary diaries": {
        "punti": 5,
        "descrizione": "Crafta il mortaio e pestello",
        "ripetibile": False
    },
    "Funziona davvero!": {
        "punti": 5,
        "descrizione": "Crafta il preserving bin",
        "ripetibile": False
    },
    "Olio di gomito": {
        "punti": 15,
        "descrizione": "Crafta il banco da lavoro",
        "ripetibile": False
    },
    "Pronti per le crociate": {
        "punti": 20,
        "descrizione": "Crafta il set armatura in ferro",
        "ripetibile": False
    },
    "Nani e vichinghi": {
        "punti": 5,
        "descrizione": "Crafta ascia e piccone in ferro",
        "ripetibile": False
    },
    "2 di picche": {
        "punti": 15,
        "descrizione": "Crafta la picca",
        "ripetibile": False
    },
    "Ora si ragiona": {
        "punti": 15,
        "descrizione": "Crafta la balestra",
        "ripetibile": False
    },
    "Meglio non sniffarlo": {
        "punti": 5,
        "descrizione": "Crafta il narcotico",
        "ripetibile": False
    },
    "Far west": {
        "punti": 20,
        "descrizione": "Crafta la pistola semplice",
        "ripetibile": False
    },
    "Old but gold": {
        "punti": 20,
        "descrizione": "Crafta il longneck rifle",
        "ripetibile": False
    },
    "Servono più munizioni": {
        "punti": 15,
        "descrizione": "Crafta dei proiettili",
        "ripetibile": False
    },
    "Con questi metti a nanna un elefante": {
        "punti": 15,
        "descrizione": "Crafta i dardi sedativi",
        "ripetibile": False
    },
    "Nikola Tesla": {
        "punti": 20,
        "descrizione": "Crafta un generatore",
        "ripetibile": False
    },
    "E luce fu!": {
        "punti": 20,
        "descrizione": "Crafta delle luci elettriche",
        "ripetibile": False
    },
    "Idraulica base": {
        "punti": 15,
        "descrizione": "Crafta un sistema di tubature per l'acqua",
        "ripetibile": False
    },
    "Fondiamo tutto!": {
        "punti": 15,
        "descrizione": "Crafta la fornace industriale",
        "ripetibile": False
    },
    "Cuociamo tutto!": {
        "punti": 10,
        "descrizione": "Crafta l'industrial grill",
        "ripetibile": False
    },
    "Ottima per qualche brodaglia": {
        "punti": 5,
        "descrizione": "Crafta la cucina da campo",
        "ripetibile": False
    },
    "Ristorante stellato": {
        "punti": 15,
        "descrizione": "Crafta la cucina industriale",
        "ripetibile": False
    },
    "Breaking Bad": {
        "punti": 15,
        "descrizione": "Crafta il banco chimico",
        "ripetibile": False
    },
    "Maciniamo tutto! (non erba)": {
        "punti": 15,
        "descrizione": "Crafta il grinder",
        "ripetibile": False
    },
    "Mettici i gelati": {
        "punti": 15,
        "descrizione": "Crafta il frigo",
        "ripetibile": False
    },
    "Fa un po male all'interno coscia": {
        "punti": 5,
        "descrizione": "Crafta una sella",
        "ripetibile": False
    },
    "Quella sotto il cuscino": {
        "punti": 15,
        "descrizione": "Crafta la pistola avanzata",
        "ripetibile": False
    },
    "Ratatatata": {
        "punti": 15,
        "descrizione": "Crafta il fucile automatico",
        "ripetibile": False
    },
    "Vuoi vedere una groviera?": {
        "punti": 15,
        "descrizione": "Crafta il fucile a pompa",
        "ripetibile": False
    },
    "Trickshot": {
        "punti": 15,
        "descrizione": "Crafta il fucile da cecchino",
        "ripetibile": False
    },
    "\"Una volta anch'io ero un avventuriero...\"": {
        "punti": 10,
        "descrizione": "Crafta un npc",
        "ripetibile": False
    },
    "B&B": {
        "punti": 15,
        "descrizione": "Costruisci una casa a due piani",
        "ripetibile": False
    },
    "Garden In": {
        "punti": 10,
        "descrizione": "Costruisci una serra (coperta in vetro)",
        "ripetibile": False
    },
    "Quartiere a luci rosse": {
        "punti": 5,
        "descrizione": "Costruisci una zona breeding",
        "ripetibile": False
    },
    "The Sims": {
        "punti": 5,
        "descrizione": "Arreda e decora la casa",
        "ripetibile": False
    },
    "R.I.P": {
        "punti": 5,
        "descrizione": "Costruisci una tomba",
        "ripetibile": False
    },
    "Con licenza": {
        "punti": 5,
        "descrizione": "Costruisci una statua di un dino",
        "ripetibile": False
    },
    "Meglio fuori che dentro": {
        "punti": 5,
        "descrizione": "Costruisci un gabinetto",
        "ripetibile": False
    },
    "A cuccia": {
        "punti": 15,
        "descrizione": "Costruisci una trappola per taming",
        "ripetibile": False
    },
    "Meglio del fosso di Helm": {
        "punti": 15,
        "descrizione": "Costruisci mura attorno alla tua base (in caso di elementi naturali tappare ogni possibile ingresso via terra)",
        "ripetibile": False
    },
    "Verso Narnia": {
        "punti": 5,
        "descrizione": "Crafta un armadio",
        "ripetibile": False
    },
    "Solo cose di valore": {
        "punti": 20,
        "descrizione": "Crafta una chest in metallo (bunker)",
        "ripetibile": False
    },
    "Skal!!": {
        "punti": 15,
        "descrizione": "Crafta della birra",
        "ripetibile": False
    },
    "Estus": {
        "punti": 15,
        "descrizione": "Crafta una pozione per la salute",
        "ripetibile": False
    },
    "Stimpack": {
        "punti": 15,
        "descrizione": "Crafta una pozione per il vigore",
        "ripetibile": False
    },
    "La mia patong": {
        "punti": 15,
        "descrizione": "Crafta un piatto (no carne cotta)",
        "ripetibile": False
    },
    "Chi sono io?": {
        "punti": 15,
        "descrizione": "Crafta il tonico scervellatore",
        "ripetibile": False
    },
    "Autan": {
        "punti": 5,
        "descrizione": "Crafta il repellente",
        "ripetibile": False
    },
    "Pronti alla rivolta": {
        "punti": 20,
        "descrizione": "Crafta il set armatura antisommossa",
        "ripetibile": False
    },
    "Nemmeno questo è ingeribile": {
        "punti": 15,
        "descrizione": "Crafta del polimero",
        "ripetibile": False
    },
    "It's Sci-Fi, really": {
        "punti": 50,
        "descrizione": "Crafta un generatore tek",
        "ripetibile": False
    },
    "Iron Man": {
        "punti": 100,
        "descrizione": "Crafta il set armatura tek",
        "ripetibile": False
    },
    "Trasmissione Istantanea": {
        "punti": 100,
        "descrizione": "Crafta il teletrasportatore",
        "ripetibile": False
    },
    "Forse stona un po ma ci piace": {
        "punti": 100,
        "descrizione": "Costruisci una base tek",
        "ripetibile": False
    },
    "Swoosh / Pew pew": {
        "punti": 20,
        "descrizione": "Crafta un'arma tek",
        "ripetibile": False
    },
    "Barriera impenetrabile": {
        "punti": 20,
        "descrizione": "Crafta il tek forcefield",
        "ripetibile": False
    },
    "Giochi a fare dio? 1": {
        "punti": 10,
        "descrizione": "Crafta un ibrido type 4",
        "ripetibile": False
    },
    "Giochi a fare dio? 2": {
        "punti": 15,
        "descrizione": "Crafta un ibrido type 3",
        "ripetibile": False
    },
    "Giochi a fare dio? 3": {
        "punti": 20,
        "descrizione": "Crafta un ibrido type 2",
        "ripetibile": False
    },
    "Giochi a fare dio? 4": {
        "punti": 25,
        "descrizione": "Crafta un ibrido type 1",
        "ripetibile": False
    },
    "Giochi a fare dio? 5": {
        "punti": 30,
        "descrizione": "Crafta un ibrido type A",
        "ripetibile": False
    },
    "Giochi a fare dio? 6": {
        "punti": 35,
        "descrizione": "Crafta un ibrido type S",
        "ripetibile": False
    },
    "Giochi a fare dio? 7": {
        "punti": 50,
        "descrizione": "Crafta un ibrido Operation type",
        "ripetibile": False
    },
    "La guerra dei cloni": {
        "punti": 150,
        "descrizione": "Crafta una camera di clonazione e clona un dino",
        "ripetibile": False
    }
}

all_achievement_lists = {
    "Survival": (achievements_survival, 0x2ecc71),
    "Combat": (achievements_combat, 0x3498db),
    "Crafting": (achievements_crafting, 0x8a2be2),
}

IMAGE_MAP = {
    "Small": {
        "Land": "https://i.imgur.com/g6fr4Me.png",
        "Flyers": "https://i.imgur.com/g6fr4Me.png",
        "Acquatic": "https://i.imgur.com/g6fr4Me.png",
    },
    "Medium": {
        "Land": "https://i.imgur.com/g6fr4Me.png",
        "Flyers": "https://i.imgur.com/g6fr4Me.png",
        "Acquatic": "https://i.imgur.com/g6fr4Me.png",
    },
    "Big": {
        "Land": "https://i.imgur.com/g6fr4Me.png",
        "Flyers": "https://i.imgur.com/g6fr4Me.png",
        "Acquatic": "https://i.imgur.com/g6fr4Me.png",
    },
    "Mega": {
        "Land": "https://i.imgur.com/g6fr4Me.png",
        "Flyers": "https://i.imgur.com/g6fr4Me.png",
        "Acquatic": "https://i.imgur.com/g6fr4Me.png",
    }
}

sent_messages = []
sent_messages_redeem = []
PAGE_SIZE = 25
ITEMS_PER_PAGE = 25
MAX_OPTIONS_PER_PAGE = 15
MAX_DESCRIPTION_LENGTH = 4000

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
duels_collection = db["duels"]

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

def get_tribe_id(user_id: int) -> str | None:
    for tribe_id, members in tribe_members.items():
        if user_id in members:
            return tribe_id
    return None

def get_tribe_members(user_id: int) -> list[int]:
    tribe_id = get_tribe_id(user_id)
    if tribe_id:
        return tribe_members[tribe_id]
    return [user_id]  # Se non ha tribe, considera solo se stesso

# === FUNZIONI DI CONTROLLO ===

def is_authorized(interaction: discord.Interaction) -> bool:
    """Verifica se l'utente ha uno dei ruoli autorizzati."""
    return any(role.id in AUTHORIZED_ROLE_IDS for role in interaction.user.roles)

# === VIEW DUELLI ===

class DuelResolutionView(discord.ui.View):
    def __init__(self, duels, user_id):
        super().__init__(timeout=300)
        self.duels = duels
        self.user_id = user_id
        self.page = 0

        self.duel_select = discord.ui.Select(
            placeholder="Scegli un duello da risolvere",
            min_values=1,
            max_values=1,
            options=[]
        )
        self.duel_select.callback = self.duel_select_callback
        self.add_item(self.duel_select)

        self.result_select = discord.ui.Select(
            placeholder="Seleziona il vincitore",
            options=[],
            custom_id="result_select"
        )
        self.result_select.callback = self.result_select_callback
        self.add_item(self.result_select)

        self.confirm_button = discord.ui.Button(label="✅ Conferma", style=discord.ButtonStyle.green)
        self.confirm_button.callback = self.confirm
        self.add_item(self.confirm_button)

        self.prev_button = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.secondary)
        self.prev_button.callback = self.prev_page
        self.add_item(self.prev_button)

        self.next_button = discord.ui.Button(label="➡️", style=discord.ButtonStyle.secondary)
        self.next_button.callback = self.next_page
        self.add_item(self.next_button)

        self.build_duel_options()

    def build_duel_options(self):
        self.duel_select.options.clear()
        start = self.page * 25
        end = start + 25
        page_duels = self.duels[start:end]

        for i, duel in enumerate(page_duels):
            label = f"{duel['challenger_name']} vs {duel['opponent_name']} - {duel['datetime'].strftime('%Y-%m-%d %H:%M')}"
            self.duel_select.options.append(
                discord.SelectOption(label=label[:100], value=str(start + i))
            )

        max_pages = math.ceil(len(self.duels) / 25)
        self.prev_button.disabled = (self.page == 0)
        self.next_button.disabled = (max_pages <= 1 or self.page >= max_pages - 1)

        # Se cambio pagina resetto selezioni e risultato
        #self.duel_select.values = []
        #self.result_select.values = []
        self.result_select.options = []

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def duel_select_callback(self, interaction: discord.Interaction):
        if not self.duel_select.values:
            await interaction.response.defer()
            return
        selected_index = int(self.duel_select.values[0])
        selected_duel = self.duels[selected_index]

        # Aggiorno il result_select con i nomi dei giocatori + annulla
        self.result_select.options = [
            discord.SelectOption(label=selected_duel["challenger_name"], value="challenger"),
            discord.SelectOption(label=selected_duel["opponent_name"], value="opponent"),
            discord.SelectOption(label="❌ Duello annullato", value="cancel")
        ]
        #self.result_select.values = []  # reset selezione precedente

        await interaction.response.edit_message(
            content=f"Duello selezionato: {selected_duel['challenger_name']} vs {selected_duel['opponent_name']}\nSeleziona il vincitore:",
            view=self
        )

    async def result_select_callback(self, interaction: discord.Interaction):
        # Solo rispondo per evitare interaction failed, il risultato lo confermi con il bottone
        await interaction.response.defer()

    async def prev_page(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
            self.build_duel_options()
            await interaction.response.edit_message(view=self)

    async def next_page(self, interaction: discord.Interaction):
        max_pages = math.ceil(len(self.duels) / 25)
        if self.page < max_pages - 1:
            self.page += 1
            self.build_duel_options()
            await interaction.response.edit_message(view=self)

    async def confirm(self, interaction: discord.Interaction):
        if not self.duel_select.values or not self.result_select.values:
            return await interaction.response.send_message("⚠️ Devi selezionare un duello e un risultato.", ephemeral=True)

        selected_index = int(self.duel_select.values[0])
        selected_duel = self.duels[selected_index]
        winner = self.result_select.values[0]

        if winner == "cancel":
            duels_collection.delete_one({"_id": selected_duel["_id"]})
            await interaction.response.send_message("❌ Duello annullato con successo.", ephemeral=True)
            return

        category = selected_duel["type"].lower()  # era "Flyers", quindi va in lowercase
        category_map = {"land": 0, "flyers": 1, "aquatic": 2}
        index = category_map.get(category)

        if index is None:
            return await interaction.response.send_message(f"⚠️ Categoria non valida: `{selected_duel['category']}`", ephemeral=True)

        size = selected_duel["category"].capitalize()  # era "Big", quindi va capitalizzato
        if size not in ["Small", "Medium", "Big", "Mega"]:
            return await interaction.response.send_message(f"⚠️ Dimensione non valida: `{selected_duel['type']}`", ephemeral=True)

        win_points = {
            "Small": [50, 60, 70],
            "Medium": [80, 90, 100],
            "Big": [120, 130, 140],
            "Mega": [200, 0, 0]
        }
        loss_points = {
            "Small": [40, 50, 60],
            "Medium": [70, 80, 90],
            "Big": [100, 110, 120],
            "Mega": [150, 0, 0]
        }

        punti_win = win_points[size][index]
        punti_loss = loss_points[size][index]

        if winner == "challenger":
            set_punti(selected_duel["challenger_id"], get_punti(selected_duel["challenger_id"]) + punti_win)
            set_punti(selected_duel["opponent_id"], get_punti(selected_duel["opponent_id"]) + punti_loss)
        else:
            set_punti(selected_duel["opponent_id"], get_punti(selected_duel["opponent_id"]) + punti_win)
            set_punti(selected_duel["challenger_id"], get_punti(selected_duel["challenger_id"]) + punti_loss)

        duels_collection.delete_one({"_id": selected_duel["_id"]})
        await interaction.response.send_message("✅ Duello risolto con successo!", ephemeral=True)

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

        embed = discord.Embed(
        title=f"{chosen_dino} riscattato!",
        description=f"**{interaction.user.display_name}** ha riscattato **{chosen_dino}** per {dino_info['punti']} punti! 🎉",
        color=0x00ff00
        )
        if "img" in dino_info:
            embed.set_image(url=dino_info["img"])

        await interaction.response.send_message(embed=embed)

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

def format_dino_table(dinos: dict) -> str:

    dino_names = sorted(dinos.keys())

    header = f"| {'Nome':<20} | {'Livello':^7} | {'Punti':^6} |"
    separator = f"|{'-'*22}|{'-'*9}|{'-'*8}|"
    rows = [header, separator]

    for nome, dati in dinos.items():
        nome_fmt = nome[:20].ljust(20)
        livello = str(dati["livello"]).center(7)
        punti = str(dati["punti"]).center(6)
        rows.append(f"| {nome_fmt} | {livello} | {punti} |")

    return "```\n" + "\n".join(rows) + "\n```"

class DinoDropdownView(View):
    def __init__(self, dinos: dict, page: int = 0):
        super().__init__(timeout=None)
        self.dinos = dinos
        self.page = page
        self.dino_names = sorted(dinos.keys())
        self.per_page = 25

        self.total_pages = (len(self.dino_names) - 1) // self.per_page + 1
        self.current_dino = None

        self.update_select_menu()
        self.add_navigation_buttons()

    def update_select_menu(self):
        start = self.page * self.per_page
        end = start + self.per_page
        options = [
            SelectOption(label=nome, value=nome)
            for nome in self.dino_names[start:end]
        ]

        self.select = Select(
            placeholder=f"Seleziona un dinosauro (pagina {self.page + 1}/{self.total_pages})",
            options=options,
            custom_id="select_dino"
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    def add_navigation_buttons(self):
        # Bottone indietro
        self.prev_button = Button(label="⬅️", style=ButtonStyle.primary, disabled=self.page == 0)
        self.prev_button.callback = self.go_previous
        self.add_item(self.prev_button)

        # Bottone avanti
        self.next_button = Button(label="➡️", style=ButtonStyle.primary, disabled=self.page >= self.total_pages - 1)
        self.next_button.callback = self.go_next
        self.add_item(self.next_button)

        # Bottone "torna alla tabella"
        self.back_button = Button(label="Torna alla tabella", style=ButtonStyle.secondary, disabled=True)
        self.back_button.callback = self.back_callback
        self.add_item(self.back_button)

    async def select_callback(self, interaction: Interaction):
        self.current_dino = self.select.values[0]
        dati = self.dinos[self.current_dino]

        embed = Embed(
            title=self.current_dino,
            description=f"Livello: {dati['livello']}\nPunti: {dati['punti']}",
            color=0x00ff00
        )
        if "img" in dati:
            embed.set_image(url=dati["img"])

        self.back_button.disabled = False

        await interaction.response.edit_message(content=None, embed=embed, view=self)

    async def back_callback(self, interaction: Interaction):
        desc = format_dino_table(self.dinos)
        self.back_button.disabled = True
        await interaction.response.edit_message(content=desc, embed=None, view=self)

    async def go_previous(self, interaction: Interaction):
        new_view = DinoDropdownView(self.dinos, page=self.page - 1)
        desc = format_dino_table(self.dinos)
        await interaction.response.edit_message(content=desc, embed=None, view=new_view)

    async def go_next(self, interaction: Interaction):
        new_view = DinoDropdownView(self.dinos, page=self.page + 1)
        desc = format_dino_table(self.dinos)
        await interaction.response.edit_message(content=desc, embed=None, view=new_view)

class AchievementsRedeemView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.list_names = list(all_achievement_lists.keys())
        self.list_page = 0  # pagina tra le liste (non usata ma la lasciamo)
        self.ach_page = 0   # pagina tra gli achievement, importante

        self.selected_list_name = self.list_names[self.list_page] if self.list_names else None
        self.selected_ach_name = None

        # Dropdown categoria
        self.list_select = Select(
            placeholder="Seleziona categoria achievement",
            options=self.get_list_options(),
            custom_id="select_list"
        )
        self.list_select.callback = self.list_select_callback
        self.add_item(self.list_select)

        # Dropdown achievement (mostra max 25 per pagina)
        self.ach_select = Select(
            placeholder="Seleziona achievement",
            options=self.get_achievement_options(),
            custom_id="select_achievement"
        )
        self.ach_select.callback = self.ach_select_callback
        self.add_item(self.ach_select)

        # Bottoni per navigare la pagina degli achievement
        self.prev_btn = Button(label="◀️ Indietro", style=discord.ButtonStyle.secondary, custom_id="ach_prev")
        self.next_btn = Button(label="Avanti ▶️", style=discord.ButtonStyle.secondary, custom_id="ach_next")
        self.prev_btn.callback = self.prev_page_callback
        self.next_btn.callback = self.next_page_callback
        self.add_item(self.prev_btn)
        self.add_item(self.next_btn)

        # Bottone completato
        self.complete_btn = Button(
            label="Completato",
            style=discord.ButtonStyle.success,
            custom_id="complete_achievement"
        )
        self.complete_btn.callback = self.complete_callback
        self.add_item(self.complete_btn)

    def get_list_options(self):
        if not self.list_names:
            return [discord.SelectOption(label="Nessuna categoria", value="none", default=True)]
        return [discord.SelectOption(label=n, value=n) for n in self.list_names[:25]]

    def get_achievement_options(self):
        if not self.selected_list_name or self.selected_list_name == "none":
            return [discord.SelectOption(label="Nessun achievement", value="none", default=True)]

        ach_dict, _ = all_achievement_lists[self.selected_list_name]
        ach_names = sorted(ach_dict.keys())

        if not ach_names:
            return [discord.SelectOption(label="Nessun achievement", value="none", default=True)]

        # Calcolo paginazione
        per_page = 25
        start = self.ach_page * per_page
        end = start + per_page
        paged_names = ach_names[start:end]

        options = [discord.SelectOption(label=n, value=n) for n in paged_names]
        return options if options else [discord.SelectOption(label="Nessun achievement", value="none", default=True)]

    async def update_view(self, interaction: Interaction):
        # Aggiorna le options dropdown
        self.list_select.options = self.get_list_options()
        self.ach_select.options = self.get_achievement_options()

        # Controlla validità selezione achievement
        ach_values = [opt.value for opt in self.ach_select.options]
        if self.selected_ach_name not in ach_values:
            self.selected_ach_name = ach_values[0] if ach_values else None

        self.list_select.default_values = [self.selected_list_name] if self.selected_list_name else []
        self.ach_select.default_values = [self.selected_ach_name] if self.selected_ach_name else []

        # Embed aggiornato
        if self.selected_ach_name and self.selected_ach_name != "none":
            ach_dict, color = all_achievement_lists[self.selected_list_name]
            dati = ach_dict[self.selected_ach_name]
            embed = Embed(title=self.selected_ach_name, color=color)
            embed.add_field(name="Descrizione", value=dati["descrizione"], inline=False)
            embed.add_field(name="Punti", value=str(dati["punti"]), inline=True)
        else:
            embed = Embed(title="Seleziona un achievement", description="Nessun achievement selezionato", color=discord.Color.dark_gray())

        await interaction.response.edit_message(embed=embed, view=self)

    async def list_select_callback(self, interaction: Interaction):
        self.selected_list_name = interaction.data["values"][0]
        self.selected_ach_name = None
        self.ach_page = 0  # reset pagina achievement alla nuova categoria
        await self.update_view(interaction)

    async def ach_select_callback(self, interaction: Interaction):
        self.selected_ach_name = interaction.data["values"][0]
        await self.update_view(interaction)

    async def prev_page_callback(self, interaction: Interaction):
        if self.ach_page > 0:
            self.ach_page -= 1
            # Aggiorna dropdown
            await self.update_view(interaction)
        else:
            await interaction.response.send_message("Sei già alla prima pagina.", ephemeral=True)

    async def next_page_callback(self, interaction: Interaction):
        ach_dict, _ = all_achievement_lists.get(self.selected_list_name, ({}, discord.Color.default()))
        ach_names = sorted(ach_dict.keys())
        max_page = (len(ach_names) - 1) // 25
        if self.ach_page < max_page:
            self.ach_page += 1
            await self.update_view(interaction)
        else:
            await interaction.response.send_message("Sei già all'ultima pagina.", ephemeral=True)

    async def complete_callback(self, interaction: Interaction):
        if not self.selected_ach_name or self.selected_ach_name == "none":
            await interaction.response.send_message("Seleziona un achievement valido prima di completarlo.", ephemeral=True)
            return

        ach_dict, _ = all_achievement_lists[self.selected_list_name] #qui
        dati = ach_dict[self.selected_ach_name]
        user_id = interaction.user.id
        tribe_user_ids = get_tribe_members(user_id)

        # Check se già completato da qualcuno nella tribe
        if not dati["ripetibile"]:
            if achievements_collection.find_one({
                "user_id": {"$in": [str(uid) for uid in tribe_user_ids]},
                "achievement": self.selected_ach_name
            }):
                await interaction.response.send_message(
                    f"L'achievement **{self.selected_ach_name}** è già stato completato da qualcuno della tua tribe!",
                    ephemeral=True
                )
                return

        # Assegna l'achievement a tutti i membri della tribe
        for uid in tribe_user_ids:
            current_points = get_punti(uid)
            set_punti(uid, current_points + dati["punti"])
            achievements_collection.insert_one({
                "user_id": str(uid),
                "achievement": self.selected_ach_name,
                "punti": dati["punti"],
                "timestamp": interaction.created_at,
                "ripetibile": dati["ripetibile"]
            })

        # Feedback all’utente
        if len(tribe_user_ids) > 1:
            await interaction.response.send_message(
                f"L'achievement **{self.selected_ach_name}** è stato completato da {interaction.user.mention} e assegnato a tutti i membri della tribe! 🎉",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention} ha completato l'achievement **{self.selected_ach_name}** e ha guadagnato {dati['punti']} punti! 🎉",
                ephemeral=True
            )

def format_achievements_table(achievements: dict, categoria: str, page: int, per_page: int) -> str:
    achievement_names = sorted(achievements.keys())
    start = page * per_page
    end = start + per_page
    paged_names = achievement_names[start:end]

    header = f"| {'Titolo':<20} | {'Punti':^6} | {'Descrizione':<50} |"
    separator = f"|{'-'*22}|{'-'*8}|{'-'*52}|"
    rows = [f"**Categoria: {categoria} (pagina {page+1})**\n", header, separator]

    for nome in paged_names:
        dati = achievements[nome]
        titolo = nome[:20].ljust(20)
        punti = str(dati["punti"]).center(6)
        desc = dati["descrizione"][:47] + "..." if len(dati["descrizione"]) > 50 else dati["descrizione"]
        desc = desc.ljust(50)
        rows.append(f"| {titolo} | {punti} | {desc} |")

    return "```\n" + "\n".join(rows) + "\n```"


class AchievementDropdownView(View):
    def __init__(self):
        super().__init__(timeout=None)

        self.all_categories = sorted(all_achievement_lists.keys())
        self.cat_page = 0

        self.current_category = None
        self.current_achievements = None
        self.ach_page = 0

        # --- Select categoria ---
        self.category_select = Select(
            placeholder="Seleziona una categoria",
            options=self.get_category_options(),
            custom_id="select_category"
        )
        self.category_select.callback = self.select_category_callback
        self.add_item(self.category_select)

        # --- Pulsanti paginazione categorie ---
        self.cat_prev_btn = Button(label="⬅️", style=discord.ButtonStyle.secondary, disabled=True)
        self.cat_next_btn = Button(label="➡️", style=discord.ButtonStyle.secondary, disabled=(len(self.all_categories) <= MAX_OPTIONS_PER_PAGE))
        self.cat_prev_btn.callback = self.cat_prev_callback
        self.cat_next_btn.callback = self.cat_next_callback
        self.add_item(self.cat_prev_btn)
        self.add_item(self.cat_next_btn)

        # --- Select achievements ---
        self.achievement_select = Select(
            placeholder="Seleziona un achievement",
            options=[SelectOption(label="Nessuna categoria selezionata", value="none")],
            custom_id="select_achievement",
            disabled=True
        )
        self.achievement_select.callback = self.achievement_callback
        self.add_item(self.achievement_select)

        # --- Pulsanti paginazione achievements ---
        self.ach_prev_btn = Button(label="⬅️", style=discord.ButtonStyle.secondary, disabled=True)
        self.ach_next_btn = Button(label="➡️", style=discord.ButtonStyle.secondary, disabled=True)
        self.ach_prev_btn.callback = self.ach_prev_callback
        self.ach_next_btn.callback = self.ach_next_callback
        self.add_item(self.ach_prev_btn)
        self.add_item(self.ach_next_btn)

        # --- Bottone torna alla tabella ---
        self.back_button = Button(
            label="Torna alla tabella",
            style=discord.ButtonStyle.secondary,
            disabled=True
        )
        self.back_button.callback = self.back_callback
        self.add_item(self.back_button)

    def get_category_options(self):
        start = self.cat_page * MAX_OPTIONS_PER_PAGE
        end = start + MAX_OPTIONS_PER_PAGE
        sliced = self.all_categories[start:end]
        return [SelectOption(label=cat, value=cat) for cat in sliced]

    def get_achievement_options(self):
        if not self.current_achievements:
            return []
        achievement_names = sorted(self.current_achievements.keys())
        start = self.ach_page * MAX_OPTIONS_PER_PAGE
        end = start + MAX_OPTIONS_PER_PAGE
        sliced = achievement_names[start:end]
        return [SelectOption(label=nome, value=nome) for nome in sliced]

    async def select_category_callback(self, interaction: Interaction):
        self.current_category = self.category_select.values[0]
        achievements, _ = all_achievement_lists[self.current_category]
        self.current_achievements = achievements
        self.ach_page = 0

        # Aggiorna select achievements
        new_options = self.get_achievement_options()
        self.achievement_select.options = new_options
        self.achievement_select.disabled = False

        # Aggiorna bottoni paginazione achievements
        self.ach_prev_btn.disabled = True
        self.ach_next_btn.disabled = len(self.current_achievements) <= MAX_OPTIONS_PER_PAGE

        # Disabilita back_button finché non si seleziona un achievement
        self.back_button.disabled = True

        # Mostra tabella paginata della categoria (pagina 1)
        desc = format_achievements_table(self.current_achievements, self.current_category, self.ach_page, per_page=MAX_OPTIONS_PER_PAGE)

        await interaction.response.edit_message(content=desc, embed=None, view=self)

    async def achievement_callback(self, interaction: Interaction):
        selected_ach = self.achievement_select.values[0]
        dati = self.current_achievements[selected_ach]

        embed = discord.Embed(
            title=selected_ach,
            description=dati["descrizione"],
            color=0x00ff00
        )
        embed.add_field(name="Punti", value=str(dati["punti"]), inline=True)

        self.back_button.disabled = False

        await interaction.response.edit_message(content=None, embed=embed, view=self)

    async def back_callback(self, interaction: Interaction):
        desc = format_achievements_table(self.current_achievements, self.current_category, self.ach_page, per_page=MAX_OPTIONS_PER_PAGE)
        self.back_button.disabled = True
        await interaction.response.edit_message(content=desc, embed=None, view=self)

    async def cat_prev_callback(self, interaction: Interaction):
        if self.cat_page > 0:
            self.cat_page -= 1
            self.category_select.options = self.get_category_options()
            self.cat_next_btn.disabled = False
            self.cat_prev_btn.disabled = self.cat_page == 0

            # Reset stato
            self.current_category = None
            self.current_achievements = None
            self.achievement_select.options = [SelectOption(label="Nessuna categoria selezionata", value="none")]
            self.achievement_select.disabled = True
            self.ach_prev_btn.disabled = True
            self.ach_next_btn.disabled = True
            self.back_button.disabled = True

            await interaction.response.edit_message(content="Seleziona una categoria:", embed=None, view=self)

    async def cat_next_callback(self, interaction: Interaction):
        max_page = (len(self.all_categories) - 1) // MAX_OPTIONS_PER_PAGE
        if self.cat_page < max_page:
            self.cat_page += 1
            self.category_select.options = self.get_category_options()
            self.cat_prev_btn.disabled = False
            self.cat_next_btn.disabled = self.cat_page == max_page

            # Reset stato
            self.current_category = None
            self.current_achievements = None
            self.achievement_select.options = [SelectOption(label="Nessuna categoria selezionata", value="none")]
            self.achievement_select.disabled = True
            self.ach_prev_btn.disabled = True
            self.ach_next_btn.disabled = True
            self.back_button.disabled = True

            await interaction.response.edit_message(content="Seleziona una categoria:", embed=None, view=self)

    async def ach_prev_callback(self, interaction: Interaction):
        if self.ach_page > 0:
            self.ach_page -= 1
            self.achievement_select.options = self.get_achievement_options()
            self.ach_next_btn.disabled = False
            self.ach_prev_btn.disabled = self.ach_page == 0
            self.back_button.disabled = True

            # Mostra pagina achievements aggiornata
            desc = format_achievements_table(self.current_achievements, self.current_category, self.ach_page, per_page=MAX_OPTIONS_PER_PAGE)
            await interaction.response.edit_message(content=desc, embed=None, view=self)

    async def ach_next_callback(self, interaction: Interaction):
        max_page = (len(self.current_achievements) - 1) // MAX_OPTIONS_PER_PAGE
        if self.ach_page < max_page:
            self.ach_page += 1
            self.achievement_select.options = self.get_achievement_options()
            self.ach_prev_btn.disabled = False
            self.ach_next_btn.disabled = self.ach_page == max_page
            self.back_button.disabled = True

            desc = format_achievements_table(self.current_achievements, self.current_category, self.ach_page, per_page=MAX_OPTIONS_PER_PAGE)
            await interaction.response.edit_message(content=desc, embed=None, view=self)

async def send_paginated_embed(interaction: Interaction, entries: list[str], title: str):
    per_page = 10
    total_pages = math.ceil(len(entries) / per_page)

    def get_embed(page):
        start = page * per_page
        end = start + per_page
        embed = Embed(title=title, description="\n".join(entries[start:end]))
        embed.set_footer(text=f"Pagina {page + 1} di {total_pages}")
        return embed

    class Paginator(View):
        def __init__(self):
            super().__init__(timeout=120)
            self.current_page = 0
            self.update_buttons()

        def update_buttons(self):
            self.clear_items()

            if total_pages <= 1:
                return  # Nessun bottone se c'è solo una pagina

            back_button = Button(label="⬅️ Indietro", style=ButtonStyle.secondary)
            next_button = Button(label="Avanti ➡️", style=ButtonStyle.secondary)

            back_button.disabled = self.current_page == 0
            next_button.disabled = self.current_page == total_pages - 1

            async def back_callback(interaction: Interaction):
                self.current_page -= 1
                self.update_buttons()
                await interaction.response.edit_message(embed=get_embed(self.current_page), view=self)

            async def next_callback(interaction: Interaction):
                self.current_page += 1
                self.update_buttons()
                await interaction.response.edit_message(embed=get_embed(self.current_page), view=self)

            back_button.callback = back_callback
            next_button.callback = next_callback

            self.add_item(back_button)
            self.add_item(next_button)

    view = Paginator()
    await interaction.followup.send(embed=get_embed(0), view=view, ephemeral=True)

class UndoSelectView(View):
    def __init__(self, user_id: int, collection, list_type: str, max_entries: int = 10):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.collection = collection
        self.list_type = list_type  # "achievement" o "redeem"
        self.max_entries = max_entries
        self.entries = list(collection.find({"user_id": str(user_id)}).sort("timestamp", -1).limit(max_entries))

        options = []
        for i, entry in enumerate(self.entries):
            # Testo da mostrare nella select, breve descrizione con segno punti
            if list_type == "achievement":
                label = entry.get("achievement", "achievement sconosciuto")
                pts = entry.get("punti", 0)
                desc = f"-{pts} pt"
            else:
                label = entry.get("nome", "Redeem")
                pts = entry.get("punti", 0)
                desc = f"+{pts} pt"

            options.append(discord.SelectOption(
                label=label[:100],  # limite Discord
                description=desc,
                value=str(i)  # indice nell'array
            ))

        self.add_item(UndoSelect(options, self))

class UndoSelect(Select):
    def __init__(self, options, parent_view):
        super().__init__(placeholder="Scegli una entry da annullare...", options=options, min_values=1, max_values=1)
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        idx = int(self.values[0])
        entry = self.parent_view.entries[idx]

        # Elimina dal DB
        result = self.parent_view.collection.delete_one({"_id": entry["_id"]})

        if result.deleted_count == 0:
            await interaction.response.send_message("Errore: entry non trovata o già cancellata.", ephemeral=True)
            return

        # Aggiorna punti
        user_id = int(entry["user_id"])
        punti_utente = get_punti(user_id)
        punti_da_modificare = entry.get("punti", 0)

        if self.parent_view.list_type == "achievement":
            # Undo achievement: tolgo i punti guadagnati
            nuovi_punti = max(0, punti_utente - punti_da_modificare)
            set_punti(user_id, nuovi_punti)
            segno = "-"
            nome_entry = entry.get("achievement", "achievement sconosciuto")
        else:
            # Undo redeem: riaggiungo i punti tolti dal redeem
            nuovi_punti = punti_utente + punti_da_modificare
            set_punti(user_id, nuovi_punti)
            segno = "+"
            nome_entry = entry.get("nome", "redeem sconosciuto")

        await interaction.response.send_message(
            f"Entry '{nome_entry}' annullata.\nPunti modificati: {segno}{punti_da_modificare} (totale ora: {nuovi_punti}) per l'utente <@{user_id}>.",
            ephemeral=True
        )
        self.parent_view.stop()

# === SCRAPING ===

def get_dino_description(nome_dino: str):
    slug = nome_dino.strip().replace(" ", "_")
    url = f"https://ark.fandom.com/wiki/{slug}"
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None, None, None, f"Pagina per '{nome_dino}' non trovata sul wiki di Ark."

    soup = BeautifulSoup(r.text, "html.parser")

    # Trova l'immagine giusta nella tabella info a destra
    image_tag = None
    container = soup.select_one("div.info-arkitex.info-framework div.info-arkitex.info-unit div.info-arkitex.info-unit-row div.info-arkitex.info-X1-100.info-column span[mw\\:File] a.mw-file-description.image img")
    if container:
        image_tag = container.select_one("a.image img")

    if not image_tag:
        # fallback classico se sopra non funziona
        image_tag = soup.find("img", class_="mw-file-element")

    image_url = None
    if image_tag and image_tag.has_attr("src"):
        image_url = image_tag["src"]
        if image_url.startswith("//"):
            image_url = "https:" + image_url
        elif not image_url.startswith("http"):
            image_url = "https://" + image_url.lstrip("/")

    # Validazione URL immagine: deve essere http(s) e non data URI
    def is_valid_image_url(url: str) -> bool:
        if not url:
            return False
        url = url.strip()
        return (url.startswith("http://") or url.startswith("https://")) and not url.startswith("data:")

    if not is_valid_image_url(image_url):
        image_url = None

    # Cerca sezione Utility → Roles
    utility_header = soup.find(id="Utility")
    if not utility_header:
        return None, url, image_url, f"Sezione 'Utility' non trovata per '{nome_dino}'."

    roles_header = utility_header.find_next("span", id="Roles")
    if not roles_header:
        return None, url, image_url, f"Sezione 'Roles' non trovata per '{nome_dino}'."

    roles_list = roles_header.find_parent().find_next_sibling("ul")
    if not roles_list:
        return None, url, image_url, f"Lista 'Roles' non trovata per '{nome_dino}'."

    items = [f"• {li.get_text(strip=True)}" for li in roles_list.find_all("li")]
    descrizione = "\n".join(items)

    return descrizione, url, image_url, None

# === BOT SETUP ===
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def is_valid_image_url(url: str) -> bool:
    if not url:
        return False
    url = url.strip()
    if url.startswith("http://") or url.startswith("https://"):
        if url.startswith("data:"):
            return False
        return True
    return False

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

@bot.tree.command(name="aggiungi", description="Aggiungi punti a un utente (ADMIN)")
@app_commands.describe(membro="L'utente a cui aggiungere punti", quantita="Numero di punti da aggiungere")
async def aggiungi(interaction: discord.Interaction, membro: discord.Member, quantita: int):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return
    attuali = get_punti(membro.id)
    set_punti(membro.id, attuali + quantita)
    await interaction.response.send_message(f"{quantita} punti aggiunti a {membro.display_name}.")

@bot.tree.command(name="togli", description="Togli punti a un utente (ADMIN)")
@app_commands.describe(membro="L'utente a cui togliere punti", quantita="Numero di punti da togliere")
async def togli(interaction: discord.Interaction, membro: discord.Member, quantita: int):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return
    attuali = get_punti(membro.id)
    nuovi = max(attuali - quantita, 0)
    set_punti(membro.id, nuovi)
    await interaction.response.send_message(f"{quantita} punti rimossi da {membro.display_name}.")

@bot.tree.command(name="classifica", description="Mostra la classifica dei punti e achievement")
@app_commands.describe(tipo="Scrivi 'tribe' per vedere la classifica delle tribù")
async def classifica(interaction: discord.Interaction, tipo: Literal["generale", "tribe"] = "generale"):
    
    global tribe_members  # opzionale ma esplicativo

    if tipo == "tribe":

        # Prepara contatori
        tribe_counts = {tribe: 0 for tribe in tribe_members}

        # Conta achievement per ciascun membro e assegna alla tribe
        for tribe, members in tribe_members.items():
            for user_id in members:
                count = achievements_collection.count_documents({"user_id": str(user_id)})
                tribe_counts[tribe] += count

        # Ordina le tribe per numero di achievement
        sorted_tribes = sorted(tribe_counts.items(), key=lambda x: x[1], reverse=True)

        # Crea embed
        embed = discord.Embed(
            title="🏕️ Classifica Tribe",
            description="Le tribe con più achievement completati!",
            color=discord.Color.green()
        )

        medaglie = {0: "🥇", 1: "🥈", 2: "🥉"}

        for i, (tribe, count) in enumerate(sorted_tribes):
            medaglia = medaglie.get(i, f"#{i+1}")
            embed.add_field(
                name=f"{medaglia} {tribe}",
                value=f"🎯 **{count}** achievement totali",
                inline=False
            )

        await interaction.response.send_message(embed=embed)
        return

    # CLASSIFICA GENERALE
    top = punti_collection.find().sort("punti", -1).limit(10)
    embed = discord.Embed(
        title="🏆 Classifica Generale",
        description="Ecco i top 10 per **punti** e **achievement** sbloccati!",
        color=discord.Color.gold()
    )

    posizione = 1
    medaglie = {1: "🥇", 2: "🥈", 3: "🥉"}

    for doc in top:
        user_id = str(doc["_id"])
        punti = doc.get("punti", 0)

        n_achievements = achievements_collection.count_documents({"user_id": user_id})

        int_user_id = int(user_id)
        membro = interaction.guild.get_member(int_user_id)
        if membro:
            nome = membro.display_name
        else:
            try:
                user = await bot.fetch_user(int_user_id)
                nome = user.name
            except:
                nome = f"Utente ID {user_id}"

        medaglia = medaglie.get(posizione, f"#{posizione}")
        embed.add_field(
            name=f"{medaglia} {nome}",
            value=f"✨ **{punti}** punti",
            inline=False
        )
        posizione += 1

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="clear_points", description="Rimuove un utente dal conteggio punti (ADMIN)")
@app_commands.describe(membro="L'utente da rimuovere")
async def clear_points(interaction: discord.Interaction, membro: discord.Member):
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
@bot.tree.command(name="redeem_dino", description="Effettivo redeem dei dino")
async def redeem_dino(interaction: discord.Interaction):
    user_id = interaction.user.id
    view = DinoRedeemView(user_id, redeemable_dinos)
    await interaction.response.send_message("Scegli il dino da redeemare:", view=view, ephemeral=True)

@bot.tree.command(name="lista_dino", description="Mostra i dino disponibili per il redeem")
async def lista_dino(interaction: Interaction):
    desc = format_dino_table(redeemable_dinos)
    view = DinoDropdownView(redeemable_dinos)
    await interaction.response.send_message(content=desc, view=view, ephemeral=True)

@bot.tree.command(name="redeem_history", description="Mostra log redeem dinos (ADMIN)")
async def redeem_history(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True) 

    docs = list(redeemed_collection.find().sort("timestamp", 1))
    if not docs:
        await interaction.followup.send("Nessun redeem registrato.", ephemeral=True)
        return

    entries = []
    for doc in docs:
        user = await bot.fetch_user(int(doc["user_id"]))
        time = datetime.fromisoformat(str(doc["timestamp"]).replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
        entries.append(f"[{time}] {user.name} ha riscattato **{doc['nome']}** per {doc['punti']} pt")

    await send_paginated_embed(interaction, entries, "📋 Log Redeem")

@bot.tree.command(name="clear_redeem_history", description="Pulisce la lista dei redeem (ADMIN)")
async def clear_redeem_history(interaction: discord.Interaction):
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
    video_url = "https://youtu.be/EqQv6WtLLwY"
    video_title = "The only thing that lystros are worth for"

    await interaction.response.send_message(f"**{video_title}**\n{video_url}")

@bot.tree.command(name="regole_1vs1", description="Mostra le regole per le sfide 1vs1/tornei")
async def regole_1vs1(interaction: discord.Interaction):
    
    # Crea l'embed
    embed = discord.Embed(
        title="Regole per le sfide 1vs1",
        description="TBA",
        color=discord.Color.green()
    )

    # Invia il messaggio con l'embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="regole_achievement", description="Spiega come funziona il sistema degli achievements")
async def regole_achievement(interaction: discord.Interaction):

    # Crea l'embed
    embed = discord.Embed(
        title="Come usare il file di spreadheets",
        description="TBA",
        color=discord.Color.green()
    )

    # Invia il messaggio con l'embed
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="lista_achievements", description="Mostra gli achievements disponibili")
async def lista_achievements(interaction: Interaction):

    await interaction.response.defer(thinking=True, ephemeral=True)
    default_cat = sorted(all_achievement_lists.keys())[0]
    achievements, _ = all_achievement_lists[default_cat]
    desc = format_achievements_table(achievements, default_cat, page=0, per_page=MAX_OPTIONS_PER_PAGE)
    view = AchievementDropdownView()
    
    if len(desc) > 2000:
        file = discord.File(io.StringIO(desc), filename="achievements.txt")
        await interaction.followup.send(
            content="Troppi achievement per mostrarli nel messaggio. Ecco il file:",
            file=file,
            view=view,
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            content=desc,
            view=view,
            ephemeral=True
        )

@bot.tree.command(name="redeem_achievement", description="Completa uno o piu achievement")
async def redeem_achievement(interaction: Interaction):
    view = AchievementsRedeemView()
    # Embed iniziale della prima lista e primo achievement
    ach_dict, color = all_achievement_lists[view.selected_list_name]
    first_ach_name = sorted(ach_dict.keys())[0] if ach_dict else None

    if first_ach_name:
        dati = ach_dict[first_ach_name]
        embed = Embed(title=first_ach_name, color=color)
        embed.add_field(name="Descrizione", value=dati["descrizione"], inline=False)
        embed.add_field(name="Punti", value=str(dati["punti"]), inline=True)
        ripetibile_txt = "Sì" if dati["ripetibile"] else "No"
        embed.add_field(name="Ripetibile", value=ripetibile_txt, inline=True)
    else:
        embed = Embed(title="Nessun achievement", description="Non ci sono achievement da mostrare.", color=discord.Color.dark_gray())

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="achievement_history", description="Mostra gli achievement completati dagli utenti (ADMIN)")
async def achievement_history(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True) 

    docs = list(achievements_collection.find().sort("timestamp", 1))
    if not docs:
        await interaction.followup.send("Nessun achievement registrato.", ephemeral=True)
        return

    entries = []
    for doc in docs:
        user = await bot.fetch_user(int(doc["user_id"]))
        time = datetime.fromisoformat(str(doc["timestamp"]).replace("Z", "+00:00")).strftime("%d/%m/%Y %H:%M")
        entries.append(f"[{time}] {user.name} ha completato **{doc['achievement']}** per {doc['punti']} pt")

    await send_paginated_embed(interaction, entries, "📋 Log Achievement")

@bot.tree.command(name="clear_achievement_history", description="Pulisce la lista degli achievement completati (ADMIN)")
async def clear_achievement_history(interaction: discord.Interaction):
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

@bot.tree.command(name="dodo", description="Mostra la lista dei comandi disponibili")
@app_commands.describe(visibilita="Scrivi 'public' per renderlo visibile a tutti, altrimenti sarà privato.")
async def dodo(interaction: discord.Interaction, visibilita: Literal["public", "private"] = None):
    embed = Embed(
        title="📜 Lista Comandi Disponibili",
        description="Ecco un riepilogo di tutti i comandi disponibili con una breve descrizione.",
        color=0x3498db
    )

    # Comandi base e informativi
    embed.add_field(name=" --> COMANDI BASE E INFORMATIVI", value="", inline=False)

    embed.add_field(name="/dodo", value="🔍 Lista dei comandi disponibili, l'hai appena usato!", inline=False)
    embed.add_field(name="/punti", value="💸 Mostra i punti attuali di un utente.", inline=False)
    embed.add_field(name="/classifica", value="🏅 Mostra la classifica dei punti degli utenti.", inline=False)
    embed.add_field(name="/regole_achievement", value="📏 Spiega come funziona il sistema degli achievements di Dodo", inline=False)
    embed.add_field(name="/regole_1vs1", value="⚔️ Mostra le regole per le sfide 1vs1/tornei.", inline=False)

    # Comandi cazzari
    embed.add_field(name="/patata", value="🥔 Se ti vuoi davvero male", inline=False)

    # Comandi dinosauri
    embed.add_field(name=" --> COMANDI REDEEM DINO", value="", inline=False)

    embed.add_field(name="/lista_dino", value="🦕 Mostra i dino disponibili per il redeem.", inline=False)
    embed.add_field(name="/redeem_dino", value="🦖 Comando per l'effettivo redeem dei dino.", inline=False)
    embed.add_field(name="/redeem_hisory", value="📜 Mostra il log dei redeem (ADMIN).", inline=False)
    embed.add_field(name="/clear_redeem_history", value="🔥 Pulisce la lista dei redeem (ADMIN).", inline=False)
    embed.add_field(name="/clear_last_redeems", value="🧹 Pulisce gli ultimi n redeems completati (ADMIN)", inline=False)

    # Comandi achievement
    embed.add_field(name=" --> COMANDI ACHIEVEMENTS", value="", inline=False)

    embed.add_field(name="/lista_achievements", value="📋 Mostra la lista degli achievement disponibili, con descrizioni e punti.", inline=False)
    embed.add_field(name="/redeem_achievement", value="🏆 Completa uno o più achievement e guadagna punti.", inline=False)
    embed.add_field(name="/achievement_history", value="📜 Mostra gli achievement completati dagli utenti (ADMIN)", inline=False)
    embed.add_field(name="/clear_achievement_history", value="🔥 Pulisce la lista degli achievement completati (ADMIN)", inline=False)
    embed.add_field(name="/clear_last_achievements", value="🧹 Pulisce gli ultimi n achievements completati (ADMIN)", inline=False)

    # Comandi amministrativi
    embed.add_field(name=" --> COMANDI MOD", value="", inline=False)

    embed.add_field(name="/aggiungi", value="➕ Aggiungi punti a un utente (ADMIN).", inline=False)
    embed.add_field(name="/togli", value="➖ Togli punti a un utente (ADMIN).", inline=False)
    embed.add_field(name="/clear_points", value="❌ Rimuove un utente dal conteggio punti (ADMIN).", inline=False)
    embed.add_field(name="/undo", value="↩️ Annulla una o piu azioni (entries) fra le ultime 10 di un utente (ADMIN)", inline=False)

    embed.set_footer(text="Per ulteriori dettagli, chiedi a kurous")
    # Controlla la visibilità
    if visibilita and visibilita.lower() == "public":
        await interaction.response.send_message(embed=embed, ephemeral=False)
    else:
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="clear_last_achievements", description="Elimina gli ultimi N achievement completati da un utente (ADMIN)")
@app_commands.describe(membro="Utente a cui rimuovere gli achievement", numero="Numero di achievement da eliminare")
async def clear_last_achievements(interaction: discord.Interaction, membro: discord.Member, numero: int):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    user_id = str(membro.id)
    # Prendi gli ultimi N achievement ordinati per timestamp decrescente
    achievements = list(achievements_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(numero))

    if not achievements:
        await interaction.response.send_message("Nessun achievement trovato per questo utente.", ephemeral=True)
        return

    # Elimina i documenti uno per uno
    deleted_count = 0
    for ach in achievements:
        achievements_collection.delete_one({"_id": ach["_id"]})
        deleted_count += 1

    await interaction.response.send_message(
        f"✅ Eliminati **{deleted_count}** achievement per {membro.display_name}.",
        ephemeral=True
    )

@bot.tree.command(name="clear_last_redeems", description="Elimina gli ultimi N redeem di un utente (ADMIN)")
@app_commands.describe(membro="Utente a cui rimuovere i redeem", numero="Numero di redeem da eliminare")
async def clear_last_redeems(interaction: discord.Interaction, membro: discord.Member, numero: int):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    user_id = str(membro.id)
    # Prendi gli ultimi N redeem ordinati per timestamp decrescente
    redeems = list(redeemed_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(numero))

    if not redeems:
        await interaction.response.send_message("Nessun redeem trovato per questo utente.", ephemeral=True)
        return

    # Elimina i documenti uno per uno
    deleted_count = 0
    for redeem in redeems:
        redeemed_collection.delete_one({"_id": redeem["_id"]})
        deleted_count += 1

    await interaction.response.send_message(
        f"✅ Eliminati **{deleted_count}** redeem per {membro.display_name}.",
        ephemeral=True
    )

# @bot.tree.command(name="dino_info", description="Mostra la descrizione base di un dinosauro di Ark")
# @app_commands.describe(nome="Nome del dinosauro (es: Argentavis, Rex, Dodo)")
# async def dino_info(interaction: discord.Interaction, nome: str):
#     await interaction.response.defer()

#     descrizione, url, image_url, error = get_dino_description(nome)
#     if error:
#         await interaction.followup.send(error, ephemeral=True)
#         return

#     print(f"[DEBUG] image_url: {image_url}")  # Per debug

#     embed = discord.Embed(
#         title=f"{nome.title()} - Ruoli",
#         url=url,
#         description=descrizione[:4096],
#         color=discord.Color.green()
#     )

#     if is_valid_image_url(image_url):
#         embed.set_image(url=image_url)
#     else:
#         embed.set_image(url="https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg")

#     await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="undo", description="Annulla un redeem o achievement (ADMIN)")
async def undo(interaction: discord.Interaction, utente: discord.User, lista: Literal["achievement", "redeem"] = None):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    if lista == "achievement":
        collection = achievements_collection
    elif lista == "redeem":
        collection = redeemed_collection
    else:
        await interaction.response.send_message("Lista non valida, scegli 'achievement' o 'redeem'.", ephemeral=True)
        return

    view = UndoSelectView(utente.id, collection, lista)
    if not view.entries:
        await interaction.response.send_message(f"Nessuna entry trovata per {utente.name} in {lista}.", ephemeral=True)
        return

    await interaction.response.send_message(f"Scegli quale entry annullare per {utente.name} in {lista}:", view=view, ephemeral=True)

@bot.tree.command(name="duel", description="Schedula un duello tra due utenti con evento")
async def duel(
    interaction: discord.Interaction,
    utente: discord.User,
    data: str,
    ora: str,
    categoria: Literal["Small", "Medium", "Big", "Mega"],
    tipo: Literal["Land", "Flyers", "Acquatic"]
):
    await interaction.response.defer()

    try:
        # Imposta la timezone italiana
        italy_tz = pytz.timezone("Europe/Rome")

        # Converte stringa in datetime naive
        duel_datetime_naive = datetime.strptime(f"{data} {ora}", "%Y-%m-%d %H:%M")

        # Rende il datetime "aware" con timezone italiana
        duel_datetime = italy_tz.localize(duel_datetime_naive)

        # Controlla che sia nel futuro rispetto all'ora corrente italiana
        if duel_datetime < datetime.now(italy_tz):
            return await interaction.followup.send("⚠️ La data/ora deve essere nel futuro!", ephemeral=True)

    except ValueError:
        return await interaction.followup.send("❌ Formato non valido! Usa data `YYYY-MM-DD` e ora `HH:MM`", ephemeral=True)

    guild = interaction.guild
    arena_channel = discord.utils.get(guild.voice_channels, name="Arena")
    if not arena_channel:
        return await interaction.followup.send("❌ Canale vocale 'Arena' non trovato!", ephemeral=True)

    title = f"Duello fra {interaction.user.display_name} e {utente.display_name}, categoria {tipo}, {categoria}"
    description = (
        f"⚔️ Duello imminente!\n\n"
        f"Categoria: **{categoria}**\n"
        f"Tipo: **{tipo}**\n"
        f"Sfidanti:\n- {interaction.user.mention}\n- {utente.mention}"
    )

    try:
        event = await guild.create_scheduled_event(
            name=title,
            start_time=duel_datetime,
            end_time=duel_datetime + timedelta(minutes=30),
            description=description,
            channel=arena_channel,
            entity_type=discord.EntityType.voice,
            privacy_level=discord.PrivacyLevel.guild_only
            # Rimuovo l'immagine per ora
        )
    except Exception as e:
        return await interaction.followup.send(f"❌ Errore durante la creazione dell'evento: {e}", ephemeral=True)

    # Salva nel database
    duels_collection.insert_one({
        "guild_id": guild.id,
        "event_id": event.id,
        "challenger_id": interaction.user.id,
        "challenger_name": interaction.user.display_name,
        "opponent_id": utente.id,
        "opponent_name": utente.display_name,
        "category": categoria,
        "type": tipo,
        "datetime": duel_datetime,
        "channel_id": arena_channel.id,
        "status": "scheduled",
        "created_at": datetime.utcnow()
    })

    await interaction.followup.send(
        f"✅ Duello schedulato!\n📅 {title}\n🕒 <t:{int(duel_datetime.timestamp())}:F>\n🗓️ Evento creato nel canale vocale **Arena**.",
        ephemeral=False
    )

@bot.tree.command(name="duel_history", description="Mostra la cronologia dei duelli schedulati (ADMIN)")
async def duel_history(interaction: discord.Interaction):
    if not is_authorized(interaction):
        await interaction.response.send_message("Non hai i permessi per eseguire questo comando.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    docs = list(duels_collection.find().sort("datetime", -1))  # Ordine decrescente per data
    if not docs:
        await interaction.followup.send("Nessun duello registrato.", ephemeral=True)
        return

    entries = []
    for doc in docs:
        challenger = await bot.fetch_user(int(doc["challenger_id"]))
        opponent = await bot.fetch_user(int(doc["opponent_id"]))
        duel_time = doc["datetime"].strftime("%d/%m/%Y %H:%M")
        status = doc.get("status", "scheduled")

        entries.append(
            f"[{duel_time}] 🥊 **{challenger.name}** vs **{opponent.name}** — {doc['type']} | {doc['category']} ({status})"
        )

    await send_paginated_embed(interaction, entries, "📋 Storico Duelli")

@bot.tree.command(name="resolve_duel", description="Risolvi un duello completato")
async def resolve_duel(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    duels = list(duels_collection.find({"status": {"$in": ["scheduled", "pending"]}}))
    user_id = interaction.user.id

    print(f"User {user_id} cerca duelli con status pending/scheduled")
    print(f"Duelli trovati nel DB: {len(duels)}")

    filtered = [duel for duel in duels if duel["challenger_id"] == user_id or duel["opponent_id"] == user_id]
    print(f"Duelli filtrati coinvolgendo l'utente: {len(filtered)}")

    if not filtered:
        return await interaction.followup.send("❌ Non ci sono duelli da risolvere in cui sei coinvolto.", ephemeral=True)

    view = DuelResolutionView(filtered, user_id)

    # Precompila le opzioni del result_select con il primo duello
    first_duel = filtered[0]
    view.result_select.options = [
        SelectOption(label=first_duel["challenger_name"], value="challenger"),
        SelectOption(label=first_duel["opponent_name"], value="opponent"),
        SelectOption(label="❌ Duello annullato", value="cancel")
    ]

    await interaction.followup.send("🎯 Seleziona un duello da risolvere:", ephemeral=True, view=view)

# === AVVIO BOT ===
@bot.event
async def on_ready():
    await bot.tree.sync()  # Sincronizza i comandi slash
    print(f'Bot online come {bot.user}!')

bot.run(TOKEN)
