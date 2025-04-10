from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить задачу"),
            KeyboardButton(text="Удалить задачу")
        ],
        [
            KeyboardButton(text="Показать мои задачи")
        ]
    ],
    resize_keyboard=True
)

