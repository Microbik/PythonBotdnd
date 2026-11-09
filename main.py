import discord
from discord.ext import commands
from discord.ui import Button, View
from info import settings
import sys
import traceback
import random
import asyncio
import math
import os
import numpy as np
import seventv
import requests
import os
import re

phrases = [
    "Dice of Fate!"
    , "Have a roll!"
    , "Are you satisfied?"
    , "I don`t feel good for that..."
    , "I think it will be a good one..."
    , "Oh..."
    , "Fear me! The GOD of DICE!"
    , "The truth here lies..."
    , "Hope this helps..."
    , "Cry about it."
    , "If cube falls forever..."

    , "...Will it ever tell the truth?"
    , "I always right!"
    , "You should reroll..."
    , "I forgive you"
    , "Here we go…"
    , "As you wish"
    , "Dice falls, number rolls…"
    , 'Your destiny is to…'
    , 'Behold! The power of truth!'
    , 'Rolling to infinity…'
    , 'I would like to give you a zero, but i can’t'
    , 'Nuh-uh'
    , 'Not today'
    , 'Its too hot on Mars today'
    , 'Its… questionable'
]

phrasesmax = [
    "You are lucky today!"
    , "CRITICAL!"
    , "A great success indeed..."
    , "Feeling lucky today, aint you?"
    , "Make a wish"
]

phrasesmin = [
    "Oh, please, don't die..."
    , "It's time to die!"
    , "Sorry, you are out of luck..."
    , "OMAIGAAAD"
    , "tis but a scratch"
]

phrasesxtra = [
    "42 братуха ииииуууу"
    , "nice"
]

phrasesd = [
    "More dices!"
    , "Not enough dices? I have many..."
    , "Can you count for me?"
    , "I have infinity cubes with infinity sides..."
    , 'So many dices!'
    , 'Enough for you?'
    , 'Here’s your nonexistent cubes…'
    , 'So many…'
    , 'Approximated to middle'
    , 'Rolling and... dicing?'
    , 'ROLL AND DICE!'
]


# ID гильдии, где нужны особые префиксы
SPECIAL_GUILD_ID = 1366133037129269308

def get_prefix(bot, message):
    if message.guild and message.guild.id == SPECIAL_GUILD_ID:
        return ["!!", ".", "l"]
    return ["!", ".", "l"]  # префиксы по умолчанию для остальных гильдий и ЛС

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command('help')


np.random.seed()


@bot.event
async def on_ready():
    activity = discord.Game(name=f"!dice or .roll or ld")
    await bot.change_presence(activity=activity)

    print("Bot is ready")

#7tv
def download_image(image_url, save_path):
    try:
        # Отправляем GET-запрос к URL изображения
        response = requests.get(image_url, stream=True)
        response.raise_for_status()  # Проверяем успешность запроса

        # Сохраняем изображение в файл
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Изображение успешно скачано и сохранено в {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке изображения: {e}")

async def myFunctionSearchEmote(name,value):
    mySevenTvSession = seventv.seventv()
    # initialize an instance of the seventv() class. this must happen in an asynchronous context

    emotes = await mySevenTvSession.emote_search(name, case_sensitive=True)
    # searches for "pepe", using the optional filter "case_sensitive"

    myEmote = emotes[value-1]  # get the first emote from the search results

    await mySevenTvSession.close()  # later close the session
    return ("https:"+myEmote.host_url+"/2x")

@bot.command(invoke_without_command=True, aliases=["e", "em", "7tv"])
@commands.cooldown(rate=1, per=10, type=commands.BucketType.user)  # 1 использование каждые 5 секунды для каждого пользователя
async def emoji(ctx, params, value=1):
    link = await myFunctionSearchEmote(params,value)
    print(link)
    path="downloaded_image.gif"
    try:
        download_image(link+".gif", path)
        file = discord.File(path)
        await ctx.send("", file=file)
    except FileNotFoundError:
        print('no gif')
        download_image(link + ".avif", path)
        file = discord.File(path)
        await ctx.send("", file=file)
    os.remove(path)
    await ctx.message.delete()

@emoji.error
async def emoji_error(ctx, error):
    await ctx.message.delete()
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(
            f"Команда доступна через {error.retry_after:.1f} секунд.",
            delete_after=3
        )


@bot.command(invoke_without_command=True, aliases=["r", "roll", "d"])
async def dice(ctx, *, params):
    try:
        user = discord.utils.get(ctx.guild.members, id=int(ctx.message.author.id))

        if not params:
            em = discord.Embed(title='**ERROR**',
                               description="Please provide parameters for the roll!",
                               color=0xff0000)
            await ctx.send(embed=em)
            return

        if params.find(",") != -1 and params.find("d") == -1:
            '''выбор вариантов'''
            try:
                lparams = [p.strip() for p in params.split(",")]
                if not lparams:
                    raise ValueError("No options provided after splitting")

                # Проверяем, что это действительно выбор вариантов, а не dice с запятой
                dice_pattern = re.compile(r'(\d*)d(\d+)([+-]\d+)?')
                has_dice = any(dice_pattern.search(param) for param in lparams)

                if has_dice:
                    raise ValueError("Invalid format - use dice without commas or options with commas")

                res = lparams[np.random.randint(0, len(lparams))]
                phrs = phrases[np.random.randint(0, len(phrases))]

                em = discord.Embed(title=f'**{phrs}**',
                                   description=f"{res}",
                                   color=0x7289da)
                em.set_author(name=f"{user}", icon_url=ctx.author.avatar)

            except Exception as e:
                em = discord.Embed(title='**ERROR**',
                                   description=f"Error processing options: {str(e)}",
                                   color=0xff0000)
                await ctx.send(embed=em)
                return

        elif params.find("d") != -1:
            '''кубы с d и модификаторами'''
            try:
                # Разделяем параметры на кубы и модификаторы
                parts = params.split(" ")
                dice_parts = []
                modifiers = []

                # Разделяем кубы и модификаторы
                dice_pattern = re.compile(r'(\d*)d(\d+)([+-]\d+)?')
                modifier_pattern = re.compile(r'^([+-]\d+%?)$')

                for part in parts:
                    part = part.strip()
                    if dice_pattern.fullmatch(part):
                        dice_parts.append(part)
                    elif modifier_pattern.fullmatch(part):
                        modifiers.append(part)
                    else:
                        em = discord.Embed(title='**ERROR**',
                                           description=f"Invalid format: `{part}`\nUse dice format: `XdY±Z` and modifiers: `±N` or `±%N`",
                                           color=0xff0000)
                        await ctx.send(embed=em)
                        return

                if not dice_parts:
                    em = discord.Embed(title='**ERROR**',
                                       description="No valid dice found! Use format like `2d6+1`",
                                       color=0xff0000)
                    await ctx.send(embed=em)
                    return

                # Бросаем кубы
                results = []
                res = 0
                count = 0

                for cube in dice_parts:
                    match = dice_pattern.fullmatch(cube.strip())
                    if not match:
                        em = discord.Embed(title='**ERROR**',
                                           description=f"Invalid dice format: `{cube}`\nCorrect format: `XdY±Z` (e.g. 2d6+1)",
                                           color=0xff0000)
                        await ctx.send(embed=em)
                        return

                    dice_count = int(match.group(1)) if match.group(1) else 1
                    dice_sides = int(match.group(2))
                    modifier = int(match.group(3)) if match.group(3) else 0

                    if dice_count <= 0 or dice_sides <= 0:
                        em = discord.Embed(title='**ERROR**',
                                           description="Dice count and sides must be positive numbers!",
                                           color=0xff0000)
                        await ctx.send(embed=em)
                        return

                    count += dice_count

                    if count > 100:
                        em = discord.Embed(title='**ERROR**',
                                           description="No more than 100 dice per roll!",
                                           color=0xff0000)
                        await ctx.send(embed=em)
                        return

                    if dice_sides > 10000:
                        em = discord.Embed(title='**ERROR**',
                                           description="No more than 10000 sides per die!",
                                           color=0xff0000)
                        await ctx.send(embed=em)
                        return

                    for _ in range(dice_count):
                        roll = np.random.randint(1, dice_sides + 1)
                        total = roll + modifier
                        results.append((roll, modifier, total))
                        res += total

                # Формируем строку с бросками
                plu = ""
                for roll, mod, total in results:
                    if mod != 0:
                        mod_str = f"{'+' if mod > 0 else ''}{mod}"
                        plu += f" + ({roll}{mod_str}={total})"
                    else:
                        plu += f" + {roll}"
                plu = plu[3:]

                # Применяем модификаторы в порядке их указания
                base_result = res
                final_result = res
                modifier_text = ""

                for modifier in modifiers:
                    try:
                        if modifier.endswith('%'):
                            # Процентный модификатор
                            percent = int(modifier[1:-1])
                            if modifier[0] == '+':
                                final_result += int(final_result * (percent / 100))
                                modifier_text += f" + {percent}%"
                            else:  # '-'
                                final_result -= int(final_result * (percent / 100))
                                modifier_text += f" - {percent}%"
                        else:
                            # Числовой модификатор
                            value = int(modifier[1:])
                            if modifier[0] == '+':
                                final_result += value
                                modifier_text += f" + {value}"
                            else:  # '-'
                                final_result -= value
                                modifier_text += f" - {value}"
                    except ValueError:
                        em = discord.Embed(title='**ERROR**',
                                           description=f"Invalid modifier format: `{modifier}`",
                                           color=0xff0000)
                        await ctx.send(embed=em)
                        return

                # Выбор фразы
                if np.random.randint(0, 3) == 1:
                    phrs = phrases[np.random.randint(0, len(phrases))]
                else:
                    phrs = phrasesd[np.random.randint(0, len(phrasesd))]

                if modifiers:
                    em = discord.Embed(title=f'**{phrs}**',
                                       description=f"🎲 You Rolled **{final_result}** (Base: {base_result}{modifier_text})\n*{plu}*",
                                       color=0x7289da)
                else:
                    em = discord.Embed(title=f'**{phrs}**',
                                       description=f"🎲 You Rolled **{final_result}**. (*{plu}*)",
                                       color=0x7289da)

                em.set_author(name=f"{user}", icon_url=ctx.author.avatar)

            except Exception as e:
                em = discord.Embed(title='**ERROR**',
                                   description=f"Error processing dice roll: {str(e)}",
                                   color=0xff0000)
                await ctx.send(embed=em)
                return

        else:
            '''1 или промежуток или +-'''
            try:
                # Проверяем наличие модификаторов
                parts = params.split(' ')
                base_part = parts[0]
                modifiers = parts[1:] if len(parts) > 1 else []

                # Проверяем формат базовой части
                if ' ' in base_part or '-' in base_part and not base_part.startswith('-'):
                    # Это диапазон
                    range_parts = base_part.split('-')
                    if len(range_parts) != 2:
                        em = discord.Embed(title='**ERROR**',
                                           description="For ranges, use format like `1-10` or `1 10`",
                                           color=0xff0000)
                        await ctx.send(embed=em)
                        return

                    try:
                        num = int(range_parts[0])
                        second = int(range_parts[1])
                        if num >= second:
                            raise ValueError("First number must be less than second")
                    except ValueError as e:
                        em = discord.Embed(title='**ERROR**',
                                           description=str(e),
                                           color=0xff0000)
                        await ctx.send(embed=em)
                        return

                    base_result = np.random.randint(num, second + 1)
                    final_result = base_result
                    modifier_text = ""

                    # Применяем модификаторы
                    for modifier in modifiers:
                        try:
                            if modifier.endswith('%'):
                                percent = int(modifier[1:-1])
                                if modifier[0] == '+':
                                    final_result += int(final_result * (percent / 100))
                                    modifier_text += f" + {percent}%"
                                else:  # '-'
                                    final_result -= int(final_result * (percent / 100))
                                    modifier_text += f" - {percent}%"
                            else:
                                value = int(modifier[1:])
                                if modifier[0] == '+':
                                    final_result += value
                                    modifier_text += f" + {value}"
                                else:  # '-'
                                    final_result -= value
                                    modifier_text += f" - {value}"
                        except ValueError:
                            em = discord.Embed(title='**ERROR**',
                                               description=f"Invalid modifier format: `{modifier}`",
                                               color=0xff0000)
                            await ctx.send(embed=em)
                            return

                    # Выбор фразы
                    if final_result == second:
                        phrs = phrasesmax[np.random.randint(0, len(phrasesmax))]
                    elif final_result == num:
                        phrs = phrasesmin[np.random.randint(0, len(phrasesmin))]
                    elif final_result == 42:
                        phrs = phrasesxtra[0]
                    else:
                        phrs = phrases[np.random.randint(0, len(phrases))]

                    if modifiers:
                        em = discord.Embed(title=f'**{phrs}**',
                                           description=f"🎲 You Rolled **{final_result}** (Base: {base_result}{modifier_text}) from {num} to {second}",
                                           color=0x7289da)
                    else:
                        em = discord.Embed(title=f'**{phrs}**',
                                           description=f"🎲 You Rolled **{final_result}** from {num} to {second}",
                                           color=0x7289da)

                else:
                    # Это простой бросок dN
                    try:
                        num = int(base_part)
                        if num <= 0:
                            raise ValueError("Number must be positive")
                    except ValueError:
                        em = discord.Embed(title='**ERROR**',
                                           description="Parameter must be a positive integer!",
                                           color=0xff0000)
                        await ctx.send(embed=em)
                        return

                    base_result = np.random.randint(1, num + 1)
                    final_result = base_result
                    modifier_text = ""

                    # Применяем модификаторы
                    for modifier in modifiers:
                        try:
                            if modifier.endswith('%'):
                                percent = int(modifier[1:-1])
                                if modifier[0] == '+':
                                    final_result += int(final_result * (percent / 100))
                                    modifier_text += f" + {percent}%"
                                else:  # '-'
                                    final_result -= int(final_result * (percent / 100))
                                    modifier_text += f" - {percent}%"
                            else:
                                value = int(modifier[1:])
                                if modifier[0] == '+':
                                    final_result += value
                                    modifier_text += f" + {value}"
                                else:  # '-'
                                    final_result -= value
                                    modifier_text += f" - {value}"
                        except ValueError:
                            em = discord.Embed(title='**ERROR**',
                                               description=f"Invalid modifier format: `{modifier}`",
                                               color=0xff0000)
                            await ctx.send(embed=em)
                            return

                    # Выбор фразы
                    if final_result == num:
                        phrs = phrasesmax[np.random.randint(0, len(phrasesmax))]
                    elif final_result == 1:
                        phrs = phrasesmin[np.random.randint(0, len(phrasesmin))]
                    elif final_result == 42:
                        phrs = phrasesxtra[0]
                    elif final_result == 69:
                        phrs = phrasesxtra[1]
                    else:
                        phrs = phrases[np.random.randint(0, len(phrases))]

                    if modifiers:
                        em = discord.Embed(title=f'**{phrs}**',
                                           description=f"🎲 You Rolled **{final_result}** on d{num}. (Base: {base_result}{modifier_text})",
                                           color=0x7289da)
                    else:
                        em = discord.Embed(title=f'**{phrs}**',
                                           description=f"🎲 You Rolled **{final_result}** on d{num}.",
                                           color=0x7289da)

                em.set_author(name=f"{user}", icon_url=ctx.author.avatar)

            except Exception as e:
                em = discord.Embed(title='**ERROR**',
                                   description=f"Error processing simple roll: {str(e)}",
                                   color=0xff0000)
                await ctx.send(embed=em)
                return

        await ctx.send(embed=em)

    except Exception as e:
        em = discord.Embed(title='**ERROR**',
                           description=f"Unexpected error: {str(e)}",
                           color=0xff0000)
        await ctx.send(embed=em)

@bot.command(invoke_without_command=True, aliases=["l"])
async def loot(ctx):
    user = discord.utils.get(ctx.guild.members, id=int(ctx.message.author.id))

    lt = ["Обычное", "Редкое", "Супер Редкое", "Эпик", "Легендарное", "МИФИК!", "???"]
    cloth = ["Правая рука", "Левая рука", "Голова", "Торс", "Плащ/Накидка", "Ноги", "Шея", "Кольцо", "Карман",
             "Расходник"]
    dictlt = {"Обычное": 0xe1e6ed, "Редкое": 0x04852d, "Супер Редкое": 0x1f65a6, "Эпик": 0x9c3393,
              "Легендарное": 0xd1b91f, "МИФИК!": 0xa61a17, "???": 0x140811}

    numb = np.random.randint(1, 16)
    ltres = lt[np.random.randint(0, len(lt))]
    clothres = cloth[np.random.randint(0, len(cloth))]

    em = discord.Embed(title=f'**Сундук удачи!**',
                       description=f"Вам выпало **{ltres} {clothres}** № **{numb}**",
                       color=dictlt.get(ltres))
    em.set_author(name=f"{user}", icon_url=ctx.author.avatar)

    await ctx.send(embed=em)


# ИГРА LIARS BAR

def CountAlive(players):
    check = 0
    for i in players:
        if players[i][1]:
            check += 1
    return check


def CheckIfOnlyYouWithCards(players, name):
    counter = 0
    for player in players:
        if players[player][4].count(None) == 5 and player != name:
            counter += 1
    if counter == 1:
        return True
    else:
        return False

# Массив для хранения ID игр
games = {}

# Словарь для хранения игроков
players_in_game = {}

# Класс для кнопки "Присоединиться к игре"
class GameStartButton(View):
    def __init__(self, game_id):
        super().__init__()
        self.game_id = game_id
        self.players = {}
        self.game_active = False  # Флаг, показывающий активна ли игра
        self.GameIsOver = False

    @discord.ui.button(label="Присоединиться к игре", style=discord.ButtonStyle.green)
    async def start_game(self, interaction: discord.Interaction, button: discord.ui.Button):
        player_id = interaction.user.id
        player_name = interaction.user.name

        if self.GameIsOver:
            await interaction.response.send_message(f"Игра {self.game_id} Закончена.",
                                                    ephemeral=True)
            return

        # Проверяем, активна ли игра
        if self.game_active:
            await interaction.response.send_message(f"Игра {self.game_id} уже началась. Невозможно присоединиться.",
                                                    ephemeral=True)
            return

        # Если игрок еще не присоединился
        if player_id not in self.players:
            self.players[player_id] = player_name
            await interaction.response.send_message(f"{player_name} присоединился к игре!")
        else:
            await interaction.response.send_message(f"Вы уже присоединились к игре {self.game_id}.", ephemeral=True)

    async def start_game_timer(self, ctx):
        # Ожидаем 30 секунд
        await asyncio.sleep(30)

        # Если игроков недостаточно (меньше 2 или больше 4), удаляем данные
        if len(self.players) < 2 or len(self.players) > 4:
            await ctx.send(
                f"Игра {self.game_id} не состоялась. Недостаточно игроков или слишком много.")
            self.game_active = False  # Закрываем игру для новых игроков
            self.GameIsOver = True
            # Удаляем игру из словарей
            if self.game_id in players_in_game:
                del players_in_game[self.game_id]
            if self.game_id in games:
                del games[self.game_id]
            return

        # Если игра состоялась, начинаем
        self.game_active = True  # Игра началась, запрещаем вступление
        await ctx.send(f"Игра {self.game_id} началась с {len(self.players)} игроками!")
        # Можно добавить дополнительную логику для начала игры
        players_info = "\n".join(
            [f"{player_name} (ID: {player_id})" for player_id, player_name in self.players.items()])
        await ctx.send(f"Игроки в игре {self.game_id}:\n{players_info}")

        # ПИСАЛ Я

        names = [player_name[1] for player_name in self.players.items()]
        np.random.shuffle(names)
        players = {}
        for bebebe in names:
            pid = ""
            for id, name in self.players.items():
                if name == bebebe:
                    pid = id
                    break
            bullet = int(np.random.choice([1,1,2,2,2,3,3,3,3,4,4,4,4,5,5,5,6,6]))
            bullet += 1

            players[bebebe] = [pid, True, 0, bullet, [None, None, None, None, None]]
        RoundCount = 0

        PlayerTurn=0

        while CountAlive(players) > 1:  # Игра работает пока не умер
            np.random.seed()
            # Перед началом раунда
            RoundCount += 1
            RoundIsOver = False
            x = len(names)
            amountCards = int(-0.5 * x ** 2 + 4.5 * x - 4)
            cards = ["Ace"] * amountCards + ["King"] * amountCards + ["Queen"] * amountCards + ["Joker"] * 2
            np.random.shuffle(cards)
            table = np.random.choice(["King", "Queen", "Ace"])
            countDeck = 0
            CardsOnTable = [None, None, None, None, None]
            for k in names:
                for j in range(0, 5):
                    players[k][4][j] = cards[countDeck]
                    countDeck += 1
            bebebe=" >> ".join(names)
            await ctx.send(
                f"**Раунд {RoundCount}**\n{table}'s Table\n Порядок ходов: {bebebe}")

            while not RoundIsOver:  # Раунд
                i = names[(PlayerTurn%len(names))]
                if CheckIfOnlyYouWithCards(players, i):
                    await asyncio.sleep(6)# Автопроверка если едниственный с картами
                    await ctx.send("Только у вас остались карты! Автоматически вы проверяете стол")
                    await ctx.send(f"Игрок <@{players[i][0]}> не верит предыдущему!")
                    await asyncio.sleep(1)
                    # Проверка на ложь
                    checkLied = any(
                        card != table and card != "Joker" for card in CardsOnTable if card is not None)
                    if checkLied:
                        if names.index(i) != 0:
                            WhoToShoot = names[names.index(i) - 1]
                        else:
                            WhoToShoot = names[-1]

                        await ctx.send(f"Игрок <@{players[WhoToShoot][0]}> Соврал!")
                        await asyncio.sleep(2)
                        await ctx.send(f"Игрок <@{players[WhoToShoot][0]}> Стреляет себе в голову...")
                        players[WhoToShoot][2] += 1
                        if players[WhoToShoot][2] == players[WhoToShoot][3]:
                            players[WhoToShoot][1] = False
                            await ctx.send(f"Игрок <@{players[WhoToShoot][0]}> Получил смертельный выстрел!")
                        else:
                            await ctx.send(f"Игрок <@{players[WhoToShoot][0]}> Выживает...")
                    else:
                        await ctx.send(f"Предыдущий игрок не лгал! Стреляйте себе в голову...")
                        players[i][2] += 1
                        if players[i][2] == players[i][3]:
                            players[i][1] = False
                            await ctx.send(f"Игрок <@{players[i][0]}> Получил смертельный выстрел!")
                        else:
                            await ctx.send(f"Игрок <@{players[i][0]}> Выживает...")

                    PlayerTurn+=1
                    print(names, players, "\n", RoundCount, PlayerTurn)
                    RoundIsOver = True

                if RoundIsOver == True:
                    await ctx.send(f"Раунд {RoundCount} окончен!")
                    break

                print(names, players, "\n", RoundCount, PlayerTurn)
                await asyncio.sleep(3)
                await ctx.send(f"Ход игрока <@{players[i][0]}>")

                if players[i][4].count(None) == 5 or not players[i][1]:
                    continue

                selectedCards = [None, None, None, None, None]

                # МЕНЮ ХОДА

                # Получаем ID пользователя, который должен взаимодействовать с меню
                allowed_user_id = players[i][0]

                # Создаем объект View с таймаутом 60 секунд
                view = View(timeout=60)
                button_press_count = {f"button{i}": 0 for i in range(1, 7)}  # Счетчик нажатий для каждой кнопки

                CopiedPlayerCards = players[i][4].copy()

                interaction_completed = False  # Флаг завершения взаимодействия

                async def button_callback(interaction: discord.Interaction):
                    nonlocal interaction_completed
                    nonlocal CardsOnTable
                    nonlocal button_press_count
                    nonlocal RoundIsOver
                    nonlocal PlayerTurn

                    # Проверяем, что взаимодействует только разрешённый пользователь
                    if interaction.user.id != allowed_user_id:
                        await interaction.response.send_message("Вы не можете взаимодействовать с этим меню.",
                                                                ephemeral=True)
                        return

                    # Получаем custom_id кнопки
                    button_id = interaction.data['custom_id']

                    # Логика для кнопок 1-5
                    if button_id.startswith("button") and button_id not in ["button6", "button7"]:
                        index = int(button_id[-1]) - 1
                        if button_press_count[button_id] % 2 == 0:
                            button_press_count[button_id] += 1
                            selectedCards[index] = players[i][4][index]
                            players[i][4][index] = None
                            await interaction.response.send_message(
                                f"Вы выбрали карту: {index + 1}, {selectedCards}")
                        else:
                            button_press_count[button_id] += 1
                            players[i][4][index] = selectedCards[index]
                            selectedCards[index] = None
                            await interaction.response.send_message(f"Вы отменили выбор карты: {index + 1}")

                    # Логика для кнопки "Сбросить на стол" (button6)
                    elif button_id == "button6":
                        PlayerTurn += 1
                        none_count = selectedCards.count(None)
                        if none_count not in [2, 3, 4]:
                            await interaction.response.send_message(
                                f"Неверное количество выбранных карт. Пожалуйста, выберите карты снова.{selectedCards},{CardsOnTable}",
                                ephemeral=True
                            )
                        else:
                            interaction_completed = True  # Завершаем взаимодействие
                            CardsOnTable = selectedCards
                            for button in view.children:
                                button.disabled = True
                            view.stop()
                            await interaction.response.send_message(f"Вы сбросили карты на стол: {selectedCards}")
                            await ctx.send(
                                f"Игрок {allowed_user.mention} Claims {(len(selectedCards) - CardsOnTable.count(None))} {table}'s.")

                    # Логика для кнопки "Осудить во лжи" (button7)
                    elif button_id == "button7":
                        PlayerTurn += 1
                        await interaction.response.send_message(f"Вы решили проверить стол...")
                        await ctx.send(f"Игрок <@{players[i][0]}> не верит предыдущему!")
                        await asyncio.sleep(1)
                        interaction_completed = True  # Завершаем взаимодействие
                        # Проверка на ложь
                        checkLied = any(
                            card != table and card != "Joker" for card in CardsOnTable if card is not None)
                        if checkLied:
                            if names.index(i) != 0:
                                WhoToShoot = names[names.index(i) - 1]
                            else:
                                WhoToShoot = names[-1]

                            await ctx.send(f"Игрок <@{players[WhoToShoot][0]}> Соврал!")
                            await asyncio.sleep(2)
                            await ctx.send(f"Игрок <@{players[WhoToShoot][0]}> Стреляет себе в голову...")
                            players[WhoToShoot][2] += 1
                            if players[WhoToShoot][2] == players[WhoToShoot][3]:
                                players[WhoToShoot][1] = False
                                await ctx.send(f"Игрок <@{players[WhoToShoot][0]}> Получил смертельный выстрел!")
                            else:
                                await ctx.send(f"Игрок <@{players[WhoToShoot][0]}> Выживает...")
                        else:
                            await ctx.send(f"Предыдущий игрок не лгал! Стреляйте себе в голову...")
                            players[i][2] += 1
                            if players[i][2] == players[i][3]:
                                players[i][1] = False
                                await ctx.send(f"Игрок <@{players[i][0]}> Получил смертельный выстрел!")
                            else:
                                await ctx.send(f"Игрок <@{players[i][0]}> Выживает...")

                        for button in view.children:
                            button.disabled = True
                        view.stop()
                        RoundIsOver = True

                # Создаем View и добавляем кнопки
                view = View(timeout=60)
                buttons = []

                # Добавляем кнопки 1-5
                for o in range(5):
                    button = Button(
                        label=str(o + 1),
                        style=discord.ButtonStyle.primary,
                        custom_id=f"button{o + 1}",
                        disabled=players[i][4][o] is None
                    )
                    button.callback = button_callback
                    buttons.append(button)

                # Добавляем кнопку "Сбросить на стол"
                reset_button = Button(label="Сбросить на стол", style=discord.ButtonStyle.green,
                                      custom_id="button6")
                reset_button.callback = button_callback
                buttons.append(reset_button)

                # Добавляем кнопку "Осудить во лжи"
                check_button = Button(
                    label="Осудить во лжи", style=discord.ButtonStyle.danger, custom_id="button7",
                    disabled=CardsOnTable == [None] * 5
                )
                check_button.callback = button_callback
                buttons.append(check_button)

                # Добавляем кнопки в View
                for button in buttons:
                    view.add_item(button)

                # Отправляем сообщение с View
                card_message = f"**Игра {self.game_id}**\n**Раунд: {RoundCount}**\n*Выстрелов: {players[i][2]}*\n*Стол: {table}*\nВаши карты:\n" + "\t".join(
                    [card if card is not None else "Пусто" for card in players[i][4]]
                )
                allowed_user = await ctx.bot.fetch_user(allowed_user_id)
                message = await allowed_user.send(f"{card_message}\nВыберите действие, {allowed_user.mention}:",
                                                  view=view)

                # Ожидаем взаимодействия
                await view.wait()

                # Обработка завершения ожидания
                if not interaction_completed:
                    await message.edit(content="Время истекло. Выполняем действие по умолчанию.")
                    selectedCards = [None, None, None, None, None]
                    players[i][4] = CopiedPlayerCards.copy()
                    for cc in range(5):
                        if players[i][4][cc] is not None:
                            selectedCards[cc] = players[i][4][cc]
                            players[i][4][cc] = None
                            CardsOnTable = selectedCards
                            await ctx.send(
                                f"Игрок {allowed_user.mention} Claims {(len(selectedCards) - CardsOnTable.count(None))} {table}'s."
                            )
                            PlayerTurn += 1
                            break

        # Конец игры
        self.GameIsOver = True
        winner = ""
        for i in names:
            if players[i][1] == True:
                winner = players[i][0]
                continue
        await ctx.send(f"Игра {self.game_id} Окончена! победил <@{winner}>")
        print(names, players)
        self.game_active = False  # Закрываем игру для новых игроков
        # Удаляем игру из словарей
        if self.game_id in players_in_game:
            del players_in_game[self.game_id]
        if self.game_id in games:
            del games[self.game_id]
            return


# Команда для начала игры
@bot.command()
async def start(ctx):
    game_id = len(games) + 1  # Генерация уникального ID игры
    game = GameStartButton(game_id)  # Создание нового объекта игры
    games[game_id] = game  # Добавляем игру в список активных игр
    players_in_game[game_id] = game  # Добавляем игру в словарь с игроками

    # Отправляем сообщение с кнопкой
    await ctx.send(
        f"Нажмите на кнопку, чтобы присоединиться к игре №{game_id}!",
        view=game
    )

    # Запускаем таймер для игры
    await game.start_game_timer(ctx)


@bot.command()
async def get_games(ctx):
    if not games:
        await ctx.send("Нет активных игр.")
        return

    # Создаем список всех игр и игроков
    games_info = []
    for game_id, game in games.items():
        players = ', '.join(game.players.values())
        games_info.append(f"Игра {game_id}: {players if players else 'Нет игроков'}")

    # Отправляем информацию о всех играх
    await ctx.send("\n".join(games_info))

@bot.tree.command(name="hello", description="Say hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Привет, {interaction.user.mention}!")

@bot.command(name="h", aliases=["help"])
async def help_cmd(ctx):
    embed = discord.Embed(
        title="📖 **Помощь по боту**",
        description=(
            "**Префиксы:** `!`, `.`, `l`\n"
        ),
        color=0x7289da
    )

    embed.add_field(
        name="🎲 `dice` — Бросок кубиков",
        value=(
            "**Альт:** `r`, `roll`, `d`\n"
            "Бросает кубики во всех форматах ниже. Поддерживает модификаторы "
            "`+N`, `-N`, `+N%`, `-N%`.\n"
            "Ограничения: до 100 кубиков за бросок, до 10000 сторон у кубика.\n"
            "Особые фразы для максимума, минимума, `42` и `69`."
        ),
        inline=False
    )

    embed.add_field(
        name="📖 Как кидать кубик для слабо думающих",
        value=(
            "`!d` — основная команда (можно также `!r`, `!roll`)\n"
            "`!d 100` — кинуть от 1 до 100\n"
            "`!d 20 100` — кинуть от 20 до 100\n"
            "`!d 2d50` — кинуть 2 раза от 1 до 50\n"
            "`!d 6d13 8d15 3d60` — дз подумать что будет\n"
            "`!d хуй, пизда, 36` — выбор из трёх вариантов, разграничивать запятой\n"
            "`!d 1d20+5 2d20-5` — добавить/убавить к **каждому** кубику\n"
            "`!d 20 +3` — прибавить +3 к результату (также `-число`)\n"
            "`!d 20 +%50` — добавить 50% к результату (выпало 10 → стало 15), "
            "также можно `-%число`\n"
            "`!d 3d20 1d40 +3` — добавит +3 **только к общему** результату, "
            "а не к каждому кубику (также `-число`, `±%число`)"
        ),
        inline=False
    )

    embed.add_field(
        name="🎁 `loot` — Сундук удачи",
        value=(
            "**Альт:** `l`\n"
            "Случайно выдаёт предмет с редкостью (Обычное → Редкое → Супер Редкое → "
            "Эпик → Легендарное → МИФИК! → ???), часть экипировки и номер. "
            "Цвет embed зависит от редкости."
        ),
        inline=False
    )

    embed.add_field(
        name="😀 `emoji` — Поиск эмоций 7TV",
        value=(
            "**Альт:** `e`, `em`, `7tv`\n"
            "Ищет эмоцию по названию и отправляет файлом (`gif` / `avif`).\n"
            "`!emoji pepe` — первая эмоция, `!emoji pepe 2` — вторая.\n"
            "Кулдаун: 1 раз в 10 секунд на пользователя.\n"
        ),
        inline=False
    )

    embed.add_field(
        name="🎭 `start` — Liars Bar",
        value=(
            "Создаёт игру с кнопкой «Присоединиться». Сбор 30 секунд, нужно 2–4 игрока.\n"
            "Механика: раунды, карты (`Ace` / `King` / `Queen` / `Joker`), "
            "заявление карт стола, кнопки выбора `1–5`, «Сбросить на стол», "
            "«Осудить во лжи».\n"
            "Кто соврал — стреляет себе в голову. У кого кончились карты — пропускает ход.\n"
            "Меню хода приходит в ЛС, таймаут 60 секунд. Игра идёт до последнего выжившего."
        ),
        inline=False
    )

    embed.add_field(
        name="📋 `get_games` — Активные игры",
        value="Показывает список активных игр Liars Bar и их игроков.",
        inline=False
    )

    embed.set_footer(text=f"Запросил: {ctx.author.display_name}")
    await ctx.send(embed=embed)

bot.run(settings['token'])