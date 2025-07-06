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
    user = discord.utils.get(ctx.guild.members, id=int(ctx.message.author.id))

    if params.find(",") != -1:
        '''выбор вариантов'''

        lparams = params.split(",")
        res = lparams[np.random.randint(0, len(lparams))]
        phrs = phrases[np.random.randint(0, len(phrases))]

        if res[0] == " ":
            res = res[1:]

        em = discord.Embed(title=f'**{phrs}**',
                           description=f"{res}",
                           color=0x7289da)
        em.set_author(name=f"{user}", icon_url=ctx.author.avatar)

    elif params.find("d") != -1:


        '''кубы с d и модификаторами'''

        lparams = params.split(" ")
        results = []
        res = 0
        count = 0
        number = 0
        dice_pattern = re.compile(r'(\d*)d(\d+)([+-]\d+)?')

        paramslast = lparams[-1]
        isextramod = False

        if paramslast.find("+") != -1 or paramslast.find("-") != -1 or paramslast.find("-%") != -1 or paramslast.find("+%") != -1:
            lparams.pop()
            isextramod = True

        for cube in lparams:
            match = dice_pattern.fullmatch(cube.strip())
            if not match:
                em = discord.Embed(title=f'**ERROR**',
                                   description=f"Invalid format: `{cube}`",
                                   color=0xff0000)
                await ctx.send(embed=em)
                return

            dice_count = int(match.group(1)) if match.group(1) else 1
            dice_sides = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0
            count += dice_count
            number += dice_sides
            if count > 100:
                em = discord.Embed(title=f'**ERROR**',
                                   description=f"No more than 100 cubes!",
                                   color=0xff0000)
                await ctx.send(embed=em)
                return

            if dice_sides > 10000:
                em = discord.Embed(title=f'**ERROR**',
                                   description=f"No more than 10000 sides!",
                                   color=0xff0000)
                await ctx.send(embed=em)
                return

            for _ in range(dice_count):
                roll = np.random.randint(1, dice_sides + 1)
                total = roll + modifier
                results.append((roll, modifier, total))
                res += total

        # Формируем строку с бросками и модификаторами

        # Формируем строку с бросками и модификаторами с пробелами между плюсами
        plu = ""
        for roll, mod, total in results:
            if mod != 0:
                mod_str = f"{'+' if mod > 0 else ''}{mod}"
                plu += f" + ({roll}{mod_str}={total})"
            else:
                plu += f" + {roll}"
        plu = plu[3:]

        # Выбор фразы

        if np.random.randint(0, 3) == 1:
            phrs = phrases[np.random.randint(0, len(phrases))]

        else:
            phrs = phrasesd[np.random.randint(0, len(phrasesd))]

        if isextramod == False:

            em = discord.Embed(title=f'**{phrs}**',
                               description=f"🎲 You Rolled **{res}**. (*{plu}*)",
                               color=0x7289da)

            em.set_author(name=f"{user}", icon_url=ctx.author.avatar)

        else:
            match paramslast:
                case p if (p.find('+%') != -1):
                    resnew = res + int(res * (int(paramslast[2:]) / 100))
                case p if (p.find('-%') != -1):
                    resnew = res - int(res * (int(paramslast[2:]) / 100))
                case p if (p.find('+') != -1):
                    resnew = res + int(paramslast[1:])
                case p if (p.find('-') != -1):
                    resnew = res - int(paramslast[1:])

            em = discord.Embed(title=f'**{phrs}**',
                               description=f"🎲 You Rolled **{resnew}**, Actually **{res}{paramslast}** (*{plu}*)",
                               color=0x7289da)

            em.set_author(name=f"{user}", icon_url=ctx.author.avatar)


    else:

        '''1 или промежуток или +-'''
        if params.find(" +") != -1 or params.find(" -") != -1 or params.find(" -%") != -1 or params.find(" +%") != -1:
            lparams = params.split(' ')

            if len(lparams) > 2:
                em = discord.Embed(title=f'**ERROR**',
                                   description=f"Use 1-2 integer numbers or +-% statements, words divided by (',') or follow [int]d[int] pattern!",
                                   color=0xff0000)
                await ctx.send(embed=em)
                return

            num = int(lparams[0])
            func = lparams[1]

            res = np.random.randint(1, int(num) + 1)

            if res == int(num):
                phrs = phrasesmax[np.random.randint(0, len(phrasesmax))]
            elif res == 1:
                phrs = phrasesmin[np.random.randint(0, len(phrasesmin))]
            elif res == 42:
                phrs = phrasesxtra[0]
            elif res == 69:
                phrs = phrasesxtra[1]
            else:
                phrs = phrases[np.random.randint(0, len(phrases))]

            match func:
                case p if (p.find('+%') != -1):
                    resnew = res + int(res * (int(func[2:]) / 100))
                case p if (p.find('-%') != -1):
                    resnew = res - int(res * (int(func[2:]) / 100))
                case p if (p.find('+') != -1):
                    resnew = res + int(func[1:])
                case p if (p.find('-') != -1):
                    resnew = res - int(func[1:])

            em = discord.Embed(title=f'**{phrs}**',
                               description=f"🎲 You Rolled **{resnew}** on d{num}. (actually **{res}{func}**)",
                               color=0x7289da)
            em.set_author(name=f"{user}", icon_url=ctx.author.avatar)

        elif params.find(' ') != -1:
            lparams = params.split(' ')

            if len(lparams) > 2:
                em = discord.Embed(title=f'**ERROR**',
                                   description=f"Use 1-2 integer numbers or +-% statements, words divided by (',') or follow [int]d[int] pattern!",
                                   color=0xff0000)
                await ctx.send(embed=em)
                return

            num = int(lparams[0])
            second = int(lparams[1])

            res = np.random.randint(num, second + 1)

            if res == int(second):
                phrs = phrasesmax[np.random.randint(0, len(phrasesmax))]
            elif res == int(num):
                phrs = phrasesmin[np.random.randint(0, len(phrasesmin))]
            elif res == 42:
                phrs = phrasesxtra[0]
            else:
                phrs = phrases[np.random.randint(0, len(phrases))]

            em = discord.Embed(title=f'**{phrs}**',
                               description=f"🎲 You Rolled **{res}**. From {num} to {second}",
                               color=0x7289da)
            em.set_author(name=f"{user}", icon_url=ctx.author.avatar)

        else:

            num = int(params)

            res = np.random.randint(1, int(num) + 1)

            if res == int(num):
                phrs = phrasesmax[np.random.randint(0, len(phrasesmax))]
            elif res == 1:
                phrs = phrasesmin[np.random.randint(0, len(phrasesmin))]
            elif res == 42:
                phrs = phrasesxtra[0]
            elif res == 69:
                phrs = phrasesxtra[1]
            else:
                phrs = phrases[np.random.randint(0, len(phrases))]

            em = discord.Embed(title=f'**{phrs}**',
                               description=f"🎲 You Rolled **{res}** on d{num}.",
                               color=0x7289da)
            em.set_author(name=f"{user}", icon_url=ctx.author.avatar)

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


bot.run(settings['token'])