import sqlite3
import random
from aiogram import Bot, Dispatcher, executor, types

#SQLite
conn = sqlite3.connect('dice_game.db')
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS games
                (id INTEGER PRIMARY KEY AUTOINCREMENT, creator_id INTEGER, stake REAL, player1_id INTEGER, player2_id INTEGER, winner_id INTEGER)''')

conn.commit()


API_TOKEN = 'tokenblya'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# /newgame 
@dp.message_handler(commands=['newgame'])
async def new_game(message: types.Message):
    stake = float(message.get_args()) 
    player1_id = message.from_user.id
    # Добавляем новую игру в базу данных
    cursor.execute('INSERT INTO games (creator_id, stake, player1_id) VALUES (?, ?, ?)', (player1_id, stake, player1_id))
    conn.commit()
    await message.answer(f'Новая игра создана! Пригласите другого игрока с помощью команды /joingame')

# /joingame для присоединения к существующей игре
@dp.message_handler(commands=['joingame'])
async def join_game(message: types.Message):
    game_id = int(message.get_args())
    player2_id = message.from_user.id
    cursor.execute('UPDATE games SET player2_id=? WHERE id=?', (player2_id, game_id))
    conn.commit()
    await message.answer(f'Вы присоединились к игре {game_id}! Ожидайте результат броска кубика.')

# /roll для броска кубика
@dp.message_handler(commands=['roll'])
async def roll_dice(message: types.Message):
    game_id = int(message.get_args())
    cursor.execute('SELECT stake, player1_id, player2_id FROM games WHERE id=?', (game_id,))
    row = cursor.fetchone()
    stake, player1_id, player2_id = row
    result1 = random.randint(1, 6)
    result2 = random.randint(1, 6)

    # Можем повотрить спасибо деду за попеду
    if result1 > result2:
        winner_id = player1_id
    elif result2 > result1:
        winner_id = player2_id
    else:
        winner_id = None  # Ничья

    cursor.execute('UPDATE games SET winner_id=? WHERE id=?', (winner_id, game_id))
    conn.commit()

    if winner_id:
        await message.answer(f'Бросок кубика: Игрок 1 - {result1}, Игрок 2 - {result2}. Победил игрок с ID {winner_id}!')
    else:
        await message.answer(f'Бросок кубика: Игрок 1 - {result1}, Игрок 2 - {result2}. Ничья!')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
