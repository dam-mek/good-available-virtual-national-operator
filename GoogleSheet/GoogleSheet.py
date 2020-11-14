import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials
import hashlib
import gspread


class GoogleSheet:
    CREDENTIALS_FILE = 'mpython-295405-e9a0e35c1fdd.json'  # Имя файла с закрытым ключом, вы должны подставить свое
    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE,
                                                                   ['https://www.googleapis.com/auth/spreadsheets',
                                                                    'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())  # Авторизуемся в системе
    service = discovery.build('sheets', 'v4', http=httpAuth)  # Выбираем работу с таблицами и 4 версию API
    spreadsheetId = '1RRSmIGRu0vwqZ5AIz8lS8s-H3EY7oD-Znv0mHy_bfSo'

    @staticmethod
    def authentication(user_id, password):
        salt = b'5n\x06\x15\xeb9eF\xc8\xf6\x87\xcb4p\x9b\xe5\xb6\xa7\xb1Q\xbb\xe3\xa1\xae!\xd2r]B\xd6\x1a\xb8'
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('mpython-295405-e9a0e35c1fdd.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('School').sheet1
        j = 1
        T = False
        for i in (sheet.col_values(5)):
            # print(i)
            if str(i) == str(key):
                sheet.update_cell(j, 1, user_id)
                sheet.update_cell(j, 7, 'True')
                T = True

            j += 1
        if T != True:
            j = 1
            sheet = client.open('School').get_worksheet(1)
            for i in (sheet.col_values(5)):
                # print(i)
                if str(i) == str(key):
                    sheet.update_cell(j, 1, user_id)
                    sheet.update_cell(j, 8, 'True')
                    T = True
                j += 1
        return T

    def create_question(self, teacher_id, subject, topic, classes, questions):
        ranges = ['Лист номер один!A1:A1']
        results = self.service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheetId,
                                                                ranges=ranges,
                                                                valueRenderOption='FORMATTED_VALUE',
                                                                dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        n = int(sheet_values[0][0]) % 10000
        if n == 0 or n == 1:
            n = 2
        que_list = questions.replace('\n', '').split(';')
        # print(que_list)
        for i in range(len(que_list)):
            que_list[i] = tuple(que_list[i].split('? '))
        # print(que_list)
        ans_list = []
        que_list1 = []
        for i in range(len(que_list)):
            que_list1.append(que_list[i][0])
            ans_list.append(que_list[i][1])
            # if que_list[i][1]==':::':
            #     results = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheetId, body={
            #         "valueInputOption": "USER_ENTERED",
            #         # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            #
            #         "data": [
            #             {"range": f"Лист номер один!A{i + 1}:F{a}",
            #              "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
            #              "values": [
            #                  [i + 1, tid, que_list[i][0], 'Свобдный ответ'],  # Заполняем первую строку
            #              ]}
            #         ]
            #     }).execute()
            # else:
        results = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheetId, body={
            "valueInputOption": "USER_ENTERED",
            # Данные воспринимаются, как вводимые пользователем (считается значение формул)

            "data": [
                {"range": f"Лист номер один!A{n}:K{n}",
                 "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                 "values": [
                     [n - 1, teacher_id, subject, topic, classes, (';').join(que_list1), (';').join(ans_list), False],
                     # Заполняем первую строку
                 ]}
            ]
        }).execute()
        results = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheetId, body={
            "valueInputOption": "USER_ENTERED",
            # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            "data": [
                {"range": f"Ответы!A1:A1",
                 "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                 "values": [
                     [n + 1]  # Заполняем первую строку
                 ]}
            ]
        }).execute()

    def create_attempt(self, student_id, subject, topic, answer):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('mpython-295405-e9a0e35c1fdd.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('School').get_worksheet(0)
        cl = ''
        j = 0
        for i in sheet.col_values(1):
            if str(i) == str(id):
                cl = str(sheet.row_values(j + 1)[5])
                break
            j += 1
        sheet = client.open('School').get_worksheet(1)
        j = 0
        tgid = 0
        for i in sheet.col_values(6):
            b = sheet.col_values(6)[j].split(';')
            for h in range(len(b)):
                if str(b[h]) == subject:
                    c = sheet.row_values(j + 1)[6].split(';')
                    for k in range(len(c)):
                        if str(c[k]) == str(cl):
                            tgid = sheet.row_values(j + 1)[0]
                            break
            j += 1

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('mpython-295405-e9a0e35c1fdd.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Вопросы').get_worksheet(0)
        h = 0
        qid = 0
        for i in sheet.col_values(2):
            if str(i) == str(tgid):
                b = sheet.row_values(h + 1)[4].split(';')
                for p in range(len(b)):
                    if str(sheet.row_values(h + 1)[2]) == str(subject) and str(sheet.row_values(h + 1)[3]) == str(
                            topic) and \
                            str(b[p]) == str(cl):
                        qid = sheet.row_values(h + 1)[0]
                        print(qid)
                        break
            h += 1

        ranges = ['Ответы!A1:A1']
        results = self.service.spreadsheets().values().batchGet(spreadsheetId=self.spreadsheetId,
                                                                ranges=ranges,
                                                                valueRenderOption='FORMATTED_VALUE',
                                                                dateTimeRenderOption='FORMATTED_STRING').execute()
        sheet_values = results['valueRanges'][0]['values']
        n = int(sheet_values[0][0]) % 10000
        if n == 0 or n == 1:
            n = 2
        results = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheetId, body={
            "valueInputOption": "USER_ENTERED",
            # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            "data": [
                {"range": f"Ответы!A{n}:CV{n}",
                 "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                 "values": [
                     [qid, id, ';'.join(answer)],  # Заполняем первую строку
                 ]}
            ]
        }).execute()
        results = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheetId, body={
            "valueInputOption": "USER_ENTERED",
            # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            "data": [
                {"range": f"Ответы!A1:A1",
                 "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                 "values": [
                     [n + 1]  # Заполняем первую строку
                 ]}
            ]
        }).execute()

    def check(self, teacher_id, subject, topic, class_):
        a = []
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('mpython-295405-e9a0e35c1fdd.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Вопросы').get_worksheet(0)
        sheett = client.open('Вопросы').get_worksheet(1)
        h = 0
        for i in sheet.col_values(2):
            if str(i) == str(teacher_id):
                if sheet.row_values(h + 1)[2] == str(subject) and sheet.row_values(h + 1)[3] == str(topic) and \
                        sheet.row_values(h + 1)[4] == str(class_):
                    id = sheet.row_values(h + 1)[0]
                    break
            h += 1
        results = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.spreadsheetId, body={
            "valueInputOption": "USER_ENTERED",
            # Данные воспринимаются, как вводимые пользователем (считается значение формул)
            "data": [
                {"range": f"Лист номер один!H{h + 1}:H{h + 1}",
                 "majorDimension": "ROWS",  # Сначала заполнять строки, затем столбцы
                 "values": [
                     [True]  # Заполняем первую строку
                 ]}
            ]
        }).execute()
        h = 0
        for i in sheett.col_values(1):
            if str(id) == str(i):
                b = [sheett.row_values(h + 1)[1], sheett.row_values(h + 1)[2]]
                a.append(b)
            h += 1
        return id, a

    def get_questions_by_teacher_id(self, teacher_id):
        a=[]
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('mpython-295405-e9a0e35c1fdd.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('Вопросы').get_worksheet(0)
        j=0
        for i in sheet.col_values(2):
            if str(i)==str(teacher_id) and sheet.row_values(j+1)[7]==False:
                b=[sheet.row_values(j+1)[2],sheet.row_values(j+1)[3],sheet.row_values(j+1)[4]]
                a.append(b)
            j+=1
        return a

    @staticmethod
    def get_students_by_class(class_):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('mpython-295405-e9a0e35c1fdd.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('School').sheet1
        a = []
        b = sheet.col_values(1)
        j = 0
        for i in (sheet.col_values(6)):
            if str(i) == class_:
                a.append(str(b[j]))
            j += 1
        return class_, a

    def get_student_by_id(self, student_id):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('mpython-295405-e9a0e35c1fdd.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('School').sheet1
        a = [0, 0, 0, 0]
        b = sheet.col_values(1)
        j = 0
        for i in b:
            if str(i) == str(student_id):
                a[0], a[1], a[2], a[3] = sheet.row_values(2)[1], sheet.row_values(2)[2], sheet.row_values(2)[3], \
                                         sheet.row_values(2)[5]
                break
            j += 1
        if a[0] == 0:
            return None
        else:
            return a

    def get_teacher_by_id(self, teacher_id):

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('mpython-295405-e9a0e35c1fdd.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open('School').get_worksheet(1)
        a = [0, 0, 0, 0, 0]
        b = sheet.col_values(1)
        j = 0
        for i in b:
            if str(i) == str(teacher_id):
                a[0], a[1], a[2], a[3], a[4] = sheet.row_values(2)[1], sheet.row_values(2)[2], sheet.row_values(2)[3], \
                                               sheet.row_values(2)[5], sheet.row_values(2)[6]
                break
            j += 1
        if a[0] == 0:
            return None
        else:
            return a

    def is_teacher(self, user_id):
        return self.get_teacher_by_id(user_id) is not None

    def is_student(self, user_id):
        return self.get_student_by_id(user_id) is not None
