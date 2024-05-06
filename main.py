# Importing required libraries
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove

import database

bot = Bot(token='TOKEN HERE')

cache: dict[int, dict] = dict()
storage = MemoryStorage()


class States(StatesGroup):
    like_name = State()
    set_name = State()
    set_reminder = State()


class Task(StatesGroup):
    set_description = State()
    set_deadline = State()
    name = State()
    set_priority = State()


# Initializing the dispatcher object
dp = Dispatcher(storage=storage)

# Defining and adding buttons
YES = KeyboardButton(text="YES")
NO = KeyboardButton(text="NO")

replay_keyboard = ReplyKeyboardMarkup(keyboard=[[YES, NO]],
                                      resize_keyboard=True, one_time_keyboard=True)

p = [[InlineKeyboardButton(text="Fateful", callback_data="P/Fateful"),
      InlineKeyboardButton(text="Super", callback_data="P/Super")],
     [InlineKeyboardButton(text="Routine", callback_data="P/Routine"),
      InlineKeyboardButton(text="Side", callback_data="P/Side")],
     [InlineKeyboardButton(text='Go Back', callback_data='to_add')]]

MONDAY_OFF = InlineKeyboardButton(text="Monday ❌", callback_data="D/1/OFF")  # First day of ISO 8601
TUESDAY_OFF = InlineKeyboardButton(text="Tuesday ❌", callback_data="D/2/OFF")
WEDNESDAY_OFF = InlineKeyboardButton(text="Wednesday ❌", callback_data="D/3/OFF")
THURSDAY_OFF = InlineKeyboardButton(text="Thursday ❌", callback_data="D/4/OFF")
FRIDAY_OFF = InlineKeyboardButton(text="Friday ❌", callback_data="D/5/OFF")
SATURDAY_OFF = InlineKeyboardButton(text="Saturday ❌", callback_data="D/6/OFF")
SUNDAY_OFF = InlineKeyboardButton(text="Sunday ❌", callback_data="D/7/OFF")
MONDAY = InlineKeyboardButton(text="Monday ✅", callback_data="D/1")  # First day of ISO 8601
TUESDAY = InlineKeyboardButton(text="Tuesday ✅", callback_data="D/2")
WEDNESDAY = InlineKeyboardButton(text="Wednesday ✅", callback_data="D/3")
THURSDAY = InlineKeyboardButton(text="Thursday ✅", callback_data="D/4")
FRIDAY = InlineKeyboardButton(text="Friday ✅", callback_data="D/5")
SATURDAY = InlineKeyboardButton(text="Saturday ✅", callback_data="D/6")
SUNDAY = InlineKeyboardButton(text="Sunday ✅", callback_data="D/7")
CONFIRM = InlineKeyboardButton(text="Confirm", callback_data="D/OK")
PREVIOUS = InlineKeyboardButton(text="Confirm", callback_data="D/PREVIOUS")

ALL_DAYS = {1: [MONDAY_OFF, MONDAY], 2: [TUESDAY_OFF, TUESDAY],
            3: [WEDNESDAY_OFF, WEDNESDAY], 4: [THURSDAY_OFF, THURSDAY],
            5: [FRIDAY_OFF, FRIDAY], 6: [SATURDAY_OFF, SATURDAY], 7: [SUNDAY_OFF, SUNDAY]}

WEEK_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[MONDAY],
                                                    [TUESDAY],
                                                    [WEDNESDAY],
                                                    [THURSDAY],
                                                    [FRIDAY],
                                                    [SATURDAY],
                                                    [SUNDAY],
                                                    [PREVIOUS, CONFIRM]])

DAILY_BTN = InlineKeyboardButton(text='Daily Task', callback_data="deadline_daily")
MORNING_BTN = InlineKeyboardButton(text='Morning', callback_data="morning_reminder")
AFTERNOON_BTN = InlineKeyboardButton(text='Afternoon', callback_data="afternoon_reminder")
EVENING_BTN = InlineKeyboardButton(text='Evening', callback_data="evening_reminder")

PRIORITY_MARKUP = InlineKeyboardMarkup(inline_keyboard=p)
DEADLINE_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[DAILY_BTN,
                                                         InlineKeyboardButton(text='Previous',
                                                                              callback_data="to_priority")
                                                         ]])
REMINDER_MARKUP = InlineKeyboardMarkup(inline_keyboard=[[MORNING_BTN, AFTERNOON_BTN, EVENING_BTN]])

SKIP_BTN = InlineKeyboardButton(text="Skip", callback_data="description_skip")
PREVIOUS_BTN = InlineKeyboardButton(text="Previous", callback_data="to_deadline")
DESCRIPTION_MARKUP = InlineKeyboardMarkup(
    inline_keyboard=[[SKIP_BTN],
                     [PREVIOUS_BTN]])


# Message handler for the /button1 command
def check_valid_date(entered_date):
    date_parts = entered_date.split(":")

    if len(date_parts) != 2:
        return False

    hours = date_parts[0]
    minutes = date_parts[1]

    if not hours.isdigit() or not minutes.isdigit():
        return False

    if int(minutes) > 59:
        return False

    return True


# T

@dp.message(CommandStart())
async def check(message: types.Message, state: FSMContext):
    database.add_user(message.from_user.id, message.from_user.first_name, message.from_user.username,
                      message.date)
    await message.answer('Hello 👋')
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(0.5)
    await message.answer(f'Should I call you {message.from_user.first_name}?',
                         reply_markup=replay_keyboard)
    await state.set_state(States.like_name)


async def reminder_handler(message: types.Message, state: FSMContext):
    await message.answer("Wanna set a daily reminder?", replay_keyboard=replay_keyboard)
    await state.set_state(States.set_reminder)


async def final_reminder(message: types.Message, state: FSMContext):
    await message.answer('All set!', reply_markup=ReplyKeyboardRemove())
    await message.answer('You can set a reminder anytime with /reminder command!',
                         reply_markup=ReplyKeyboardRemove())
    await state.clear()


@dp.message(States.set_reminder)
async def set_reminder_handler(message: types.Message, state: FSMContext):
    if message.text.lower() == "no":
        await final_reminder(message, state)
    elif message.text.lower() == 'yes':
        await message.answer("When do you want to be reminded?",
                             reply_markup=REMINDER_MARKUP)


@dp.message(States.like_name)
async def like_name_handler(message: types.Message, state: FSMContext):
    if message.text.lower() == "no":
        await message.answer('Then what should I call you?', reply_markup=ReplyKeyboardRemove())
        await state.set_state(States.set_name)
    elif message.text.lower() == 'yes':
        await message.answer("Bingo!", reply_markup=ReplyKeyboardRemove())
        await message.answer("You can always change your name by using /name [newname] command")
        await reminder_handler(message, state)

    else:
        await message.answer("Please answer with yes or no")
        return


@dp.message(Command("priority"))
async def reminder_command_handler(message: types.Message, state: FSMContext):
    await message.answer("Under maintenance 🛠️.")


@dp.message(Command("reminder"))
async def reminder_command_handler(message: types.Message, state: FSMContext):
    await message.answer("Under maintenance 🛠️.")


@dp.message(States.set_name)
async def set_name_handler(message: types.Message, state: FSMContext):
    database.update_user_name(message.from_user.id, message.text)
    await message.answer(f'All set {database.get_name(message.from_user.id)}!', reply_markup=ReplyKeyboardRemove())
    await message.answer("You can always change your name by using /name [newname] command")
    await message.answer("Use /add to add a new task!")
    await reminder_handler(message, state)


@dp.message(Command("name"))
async def get_set_name(message: types.Message, state: FSMContext):
    msg = message.text.split()
    if len(msg) > 1:
        database.update_user_name(message.from_user.id, ' '.join(msg[1:]))
    await message.answer(f"Your name is {database.get_name(message.from_user.id)}")


@dp.message(Command("add"))
async def add_task(message: types.Message, state: FSMContext):
    x = await message.answer("What is the name of the task?")
    cache[message.from_user.id] = {}
    await state.set_state(Task.name)
    await state.set_data({"id": x.message_id})


@dp.message(Task.name)
async def set_task_name(message: types.Message, state: FSMContext, delete=False):
    data = await state.get_data()
    if delete:
        await message.bot.edit_message_text(text="<s>What is the name of the task?</s>",
                                            chat_id=message.chat.id,
                                            parse_mode=ParseMode.HTML,
                                            message_id=data['id'])
    cache[message.from_user.id]['name'] = message.text
    await message.answer("What is the priority of the task?",
                         reply_markup=PRIORITY_MARKUP)
    await state.update_data({"name": message.text})
    await state.set_state(Task.set_priority)


@dp.message(Task.set_deadline)
async def set_deadline(message: types.Message, state: FSMContext, *, daily=False, user=None):
    if daily:
        await message.answer("Daily deadline has been set!")
        deadline = "24:00"
    elif check_valid_date(message.text):
        data = await state.get_data()
        await message.bot.edit_message_text(text="<s>Type deadline in HH:MM format</s>",
                                            chat_id=message.chat.id,
                                            parse_mode=ParseMode.HTML,
                                            message_id=data['id'])
        await message.answer("Deadline has been set!")
        deadline = message.text
        user = message.from_user.id
    else:
        await message.answer("Please enter a valid deadline")
        return
    await message.answer("Add a description (Optional)", reply_markup=DESCRIPTION_MARKUP)
    cache[user]['deadline'] = deadline
    cache[user]['daily'] = daily
    await state.clear()
    if daily:
        cache[user]['days'] = {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True}
        await message.answer("Uncheck the off days", reply_markup=WEEK_MARKUP)
    else:
        await state.set_state(Task.set_description)


@dp.message(Command("list"))
async def list_tasks(message: types.Message, state: FSMContext):
    data = database.get_tasks(message.from_user.id)
    result = ""
    for i in data:
        for j in i:
            result += str(j) + " "
        result += "\n"
    await message.answer(result)


@dp.message(Task.set_description)
async def set_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    desc = None
    if data.get('call'):
        pre = InlineKeyboardButton(text="Skip", callback_data="null")
        await message.bot.edit_message_text(text=f"<s>Add a description (Optional)</s>",
                                            parse_mode=ParseMode.HTML,
                                            chat_id=message.chat.id,
                                            message_id=data.get('id') or message.message_id - 1,
                                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[pre]])
                                            )
    else:
        await message.bot.edit_message_text(text=f"<s>Add a description (Optional)</s>\n<pre>{message.text}</pre>",
                                            parse_mode=ParseMode.HTML,
                                            chat_id=message.chat.id,
                                            message_id=message.message_id - 1)
        desc = message.text
    data = await state.get_data()
    user = cache.get(message.from_user.id)
    if user is None:
        await message.answer("An error encountered! Please contact @immustafakareem.\nCode :- 1")
    x = database.add_task(message.from_user.id, user.get('name'), datetime.utcnow(), user.get('deadline'),
                          user.get('priority'), None, desc,
                          str(message.date.astimezone().tzinfo), daily=user.get('daily'))
    await message.answer(str(x), reply_markup=ReplyKeyboardRemove())
    cache[message.from_user.id].clear()
    del user
    await state.clear()


def set_reminder(date):
    pass


@dp.callback_query()
async def check_button(call: types.CallbackQuery, state: FSMContext):
    # Checking which button is pressed and respond accordingly
    match call.data:
        case 'to_add':
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Go Back", callback_data="null")
            ]])
            await call.bot.edit_message_text(text="<s>What is the priority of the task?</s>",
                                             message_id=call.message.message_id,
                                             chat_id=call.message.chat.id,
                                             reply_markup=markup,
                                             parse_mode=ParseMode.HTML)
            await add_task(call.message, state)
        case "to_priority":
            await set_task_name(call.message, state)
        case "morning_reminder":
            markup = InlineKeyboardMarkup(inline_keyboard=[[MORNING_BTN]])
            set_reminder("10:00")
            await call.bot.edit_message_reply_markup(
                reply_markup=markup,
                message_id=call.message.message_id,
                chat_id=call.message.chat.id
            )
            await final_reminder(call.message, state)
        case "afternoon_reminder":
            markup = InlineKeyboardMarkup(inline_keyboard=[[AFTERNOON_BTN]])
            set_reminder("16:00")
            await call.bot.edit_message_reply_markup(
                reply_markup=markup,
                message_id=call.message.message_id,
                chat_id=call.message.chat.id
            )
            await final_reminder(call.message, state)
        case "evening_reminder":
            markup = InlineKeyboardMarkup(inline_keyboard=[[EVENING_BTN]])
            set_reminder("22:00")
            await call.bot.edit_message_reply_markup(
                reply_markup=markup,
                message_id=call.message.message_id,
                chat_id=call.message.chat.id
            )
            await final_reminder(call.message, state)
        case "deadline_daily":
            await state.set_data({'id': call.message.message_id, 'call': True})
            markup = InlineKeyboardMarkup(inline_keyboard=[[DAILY_BTN]])
            await call.bot.edit_message_text(text="<s>Type deadline in HH:MM format</s>",
                                             message_id=call.message.message_id,
                                             chat_id=call.message.chat.id,
                                             reply_markup=markup,
                                             parse_mode=ParseMode.HTML)
            await set_deadline(call.message, state, daily=True, user=call.from_user.id)
            return
        case "description_skip":
            await state.set_data({'id': call.message.message_id, 'call': True})
            await set_description(call.message, state)
    if call.data.startswith("P/"):
        priority_title = call.data.removeprefix("P/")
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=priority_title, callback_data="null")
        ]])
        title = "<s>What is the priority of the task?</s>"
        await state.update_data({'priority': priority_title})
        cache[call.from_user.id]['priority'] = priority_title
    elif call.data == "to_deadline":
        pre = InlineKeyboardButton(text="Previous", callback_data="null")
        markup = InlineKeyboardMarkup(inline_keyboard=[[pre]])
        title = "<s>Add a description (Optional)</s>"
    if call.data.startswith("D/"):
        i = 1 if call.data.endswith("/OFF") else 0
        num = int(call.data.split("/")[1])
        days = cache[call.from_user.id].get('days')
        if days is None:
            await call.message.answer("An error encountered. Please contact @immustafakareem\n Error code :- 2")
            return
        inline = [[ALL_DAYS[k][v] if k != num else ALL_DAYS[k][i]]
                  for k, v in days.items()]
        inline.append([PREVIOUS, CONFIRM])
        markup = InlineKeyboardMarkup(inline_keyboard=inline)
        cache[call.from_user.id]['days'][num] = i
        await call.bot.edit_message_reply_markup(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            reply_markup=markup)
    if call.data.startswith("P/") or call.data == 'to_deadline':
        await call.bot.edit_message_text(text=title,
                                         message_id=call.message.message_id,
                                         chat_id=call.message.chat.id,
                                         reply_markup=markup,
                                         parse_mode=ParseMode.HTML)
        dead = await call.message.answer("Type deadline in HH:MM format",
                                         reply_markup=DEADLINE_MARKUP)
        await state.clear()

        await state.set_state(Task.set_deadline)
        await state.set_data({'id': dead.message_id})

    await call.answer()


# Start the bot
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
