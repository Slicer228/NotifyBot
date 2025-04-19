from typing import List
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from src.routers.states import GeneratedTask, DeclineChanges, ToDeleteTask, StartDeleteTask, StartAddTask, ShowTasks
from src.validator import Task


main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Добавить задачу", callback_data=StartAddTask().pack()),
            InlineKeyboardButton(text="Удалить задачу", callback_data=StartDeleteTask().pack())
        ],
        [
            InlineKeyboardButton(text="Показать мои задачи", callback_data=ShowTasks().pack())
        ]
    ]
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
    kb = [
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
    kb.append([InlineKeyboardButton(
        text="ОТМЕНА",
        callback_data=DeclineChanges().pack()
    )])
    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )


def get_minutes_kb(proceed_task: GeneratedTask):
    kb = [
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
    kb.append([InlineKeyboardButton(
        text="ОТМЕНА",
        callback_data=DeclineChanges().pack()
    )])
    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )


def get_is_one_time_kb(proceed_task: GeneratedTask):
    kb = [
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
    kb.append([InlineKeyboardButton(
        text="ОТМЕНА",
        callback_data=DeclineChanges().pack()
    )])
    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )


def get_decide_cb(task_to_delete: ToDeleteTask):
    kb = [
            [
                InlineKeyboardButton(
                    text="Да",
                    callback_data=ToDeleteTask(
                        task_id=task_to_delete.task_id,
                        decided=True
                    ).pack()
                ),
                InlineKeyboardButton(
                    text="Нет",
                    callback_data=ToDeleteTask(
                        task_id=task_to_delete.task_id,
                        decided=False
                    ).pack()
                )
            ]
        ]
    return InlineKeyboardMarkup(
        inline_keyboard=kb
    )


def get_tasks_to_delete_kb(tasks: List[Task]):
    if len(tasks) == 1:
        kb = [
            [
                InlineKeyboardButton(
                    text=str(tasks[0].task_id),
                    callback_data=ToDeleteTask(
                        task_id=tasks[0].task_id
                    ).pack()
                )
            ]
        ]
        kb.append([InlineKeyboardButton(
            text="В главное меню",
            callback_data=DeclineChanges().pack()
        )])
        return InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    elif len(tasks) == 2:
        kb = [
            [
                InlineKeyboardButton(
                    text=str(tasks[i].task_id),
                    callback_data=ToDeleteTask(
                        task_id=tasks[i].task_id
                    ).pack()
                ),
                InlineKeyboardButton(
                    text=str(tasks[i + 1].task_id),
                    callback_data=ToDeleteTask(
                        task_id=tasks[i + 1].task_id
                    ).pack()
                )
            ]
            for i in range(0, len(tasks) - 1, 3)
        ]
        kb.append([InlineKeyboardButton(
            text="В главное меню",
            callback_data=DeclineChanges().pack()
        )])
        return InlineKeyboardMarkup(
            inline_keyboard=kb
        )
    else:
        kb = [
                [
                    InlineKeyboardButton(
                        text=str(tasks[i].task_id),
                        callback_data=ToDeleteTask(
                            task_id=tasks[i].task_id
                        ).pack()
                    ),
                    InlineKeyboardButton(
                        text=str(tasks[i + 1].task_id),
                        callback_data=ToDeleteTask(
                            task_id=tasks[i + 1].task_id
                        ).pack()
                    ),
                    InlineKeyboardButton(
                        text=str(tasks[i + 2].task_id),
                        callback_data=ToDeleteTask(
                            task_id=tasks[i + 2].task_id
                        ).pack()
                    ),
                ]
                for i in range(0, len(tasks) - 1, 3)
            ]
        kb.append([InlineKeyboardButton(
            text="В главное меню",
            callback_data=DeclineChanges().pack()
        )])
        return InlineKeyboardMarkup(
            inline_keyboard=kb
        )

