import requests
import json
import  time
import glob
import config

URL_SEND_MESSAGE = "https://api.telegram.org/bot{}/sendMessage"

def send_message(chat_id: int,
                 text: str,
                 parse_mode: str = None,
                 buttons: list or None = None,
                 inline_keyboard: list or None = None,
                 one_time_keyboard: bool = True,
                 resize_keyboard: bool = True,
                 remove_keyboard: bool = False, ):
    payload = {
        "chat_id": chat_id,
        "text": text[:4095],
        "reply_markup": {
            "remove_keyboard": remove_keyboard
        }
    }

    if parse_mode:
        payload.update({"parse_mode": parse_mode})

    if buttons:
        # TODO hardcode
        keyboards = [[{"text": text}] for text in buttons]
        payload["reply_markup"].update({
            "keyboard": keyboards,
            "resize_keyboard": resize_keyboard,
            "one_time_keyboard": one_time_keyboard
        })

    if inline_keyboard:
        payload["reply_markup"].update({"inline_keyboard": inline_keyboard})

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.get(URL_SEND_MESSAGE.format(config.TG_API_TOKEN), headers=headers, data=json.dumps(payload))
    response = response.json()
 
    res = response.get("ok")

    # маскирование текста
    payload["text"] = "*******"

def send_photo(chat_id, path):
    file_opened = open((path).encode('utf-8'), 'rb')
    method = "/sendPhoto"
    params = {'chat_id': chat_id}
    files = {'photo': file_opened}
    resp = requests.post('https://api.telegram.org/bot' + config.TG_API_TOKEN + method, params, files=files)
    return resp

if __name__ == '__main__':

    send_message(
        chat_id=config.id_chat,
        text="davai-> @Gosha"
    )