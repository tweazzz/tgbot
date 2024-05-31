from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
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

regions_ru = {
    'almaty': "Алматы",
    'astana': "Астана",
    'shymkent': "Шымкент",
    'abay_oblast': "Абайская область",
    'akmolinsk_oblast': "Акмолинская область",
    'aktobe_oblast': "Актюбинская область",
    'almaty_region': "Алматинская область",
    'atyrau_oblast': "Атырауская область",
    'east_kazakhstan_oblast': "Восточно-Казахстанская область",
    'zhambyl_oblast': "Жамбылская область",
    'zhetysu_oblast': "Жетысуская область",
    'west_kazakhstan_oblast': "Западно-Казахстанская область",
    'karaganda_oblast': "Карагандинская область",
    'kostanay_oblast': "Костанайская область",
    'kyzylorda_oblast': "Кызылординская область",
    'mangystau_oblast': "Мангистауская область",
    'pavlodar_oblast': "Павлодарская область",
    'north_kazakhstan_oblast': "Северо-Казахстанская область",
    'turkestan_oblast': "Туркестанская область",
    'ulytau_oblast': "Ульятауская область"
}

keyboard_ru = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(region_name)] for region_name in regions_ru.values()],
    resize_keyboard=True
)
keyboard_kaz = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(region_name)] for region_name in regions.values()],
    resize_keyboard=True
)

user_language = {}
user_region = {}

async def get_schools_in_region(region_key: str):
    url = f"https://bilimge.kz/admins/api/school/?region={region_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()
    return data

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_language[message.from_user.id] = None  # сбрасываем выбор языка
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
    user_language[message.from_user.id] = 'ru'
    await message.answer("Выберите регион:", reply_markup=keyboard_ru)

@dp.message_handler(lambda message: message.text == "KAZ")
async def choose_language_kaz(message: types.Message):
    user_language[message.from_user.id] = 'kz'
    await message.answer("Регион таңдаңыз:", reply_markup=keyboard_kaz)

@dp.callback_query_handler(lambda query: query.data.startswith("open_school_"))
async def open_school(query: types.CallbackQuery):
    school_url = query.data.split("open_school_", 1)[1]  # Получаем URL школы из callback data
    user_id = query.from_user.id
    language = user_language.get(user_id, 'ru')

    if language == 'ru':
        web_app_url = f"https://my.kestesi.kz/ru/{school_url}/"
        message_text = "Нажмите на кнопку, чтобы открыть веб-приложение:"
        back_to_schools_text = "Выбрать другую школу"
        back_to_regions_text = "Выбрать другой регион"
    else:
        web_app_url = f"https://my.kestesi.kz/{school_url}"
        message_text = "Веб-қосымшаны ашу үшін түймені басыңыз:"
        back_to_schools_text = "Басқа мектепті таңдау"
        back_to_regions_text = "Басқа регионды таңдау"

    button = InlineKeyboardButton(text="Открыть веб-приложение", web_app=WebAppInfo(url=web_app_url))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    
    # Отправляем сообщение с кнопкой открытия веб-приложения
    await query.message.answer(message_text, reply_markup=keyboard)
    
    # Кнопки для выбора другой школы или региона
    back_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(back_to_schools_text)],
            [KeyboardButton(back_to_regions_text)]
        ],
        resize_keyboard=True
    )
    
    await query.message.answer(f"my.kestesi.kz", reply_markup=back_keyboard)
    await query.answer()  # Отвечаем на callback query

@dp.message_handler(lambda message: message.text in regions_ru.values() or message.text in regions.values())
async def handle_region_selection(message: types.Message):
    user_id = message.from_user.id
    language = user_language.get(user_id)

    if language == 'ru':
        regions_dict = regions_ru
    elif language == 'kz':
        regions_dict = regions
    else:
        await message.answer("Пожалуйста, сначала выберите язык, отправив команду /start.")
        return

    region_key = None
    for key, value in regions_dict.items():
        if message.text == value:
            region_key = key
            break
    if not region_key:
        await message.answer("Ошибка: регион не найден.")
        return

    user_region[user_id] = region_key  # Сохраняем выбранный регион для пользователя

    schools_data = await get_schools_in_region(region_key)
    if not schools_data:
        await message.answer("Учебные заведения в выбранном регионе не найдены.")
        return

    keyboard_buttons = []
    for school in schools_data:
        if language == 'ru':
            school_name = school.get("school_ru_name")
        else:
            school_name = school.get("school_kz_name")
        school_url = school.get("url")

        button = InlineKeyboardButton(text=school_name, callback_data=f"open_school_{school_url}")
        keyboard_buttons.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer("Учебные заведения в выбранном регионе:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in ["Выбрать другую школу", "Басқа мектепті таңдау"])
async def choose_another_school(message: types.Message):
    user_id = message.from_user.id
    region_key = user_region.get(user_id)

    if not region_key:
        await message.answer("Ошибка: регион не найден. Пожалуйста, выберите регион снова.")
        return

    language = user_language.get(user_id)

    schools_data = await get_schools_in_region(region_key)
    if not schools_data:
        await message.answer("Учебные заведения в выбранном регионе не найдены.")
        return

    keyboard_buttons = []
    for school in schools_data:
        if language == 'ru':
            school_name = school.get("school_ru_name")
        else:
            school_name = school.get("school_kz_name")
        school_url = school.get("url")

        button = InlineKeyboardButton(text=school_name, callback_data=f"open_school_{school_url}")
        keyboard_buttons.append([button])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer("Учебные заведения в выбранном регионе:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in ["Выбрать другой регион", "Басқа регионды таңдау"])
async def choose_another_region(message: types.Message):
    user_id = message.from_user.id
    language = user_language.get(user_id)

    if language == 'ru':
        await choose_language_ru(message)
    elif language == 'kz':
        await choose_language_kaz(message)
    else:
        await message.answer("Пожалуйста, сначала выберите язык, отправив команду /start.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
