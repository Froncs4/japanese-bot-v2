import aiohttp
import io
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.menu import get_tutor_exit_keyboard
from config import HTTP_TIMEOUT

router = Router()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.1-8b-instant"  
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_WHISPER_URL = "https://api.groq.com/openai/v1/audio/transcriptions"

class TutorState(StatesGroup):
    chatting = State()

ROLES = {
    "default": "Ты — дружелюбный репетитор японского языка по имени Акира. Общайся с учеником (уровень N5). Пиши просто. ВСЕГДА добавляй транскрипцию (ромадзи) и перевод на русский в скобках. Мягко исправляй ошибки.",
    "waiter": "Ты — официант в японской Идзакае (Токио). Ученик — посетитель. Предлагай меню, спрашивай, что он хочет. ВСЕГДА добавляй транскрипцию (ромадзи) и перевод на русский.",
    "tourist": "Ты — японский турист, потерявшийся в городе ученика. Спрашивай дорогу на японском. Ты немного напуган. ВСЕГДА добавляй транскрипцию (ромадзи) и перевод на русский.",
    "hr": "Ты — строгий HR-менеджер японской IT-компании. Проводишь собеседование. Спрашивай про опыт и почему он хочет работать в Японии. ВСЕГДА добавляй транскрипцию (ромадзи) и перевод на русский."
}

def get_tutor_roles_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Сенсей Акира (Учитель)", callback_data="tutor_role:default")],
        [InlineKeyboardButton(text="🍜 Официант в Идзакае", callback_data="tutor_role:waiter")],
        [InlineKeyboardButton(text="🗺️ Потерянный турист", callback_data="tutor_role:tourist")],
        [InlineKeyboardButton(text="👔 HR: Собеседование", callback_data="tutor_role:hr")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu:back")]
    ])

async def ask_groq_api(history: list) -> str:
    if not API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured")
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MODEL_NAME, "messages": history, "temperature": 0.7, "max_tokens": 250}
    timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(GROQ_API_URL, headers=headers, json=payload) as response:
            if response.status == 200:
                data = await response.json()
                return data["choices"][0]["message"]["content"]
            else:
                raise RuntimeError(f"Groq API error: {response.status}")

async def transcribe_audio(audio_bytes: bytes) -> str:
    if not API_KEY:
        return ""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = aiohttp.FormData()
    data.add_field('file', audio_bytes, filename='voice.ogg', content_type='audio/ogg')
    data.add_field('model', 'whisper-large-v3-turbo')
    timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(GROQ_WHISPER_URL, headers=headers, data=data) as response:
            if response.status == 200:
                return (await response.json()).get("text", "")
            return ""

@router.callback_query(F.data == "menu:tutor")
async def choose_tutor_role(callback: CallbackQuery):
    await callback.answer()
    try: await callback.message.delete()
    except: pass
    await callback.message.answer("🎭 **Выбери сценарий для общения:**\n\nПрактикуй реальные жизненные ситуации!", reply_markup=get_tutor_roles_keyboard())

@router.callback_query(F.data.startswith("tutor_role:"))
async def start_tutor_chat(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    role_key = callback.data.split(":")[1]
    prompt = ROLES.get(role_key, ROLES["default"])
    
    await state.set_state(TutorState.chatting)
    await state.update_data(chat_history=[{"role": "system", "content": prompt}])
    
    names = {"default": "Сенсеем 🎓", "waiter": "Официантом 🍜", "tourist": "Туристом 🗺️", "hr": "HR-Менеджером 👔"}
    msg = f"🗣️ **Чат с {names[role_key]}**\n\nПиши текстом или отправляй **голосовые сообщения**!\n_(Скажи что-нибудь для начала)_"
    
    try: await callback.message.delete()
    except: pass
    await callback.message.answer(msg, reply_markup=get_tutor_exit_keyboard())

@router.message(TutorState.chatting, F.voice)
async def handle_tutor_voice(message: Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    file_io = io.BytesIO()
    await message.bot.download_file((await message.bot.get_file(message.voice.file_id)).file_path, destination=file_io)
    user_text = await transcribe_audio(file_io.getvalue())
    if not user_text.strip(): return await message.answer("Не расслышал 😔 Повтори!", reply_markup=get_tutor_exit_keyboard())
    await message.answer(f"🎙 _Вы сказали:_ {user_text}", parse_mode="Markdown")
    await process_llm_request(message, state, user_text)

@router.message(TutorState.chatting, F.text)
async def handle_tutor_message(message: Message, state: FSMContext):
    await process_llm_request(message, state, message.text)

async def process_llm_request(message: Message, state: FSMContext, user_text: str):
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    data = await state.get_data()
    history = data.get("chat_history", [])
    history.append({"role": "user", "content": user_text})
    try:
        bot_reply = await ask_groq_api(history)
    except RuntimeError as e:
        await message.answer(
            "ИИ-собеседник сейчас недоступен (проблема с API). "
            "Попробуй позже или напиши текстом без ИИ.",
            reply_markup=get_tutor_exit_keyboard(),
        )
        return
    except Exception:
        await message.answer("Собеседник отошел 😔", reply_markup=get_tutor_exit_keyboard())
        return

    history.append({"role": "assistant", "content": bot_reply})
    if len(history) > 11:
        history = [history[0]] + history[-10:]
    await state.update_data(chat_history=history)
    await message.answer(bot_reply, reply_markup=get_tutor_exit_keyboard())
