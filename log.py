from time import gmtime


def log(message):
    print(create_log_str(message))


def create_log_str(message):
    date = message.date
    date = '{}.{}.{} {}:{}:{}'.format(str(gmtime(date).tm_mday).rjust(2, '0'), str(gmtime(date).tm_mon).rjust(2, '0'),
                                      str(gmtime(date).tm_year).rjust(2, '0'), str(gmtime(date).tm_hour).rjust(2, '0'),
                                      str(gmtime(date).tm_min).rjust(2, '0'), str(gmtime(date).tm_sec).rjust(2, '0'))

    log_str = 'message_id:{}|date:{}|used_id:{}|username:{}|first_name:{}|last_name:{}|text:{}'.format(
        message.message_id, date, message.from_user.id, message.from_user.username,
        message.from_user.first_name, message.from_user.last_name, message.text
    )
    return log_str
