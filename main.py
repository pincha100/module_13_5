from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor


API_TOKEN = ''

# Создаем объекты бота и диспетчера с хранилищем состояний в памяти
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определяем группу состояний для цепочки "Calories"
class UserState(StatesGroup):
    age = State()       # Состояние для ввода возраста
    growth = State()    # Состояние для ввода роста
    weight = State()    # Состояние для ввода веса

# Создание клавиатуры с двумя кнопками: 'Рассчитать' и 'Информация'
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calories = KeyboardButton('Рассчитать')
button_info = KeyboardButton('Информация')
keyboard.add(button_calories, button_info)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "Привет! Я бот, помогающий твоему здоровью.\n"
        "Нажми кнопку 'Рассчитать', чтобы начать расчёт нормы калорий.",
        reply_markup=keyboard
    )

# Обработчик кнопки 'Рассчитать'
@dp.message_handler(Text(equals="Рассчитать", ignore_case=True))
async def set_age(message: types.Message):
    await message.answer("Введите свой возраст:")
    await UserState.age.set()

# Обработчик кнопки 'Информация'
@dp.message_handler(Text(equals="Информация", ignore_case=True))
async def info(message: types.Message):
    await message.answer(
        "Этот бот поможет вам рассчитать вашу норму калорий.\n"
        "Введите 'Рассчитать' и следуйте инструкциям."
    )

# Обработка возраста и переход к росту
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0:
            raise ValueError("Возраст должен быть положительным числом.")
    except ValueError as e:
        await message.answer("Пожалуйста, введите корректный возраст (целое положительное число).")
        return  # Не переходим к следующему состоянию

    await state.update_data(age=age)  # Сохраняем возраст
    await message.answer("Введите свой рост (в сантиметрах):")
    await UserState.growth.set()

# Обработка роста и переход к весу
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    try:
        growth = int(message.text)
        if growth <= 0:
            raise ValueError("Рост должен быть положительным числом.")
    except ValueError as e:
        await message.answer("Пожалуйста, введите корректный рост (целое положительное число).")
        return  # Не переходим к следующему состоянию

    await state.update_data(growth=growth)  # Сохраняем рост
    await message.answer("Введите свой вес (в килограммах):")
    await UserState.weight.set()

# Обработка веса и подсчёт нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    try:
        weight = int(message.text)
        if weight <= 0:
            raise ValueError("Вес должен быть положительным числом.")
    except ValueError as e:
        await message.answer("Пожалуйста, введите корректный вес (целое положительное число).")
        return  # Не продолжаем дальше

    await state.update_data(weight=weight)  # Сохраняем вес

    # Получаем все данные пользователя
    data = await state.get_data()
    age = data.get("age")
    growth = data.get("growth")
    weight = data.get("weight")

    # Формула Миффлина-Сан Жеора для мужчин:
    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    # Для женщин можно использовать:
    # calories = 10 * weight + 6.25 * growth - 5 * age - 161

    # Отправляем результат пользователю
    await message.answer(f"Ваша норма калорий: {calories:.2f} ккал в день.")

    # Завершаем машину состояний
    await state.finish()

# Обработчик всех прочих сообщений
@dp.message_handler()
async def all_messages(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
