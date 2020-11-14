from telebot import types


def generate_markup(subjects):
    tmp_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for tmp_markup_btn in subjects:
        tmp_markup.add(tmp_markup_btn)
    return tmp_markup


teacher_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
teacher_markup.add(types.KeyboardButton('Задать работу'))
teacher_markup.add(types.KeyboardButton('Проверить работу'))
teacher_markup.add(types.KeyboardButton('/help'))
teacher_markup.add(types.KeyboardButton('/about'))
teacher_markup.add(types.KeyboardButton('/feedback'))


student_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
student_markup.add(types.KeyboardButton('Выполнить работу'))
student_markup.add(types.KeyboardButton('/help'))
student_markup.add(types.KeyboardButton('/about'))
student_markup.add(types.KeyboardButton('/feedback'))

none_markup = types.ReplyKeyboardRemove()
