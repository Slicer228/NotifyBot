from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from src.routers.states import GeneratedTask, DeclineChanges


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


week_days_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text="Понедельник",
        callback_data=GeneratedTask(
            week_day=0
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Вторник",
        callback_data=GeneratedTask(
            week_day=1
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Среда",
        callback_data=GeneratedTask(
            week_day=2
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Четверг",
        callback_data=GeneratedTask(
            week_day=3
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Пятница",
        callback_data=GeneratedTask(
            week_day=4
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Суббота",
        callback_data=GeneratedTask(
            week_day=5
        ).pack()
    )],
    [InlineKeyboardButton(
        text="Воскресенье",
        callback_data=GeneratedTask(
            week_day=6
        ).pack()
    )],
    [InlineKeyboardButton(
        text="ОТМЕНА",
        callback_data=DeclineChanges().pack()
    )],
])


def get_hours_kb(proceed_task: GeneratedTask):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=str(i),
                    callback_data=GeneratedTask(
                        week_day=proceed_task.week_day,
                        hour=i
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=str(i+1),
                    callback_data=GeneratedTask(
                        week_day=proceed_task.week_day,
                        hour=i+1
                    ).pack()
                ),
            ]
            for i in range(0, 24, 2)
        ]
    )


def get_minutes_kb(proceed_task: GeneratedTask):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=str(i),
                    callback_data=GeneratedTask(
                        week_day=proceed_task.week_day,
                        hour=proceed_task.hour,
                        minute=i
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=str(i+1),
                    callback_data=GeneratedTask(
                        week_day=proceed_task.week_day,
                        hour=proceed_task.hour,
                        minute=i+1
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=str(i+2),
                    callback_data=GeneratedTask(
                        week_day=proceed_task.week_day,
                        hour=proceed_task.hour,
                        minute=i+2
                    ).pack()
                ),
            ]
            for i in range(0, 59, 3)
        ]
    )


def get_is_one_time_kb(proceed_task: GeneratedTask):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да",
                    callback_data=GeneratedTask(
                        week_day=proceed_task.week_day,
                        hour=proceed_task.hour,
                        minute=proceed_task.minute,
                        is_one_time=True
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="Нет",
                    callback_data=GeneratedTask(
                        week_day=proceed_task.week_day,
                        hour=proceed_task.hour,
                        minute=proceed_task.minute,
                        is_one_time=False
                    ).pack()
                )
            ]
        ]
    )

