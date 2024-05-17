from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, WebAppInfo
import aiohttp

bot = Bot('6757216885:AAGbueKtia5rkn8oSkbgVNWciEixY2F1TJg')
dp = Dispatcher(bot)

regions = {
    'almaty': "Алматы",
    'astana': "Астана",
    'shymkent': "Шымкент",
    'abay_oblast': "Абай облысы",
    'akmolinsk_oblast': "Ақмола облысы",
    'aktobe_oblast': "Ақтөбе облысы",
    'almaty_region': "Алматы облысы",
    'atyrau_oblast': "Атырау облысы",
    'east_kazakhstan_oblast': "Шығыс Қазақстан облысы",
    'zhambyl_oblast': "Жамбыл облысы",
    'zhetysu_oblast': "Жетісу облысы",
    'west_kazakhstan_oblast': "Батыс Қазақстан облысы",
    'karaganda_oblast': "Қарағанды облысы",
    'kostanay_oblast': "Қостанай облысы",
    'kyzylorda_oblast': "Қызылорда облысы",
    'mangystau_oblast': "Маңғыстау облысы",
    'pavlodar_oblast': "Павлодар облысы",
    'north_kazakhstan_oblast': "Солтүстік Қазақстан облысы",
    'turkestan_oblast': "Түркістан облысы",
    'ulytau_oblast': "Ұлытау облысы"
}

keyboard_ru = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(region_name)] for region_name in regions.values()],
    resize_keyboard=True
)
keyboard_kaz = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(region_name)] for region_name in regions.values()],
    resize_keyboard=True
)

async def get_schools_in_region(region_key: str):
    url = f"https://bilimge.kz/admins/api/school/?region={region_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return data

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("RU")],
            [KeyboardButton("KAZ")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите язык:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "RU")
async def choose_language_ru(message: types.Message):
    await message.answer("Выберите регион:", reply_markup=keyboard_ru)

@dp.message_handler(lambda message: message.text == "KAZ")
async def choose_language_kaz(message: types.Message):
    await message.answer("Регион таңдаңыз:", reply_markup=keyboard_kaz)

@dp.message_handler(lambda message: message.text in regions.values())
async def handle_region_selection(message: types.Message):
    region_key = None
    for key, value in regions.items():
        if message.text == value:
            region_key = key
            break
    if not region_key:
        await message.answer("Ошибка: регион не найден.")
        return

    schools_data = await get_schools_in_region(region_key)
    if not schools_data:
        await message.answer("Учебные заведения в выбранном регионе не найдены.")
        return

    keyboard_buttons = []
    for school in schools_data:
        school_name = school.get("school_kz_name")
        school_url = school.get("url")
        callback_data = f"school_{school_url}"
        keyboard_buttons.append([InlineKeyboardButton(text=school_name, callback_data=callback_data)])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer("Учебные заведения в выбранном регионе:", reply_markup=keyboard)

@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('school_'))
async def handle_school_selection(callback_query: CallbackQuery):
    school_url = callback_query.data.split('_')[1]
    web_app_url = f"https://my.kestesi.kz/{school_url}"
    button = InlineKeyboardButton(text="Открыть веб-приложение", web_app=WebAppInfo(url=web_app_url))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await callback_query.message.answer("Откройте веб-приложение, нажав на кнопку ниже:", reply_markup=keyboard)
    await callback_query.answer()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
