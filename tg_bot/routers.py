from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Router
from dotenv import load_dotenv
import os
import httpx

API_URL = "http://webapp.local/api/v1/products"
load_dotenv()
router = Router()
SECRET_TOKEN = os.getenv("SECRET_TOKEN")

class Dialog(StatesGroup):
    article_num = State()

def get_product_info_button():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Получить информацию по товару")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

@router.message(Command("start"))
async def send_info(message: Message):
    await message.answer(
        "Нажмите на кнопку ниже, чтобы получить информацию по товару:",
        reply_markup=get_product_info_button()
    )

@router.message(lambda msg: msg.text == "Получить информацию по товару")
async def start_work(message: Message, state: FSMContext):
    await state.set_state(Dialog.article_num)
    await message.answer("Введите артикул товара:")

@router.message(Dialog.article_num)
async def ans(message: Message, state: FSMContext):
    articul = message.text.strip()
    payload = {
        "articul": articul
    }
    headers = {
        "Authorization": f"Bearer {SECRET_TOKEN}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                await message.answer(
                    f"Наименование товара: {data['name']}\n"
                    f"Рейтинг товара: {data['rate']}\n"
                    f"Количество на складах: {data['number']}\n"
                    f"Цена (в рублях): {data['price']}"
                )

            else:
                await message.answer(f"Ошибка: {response.json().get('detail', 'Неизвестная ошибка')}")
        except httpx.HTTPError as e:
            await message.answer("Произошла ошибка при обращении к серверу")
            print(f"Ошибка HTTP-запроса: {e}")
    await state.clear()
