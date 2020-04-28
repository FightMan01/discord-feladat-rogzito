import discord
from discord.ext import commands, tasks
import asyncio
import time
import datetime
import json
import aiohttp
import os
from discord import Webhook, AsyncWebhookAdapter

client = commands.AutoShardedBot(command_prefix=".")
Client = discord.Client()
client.remove_command('help')

with open("adat.json") as f:
    adat = json.load(f)

@client.event
async def on_ready():
    print("A bot készen van :P")
    init.start()
    await client.change_presence(activity=discord.Activity(name='Feladatok 👀', type=discord.ActivityType.watching), status=discord.Status.do_not_disturb)

@client.command()
async def rögzít(ctx, nap=None, *, szöveg=None):
    if ctx.author.bot:
        return
    if not nap:
        return await ctx.send(":x: Kérem adja meg, hány nap múlva esedékes a feladat.")
    if not szöveg:
        return await ctx.send(":x: Kérem adjon meg a feladathoz egy rövid szöveget!")
    try:
        nap = int(nap)
    except:
        return await ctx.send(":x: Kérem napnak csak számot adjon meg.")
    esedékes = datetime.date.today() + datetime.timedelta(days=nap)
    esedékes = str(esedékes.__format__("%Y.%m.%d."))
    i = 0
    for x in adat:
        if not (x == "cache" or  x == "cache2"):
            i += 1
    fid = i
    if not "cache" in adat:
        adat["cache"] = []
    if not "cache2" in adat:
        adat["cache2"] = []
    adat[fid] = {}
    adat[fid]["esedekes"] = esedékes
    adat[fid]["szöveg"] = szöveg
    adat[fid]["rögzítette"] = str(ctx.author.id)
    with open("adat.json", "w") as f2:
        json.dump(adat, f2)
    await ctx.send(":white_check_mark: Feladat rögzítve!")

@tasks.loop(minutes=5)
async def init():
    try:
        await client.wait_until_ready()
        await asyncio.gather(feladatell())
        await asyncio.gather(feladatell2())
        print("[INFO] ~> Feladat határidők ellenőrizve!")
    except Exception as e:
        print(f"[ERROR] ~> {e}")

async def feladatell():
    for id in adat:
        if not (id == "cache" or  id == "cache2"):
            if not id in adat["cache"]:
                esedékes = adat[id]["esedekes"]
                szöveg = adat[id]["szöveg"]
                holnap = datetime.date.today() + datetime.timedelta(days=1)
                holnap = str(holnap.__format__("%Y.%m.%d."))
                if esedékes == holnap:
                    csati = client.get_channel(695570356152303637)
                    rögzítő = client.get_user(int(adat[id]["rögzítette"]))
                    await csati.send(f"**{rögzítő.name}** által rögzített feladat **holnap** esedékes!\n:arrow_forward: {szöveg}")
                    adat["cache"].append(id) 
                    with open("adat.json", "w") as f2:
                        json.dump(adat, f2)

async def feladatell2():
    for id in adat:
        if not (id == "cache" or  id == "cache2"):
            if not id in adat["cache2"]:
                esedékes = adat[id]["esedekes"]
                szöveg = adat[id]["szöveg"]
                holnap = datetime.date.today()
                holnap = str(holnap.__format__("%Y.%m.%d."))
                if esedékes == holnap:
                    csati = client.get_channel(695570356152303637)
                    rögzítő = client.get_user(int(adat[id]["rögzítette"]))
                    await csati.send(f"**{rögzítő.name}** által rögzített feladat **ma** esedékes!\n:arrow_forward: {szöveg}")
                    adat["cache2"].append(id) 
                    with open("adat.json", "w") as f2:
                        json.dump(adat, f2)

@client.command()
async def feladatok(ctx):
    if ctx.author.bot:
        return
    embed = discord.Embed(title="Feladatok", color=0x00ff00, timestamp=datetime.datetime.utcnow())
    for id in adat:
        if not (id == "cache" or  id == "cache2"):
            ma = datetime.datetime.today().__format__("%Y.%m.%d.")
            ma = datetime.datetime.strptime(ma, "%Y.%m.%d.")
            esedekes = adat[id]["esedekes"]
            szöveg = adat[id]["szöveg"]
            dátum = datetime.datetime.strptime(adat[id]["esedekes"], "%Y.%m.%d.")
            if not dátum < ma:
                rögzítő = client.get_user(int(adat[id]["rögzítette"]))
                embed.add_field(name="Feladat", value=f"**Rögzítette:** {rögzítő.name}\n**Határidő:** {esedekes}\n**Szöveg:** {szöveg}")
    if len(embed.fields) > 0:
        await ctx.send(embed=embed)
    else:
        await ctx.send(":tada: Jelenleg nincs egy határidős feladat sem.")

client.run("TOKEN")
