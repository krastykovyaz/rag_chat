import datetime, time, random
from message_sendler import send_message
from work_calendar_ru import WCR
# from chatgpt.gptchat import OpenAI
import os
from collections import defaultdict
import telebot
from send_standup import send_reminder
from texts_suggests import standup

STICKERS_NEW_YEAR = ['CAACAgIAAxkBAAEDlkVhzcb8GNEYxh8ZJcm_iDAgWtRgCAACpAQAApb6EgUslWmzb-3ETiME',\
            'CAACAgIAAxkBAAEDlkdhzccc1U0RwLpw4job3WyCs7uSQgACyAQAApb6EgXirWb6Dapc0yME',\
            'CAACAgIAAxkBAAEDlklhzcc8RkPlL0gJtu-cgmCkajT9JAACygQAApb6EgUt3h-ceZw05yME',\
            'CAACAgIAAxkBAAEDlkthzcdew3anO01pI7vCdsegM_ZKwwACqQQAAs7Y6AtETjLpOtjSCCME',\
            'CAACAgIAAxkBAAEDlk1hzcfC4KQoMoHqSGvy4kI_s911jwACrAQAAs7Y6Avkoz17hGsOVSME',\
            'CAACAgIAAxkBAAEDlk9hzchDWjVRCiTkN3KHy0hd7mFtZAACjAQAAs7Y6As0kEOE9Bh5myME'
            ]

STICKERS_TIME = [
                 'CAACAgIAAxkBAAED7LdiCfn60bU0Q9pdfBGESlP7k7E1IwACZgADTlzSKbUUiSuZ-b7XIwQ',\
                 'CAACAgIAAxkBAAED7LliCfoPbGqEyVQ1WKyEV7KnHDeI_wACWwADWbv8JWRSp1P6Y54eIwQ',\
                 'CAACAgIAAxkBAAED7LtiCfoYznTGfU5jca24JY4pZDbBdwACLQADeKjmDxjLcTxHMM54IwQ',\
                 'CAACAgIAAxkBAAED7L1iCfogU5a3vVAfyl7xNtkBfPt9JwACIwADKA9qFCdRJeeMIKQGIwQ',\
                 'CAACAgIAAxkBAAED7L9iCfoomW0EPlE',\
                 'Ih4JsmJG1kWxKeQACOQEAAjDUnRGZPKIpL_aL9iME',\
                 'CAACAgIAAxkBAAED7MFiCfo7O8Qb_C217ofnKsOnr_6ZUQACTgADWbv8JQ3rz9n50HgqIwQ', \
                'CAACAgIAAxkBAAEDuCph6Qh5hEo0Bx6INO90x65SWNzcqwAC-REAAmtjoUjsJL37UK4g4yME',\
             'CAACAgEAAxkBAAEDuCxh6QkL3fprrJuzEVmNq1VvZK1oCwAC7QEAAjgOghE8J4BsgBeaAyME',\
             'CAACAgIAAxkBAAEDuC5h6QmIGqedJ5TDiZKxPegKrIowUAACJgADTlzSKWVquOx29oWbIwQ',\
            'CAACAgIAAxkBAAEDuDBh6QmsN9wM2cMXYI1ArnDOiEankQACIgADr8ZRGtYR9zsFvVVnIwQ',\
                 'CAACAgIAAxkBAAEDuDJh6QoXbBettI-55rDSF1h5av_guQACVwADQbVWDMRcizSSWwQYIwQ',\
                 ]

STICKERS_IVR = [
                 'CAACAgIAAxkBAAEFFcZisG46_Agk4gjLphLN75xvr5J5FAACZxkAAsjh6Eqk3V7qRd9C9igE',\
                 'CAACAgIAAxkBAAEFFchisG5BKO2HwraqEdVHJFq03IziEAAC8BkAAjf_IEiMbpW8utbtASgE',\
                 'CAACAgIAAxkBAAEFFcxisG5JzIM0zmTIM0eW7m0yfrKAIQACnhcAArblIUhrm29XzPX-digE'
                 ]
STICKERS_BIRHTDAY = ['CAACAgIAAxkBAAEDrzxh4bnubNCgFXfsLRkDTrkK5xPeNwACxw4AAnma-EtauQrkjzoi_yME']


def is_user_none(message):
    text = 'Придумай, пожалуйста, никнейм/Username. Укажи в настройках аккаунта. Так мы сможем идентифицировать пользоватей и сделать наш сервис лучше !'
    if type(message.chat.username) != str:
        send_message(chat_id=message.chat.id, text=text)
        time.sleep(1)


def isclient(message):
    is_user_none(message)
    with open(r'/Users/19028558/Desktop/NLP2.0/intent_recognizer_test/gosha_folder/id_chat_list.txt', 'r', encoding='utf-8') as txtf:
        for line in txtf:
            if str(message.chat.id) in line:
                return True
    return False

def save_user(message):
    file = open(r'/Users/19028558/Desktop/NLP2.0/intent_recognizer_test/gosha_folder/id_chat_list.txt', 'a',
                encoding='utf-8')
    file.write(f'{message.chat.id}|{message.chat.username}|o\n')
    file.close()

def log_reversed(file, path, bot):
    list_lines = file.readlines()
    reversed_file = [str(l) for l in [list_lines[0]] + list_lines[::-1][:-1]]
    with open(path, 'w') as f:
        f.write('\n'.join(reversed_file) + '\n')
    f = open(path, 'rb')
    bot.send_document(93027469, f)
    # os.replace(path)


def thread_function():
    # oai = OpenAI()
    wcr = WCR(start_hour=6, start_minutes=0, end_hour=22, end_minutes=0)
    # text_standup_ivr = f"Короткое приглашение на эджайл standup https://jazz.sberbank.ru/sber-44dwzz?psw=OAZSVhMcABgfFlVATAgXCxAcSA"
    text_standup_bot = f"У нас стендап: https://jazz.sberbank.ru/sber-44dwzz?psw=OAZSVhMcABgfFlVATAgXCxAcSA "
    # wishes = f"{oai.request_chat('Короткое поздравление с Днем рождения!')}💐 \nГоша🫶🏽"
    text_mail_ivr = f"Напоминание про письмо на группу сопровождения для начала тестирования"
    text_1  = f"Я все !"
    user_list_o, user_list_m = [], []
    # with open(r'/Users/19028558/Desktop/NLP2.0/intent_recognizer_test/gosha_folder/id_chat_list.txt', 'r') as txtf:
    #     for line in txtf:
    #         is_region = line.split('|')[-1].strip()
    #         user_list_o.append(line.split('|')[0].strip()) \
    #             if is_region == 'o' else user_list_m.append(line.split('|')[0].strip())
    # print('START', '------------------------------================')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    i = 20
    while True:
        f = False
        if datetime.datetime.now().strftime("%Y-%m-%d %H:%M") == f"2022-02-09 10:{i}":
            # for user in user_list_o:
            user = 93027469
            # bot.send_sticker(user, random.choice(STICKERS_NEW_YEAR))
            send_message(chat_id=user, text=text_1)
            print(user)
            time.sleep(random.choice([1, 2, 3, 4, 5]))
            print(text_1)
            # gosha.log_record('Gosha', 'Notification', 1)
            f = True
        if datetime.datetime.now().strftime("%Y-%m-%d %H:%M") == f"{datetime.datetime.now().strftime('%Y-%m-%d')} 09:30" and \
            datetime.datetime.now().weekday() not in [5, 6] and wcr.is_work_day():
            user = -1002059824895
            
            # user = 93027469
            # send_message(chat_id=user, text=text_standup_bot)
            send_reminder(random.choice(standup))
            # bot.send_sticker(user, random.choice(STICKERS_TIME))
            print(user)
            time.sleep(random.choice([1,2,3,4,5]))
            print(text_standup_bot)
            # gosha.log_record('Gosha', 'Notification', 1)
            time.sleep(60)
        # if datetime.datetime.now().strftime("%Y-%m-%d %H:%M") == f"2022-08-31 00:00":
        #     # user = 497831181
        #     # user = 93027469
        #     for user in [497831181, 93027469]:
        #         send_message(chat_id=user, text=wishes)
        #         # bot.send_sticker(user, random.choice(STICKERS_TIME))
        #         print(user)
        #         time.sleep(random.choice([1,2,3,4,5]))
        #         bot.send_sticker(user, random.choice(STICKERS_BIRHTDAY))
        #         print(wishes)
        #         time.sleep(60)
        #     gosha.log_record('Gosha', 'Notification', 1)
        # if datetime.datetime.now().strftime("%Y-%m-%d %H:%M") == f"{datetime.datetime.now().strftime('%Y-%m-%d')} 10:00" and \
        #     datetime.datetime.now().weekday() not in [5, 6] and wcr.is_work_day():
        #     user = -1001353868853
        #     user = -1001573374855
        #     # user = 93027469
        #     send_message(chat_id=user, text=text_standup_ivr)
        #     # bot.send_sticker(user, random.choice(STICKERS_TIME))

        #     print(user)
        #     time.sleep(random.choice([1,2,3,4,5]))
        #     print(text_standup_ivr)
        #     gosha.log_record('Gosha', 'Notification', 1)
        #     time.sleep(60)
        if datetime.datetime.now().strftime("%Y-%m-%d %H:%M") == f"{datetime.datetime.now().strftime('%Y-%m-%d')} 15:36" and \
            datetime.datetime.now().weekday()==3 and wcr.is_work_day():
            user = -1001755210948
            # user = 93027469
            send_message(chat_id=user, text=text_mail_ivr)
            # bot.send_sticker(user, random.choice(STICKERS_IVR))
            print(user)
            time.sleep(random.choice([1,2,3,4,5]))
            # print(text_mail_ivr)
            # gosha.log_record('Gosha', 'Notification', 1)
            time.sleep(60)
        # path_root = '/Users/19028558/Desktop/NLP2.0/intent_recognizer_test/gosha_folder/'
        # if datetime.datetime.now().time().strftime("%H:%M") == "12:00":
        #     with open(os.path.join(path_root, 'gosha.log'), "r") as file:
        #         log_reversed(file, os.path.join(path_root, 'gosha_.log'), bot)
        #     with open(os.path.join(path_root, 'logs.csv'), "r") as file:
        #         log_reversed(file, os.path.join(path_root, 'logs_.csv'), bot)
        #     gosha.log_record('Gosha', 'Pushlogs', 1)
        if f:
            i += 5
        time.sleep(60)
    # bot.polling(none_stop=True)


if __name__=='__main__':
    thread_function()