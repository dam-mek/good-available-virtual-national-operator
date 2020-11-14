from os import environ
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import telebot
from flask import Flask, request

from stuff import markups, messages
from log import log
from GoogleSheet.GoogleSheet import GoogleSheet

# TODO
#  Логирование (logging)
#  sql базы данных

token = environ.get('TOKEN_GAVNO')
password = environ.get('PASSWORD_GAVNO')
server = Flask(__name__)
bot = telebot.TeleBot(token, parse_mode='markdown')
db = GoogleSheet()
params_for_questions = dict(
    subject=None,
    topic=None,
    classes=set()
)
classes_of_teacher = set()
subjects_of_teacher = set()


@bot.message_handler(commands=['start'])
def start_message(message):
    send_mail(message)
    log(message)
    bot.send_message(chat_id=message.chat.id, text=messages.START, reply_markup=markups.none_markup)
    msg = bot.send_message(chat_id=message.chat.id, text=messages.ENTER_PASSWORD, reply_markup=markups.none_markup)
    bot.register_next_step_handler(msg, authentication)


@bot.message_handler(commands=['help'])
def help_message(message):
    log(message)
    if db.is_teacher(message.chat.id):
        mp = markups.teacher_markup
    else:
        mp = markups.student_markup
    bot.send_message(chat_id=message.chat.id, text=messages.HELP, reply_markup=mp)


@bot.message_handler(commands=['about'])
def about_message(message):
    log(message)
    if db.is_teacher(message.chat.id):
        mp = markups.teacher_markup
    else:
        mp = markups.student_markup
    bot.send_message(chat_id=message.chat.id, text=messages.ABOUT, reply_markup=mp)


@bot.message_handler(commands=['feedback'])
def feedback_message(message):
    log(message)
    if db.is_teacher(message.chat.id):
        mp = markups.teacher_markup
    else:
        mp = markups.student_markup
    bot.send_message(chat_id=message.chat.id, text=messages.FEEDBACK, reply_markup=mp)


@bot.message_handler(content_types=['text'])
def dialogue(message):
    log(message)
    if db.is_student(message.chat.id):
        if message.text.lower() == 'выполнить работу':
            pass
    else:
        global subjects_of_teacher, classes_of_teacher, params_for_questions
        if message.text.lower() == 'задать работу':
            teacher = db.get_teacher_by_id(message.chat.id)
            subjects_of_teacher = set(teacher[3].split(';'))
            classes_of_teacher = set(teacher[4].split(';'))
            tmp_markup = markups.generate_markup(subjects_of_teacher)
            msg = bot.send_message(chat_id=message.chat.id, text=messages.ASK_SUBJECT, reply_markup=tmp_markup)
            bot.register_next_step_handler(msg, ask_topic)
        elif message.text.lower() == 'проверить работу':
            teacher = db.get_teacher_by_id(message.chat.id)
            subjects_of_teacher = set(teacher[3].split(';'))
            classes_of_teacher = set(teacher[4].split(';'))
            tmp_markup = markups.generate_markup(subjects_of_teacher)
            msg = bot.send_message(chat_id=message.chat.id, text=messages.ASK_SUBJECT, reply_markup=tmp_markup)
            bot.register_next_step_handler(msg, ask_topic)
    # help_message(message)


def ask_topic(message):
    global subjects_of_teacher, params_for_questions
    if message.text not in subjects_of_teacher:
        bot.send_message(chat_id=message.chat.id, text=messages.INCORRECT_ANSWER, reply_markup=markups.teacher_markup)
        return
    params_for_questions['subject'] = message.text
    msg = bot.send_message(chat_id=message.chat.id, text=messages.ASK_TOPIC, reply_markup=markups.none_markup)
    bot.register_next_step_handler(msg, ask_classes)


def ask_classes(message):
    global params_for_questions
    params_for_questions['topic'] = message.text
    tmp_markup = markups.generate_markup(classes_of_teacher)
    tmp_markup.add('Стоп')
    msg = bot.send_message(chat_id=message.chat.id, text=messages.ASK_CLASSES, reply_markup=tmp_markup)
    bot.register_next_step_handler(msg, get_class)


def get_class(message):
    global params_for_questions
    if message.text.lower() == 'стоп':
        print('stop', params_for_questions)
        msg = bot.send_message(chat_id=message.chat.id, text=messages.ASK_QUESTIONS, reply_markup=markups.none_markup)
        bot.register_next_step_handler(msg, ask_questions)
        return
    global classes_of_teacher
    if message.text not in classes_of_teacher:
        bot.send_message(chat_id=message.chat.id, text=messages.INCORRECT_ANSWER, reply_markup=markups.teacher_markup)
        return
    if params_for_questions['classes'] is None:
        params_for_questions['classes'] = set()
    params_for_questions['classes'].add(message.text)
    tmp_markup = markups.generate_markup(classes_of_teacher)
    tmp_markup.add('Стоп')
    msg = bot.send_message(chat_id=message.chat.id, text=messages.ASK_CLASS, reply_markup=tmp_markup)
    bot.register_next_step_handler(msg, get_class)


def ask_questions(message):
    if message.text.lower().replace('ш', 'щ') == 'помощь':
        msg = bot.send_message(chat_id=message.chat.id, text=messages.EXAMPLE_QUESTIONS,
                               reply_markup=markups.none_markup)
        bot.register_next_step_handler(msg, ask_questions)
        return
    bot.send_message(chat_id=message.chat.id, text='Всё сделано!')
    classes = params_for_questions['classes']
    db.create_question(teacher_id=message.chat.id,
                       subject=params_for_questions['subject'],
                       topic=params_for_questions['topic'],
                       classes=';'.join(classes),
                       questions=message.text)
    for class_ in classes:
        print(GoogleSheet.get_students_by_class(class_))
        for student_id in GoogleSheet.get_students_by_class(class_):
            bot.send_message(chat_id=student_id,
                             text=messages.QUESTIONS_TO_STUDENT.format(params_for_questions['subject'],
                                                                       params_for_questions['topic']),
                             reply_markup=markups.student_markup)


def authentication(message):
    success = GoogleSheet.authentication(message.chat.id, message.text)
    if not success:
        msg = bot.send_message(chat_id=message.chat.id, text=messages.CANT_AUTHENTICATION,
                               reply_markup=markups.none_markup)
        bot.register_next_step_handler(msg, authentication)
        return
    if db.is_teacher(message.chat.id):
        teacher = db.get_teacher_by_id(message.chat.id)
        second_name = teacher[0].capitalize()
        first_name = teacher[1].capitalize()
        third_name = teacher[2].capitalize()
        subjects = teacher[3].replace(';', ', ').lower()
        classes = teacher[4].replace(';', ', ').upper()
        message_text = messages.SUCCESS_AUTHENTICATION_TEACHER.format(
            second_name, first_name, third_name, subjects, classes
        )
        mp = markups.teacher_markup
    else:
        student = db.get_student_by_id(message.chat.id)
        second_name = student[0].capitalize()
        first_name = student[1].capitalize()
        third_name = student[2].capitalize()
        class_ = student[3].upper()
        message_text = messages.SUCCESS_AUTHENTICATION_STUDENT.format(
            second_name, first_name, third_name, class_
        )
        mp = markups.student_markup
    bot.send_message(chat_id=message.chat.id, text=message_text,
                     reply_markup=mp)


def send_mail(message):
    global password
    email = 'denisov_aa@gkl-kemerovo.ru'
    mail_account = smtplib.SMTP('smtp.gmail.com', 587)
    mail_account.starttls()
    mail_account.login(user=email, password=password)

    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = email
    msg['Subject'] = f'Logging. {message.from_user.username} {message.from_user.first_name} sent a message to the bot!'
    from log import create_log_str
    text_message = create_log_str(message)
    msg.attach(MIMEText(text_message, 'plain'))
    mail_account.send_message(from_addr=email, to_addrs=msg['To'], msg=msg)
    mail_account.quit()


@server.route('/' + token, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'Ну типа гавно запущен', 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://go-av-vi-na-op.herokuapp.com/' + token)
    return 'Ну типа гавно запущен, а я нужен для вебхука', 200


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(environ.get('PORT', 5000)))
