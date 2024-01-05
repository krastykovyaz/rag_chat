#!/usr/bin/python3
import config
from message_sendler import send_message
import time

def tokenize(s: str) -> list[str]:
    """Очень простая функция разбития предложения на слова"""
    return s.lower().translate(str.maketrans("", "", config.string.punctuation)).split(" ")


LOADER_MAPPING = {
    ".csv": (config.CSVLoader, {}),
    ".doc": (config.UnstructuredWordDocumentLoader, {}),
    ".docx": (config.UnstructuredWordDocumentLoader, {}),
    ".enex": (config.EverNoteLoader, {}),
    ".epub": (config.UnstructuredEPubLoader, {}),
    ".html": (config.UnstructuredHTMLLoader, {}),
    ".md": (config.UnstructuredMarkdownLoader, {}),
    ".odt": (config.UnstructuredODTLoader, {}),
    ".pdf": (config.PDFMinerLoader, {}),
    ".ppt": (config.UnstructuredPowerPointLoader, {}),
    ".pptx": (config.UnstructuredPowerPointLoader, {}),
    ".txt": (config.TextLoader, {"encoding": "utf8"}),
}

# Upload files
def process_text(text):
    lines = text.split("\n")
    lines = [line for line in lines if len(line.strip()) > 2]
    text = "\n".join(lines).strip()
    if len(text) < 10:
        return None
    return text

def load_single_document(file_path: str) -> config.Document:
    ext = "." + file_path.rsplit(".", 1)[-1]
    assert ext in LOADER_MAPPING
    loader_class, loader_args = LOADER_MAPPING[ext]
    loader = loader_class(file_path, **loader_args)
    return loader.load()[0]



# Create database
def build_index(file_paths, chunk_size, chunk_overlap):
    documents = [load_single_document(path) for path in file_paths]
    text_splitter = config.RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = text_splitter.split_documents(documents)
    fixed_documents = []
    for doc in documents:
        doc.page_content = process_text(doc.page_content)
        if not doc.page_content:
            continue
        fixed_documents.append(doc)

    db = config.Chroma.from_documents(
        fixed_documents,
        embeddings,
        client_settings=config.Settings(
            anonymized_telemetry=False
        )
    )
    bm25_retriever = config.BM25Retriever.from_documents(
    documents=fixed_documents,
    preprocess_func=tokenize,
    k=3,
    )

    return db, bm25_retriever



def retrieve(history, db, k_documents):
    context = ""
    if db:
        last_user_message = history[-1]

        retriever = db.as_retriever(search_kwargs={"k": k_documents})
        docs = retriever.get_relevant_documents(last_user_message)
        retrieved_docs = "\n\n".join([doc.page_content for doc in docs])
    return retrieved_docs, docs


embeddings = config.HuggingFaceEmbeddings(model_name=config.embedder_name)

db, bm25_retriever = build_index(config.file_paths, config.chunk_size, config.chunk_overlap)

embedding_retriever = db.as_retriever(search_kwargs={"k": config.k_documents})

ensemble_retriever = config.EnsembleRetriever(
    retrievers=[embedding_retriever, bm25_retriever],
    weights=[0.4, 0.6],
)
DEFAULT_SYSTEM_PROMPT = "Ты — ГигаЧат, русскоязычный автоматический ассистент СберБанка. Ответь на вопрос кратко."

# embedding_retriever = faiss_db.as_retriever(search_kwargs={"k": 5})
def get_answer(message: str):
    # history = []
    # history.append(message)
    # retrieved_docs, docs = retrieve(history, db, k_documents)

    new_message = f"\nИспользуя контекст, ответь на вопрос.\n {message}"
    new_message = DEFAULT_SYSTEM_PROMPT +  new_message

    output = tokenize(new_message)

    # output += f"\n Релевантный документ по вопросу: {docs[0].metadata['source'].split('/')[-1]}"

    return output



# Авторизация в сервисе GigaChat
chat = config.GigaChat(credentials=config.CREDS, verify_ssl_certs=False)

bot = config.telebot.TeleBot(config.TG_API_TOKEN)

keyboard = config.types.InlineKeyboardMarkup()
keyboard.add(
    config.types.InlineKeyboardButton(text='👍', callback_data='button_pressed_Ok'),
    config.types.InlineKeyboardButton(text='👎', callback_data='button_pressed_error')
)

def send2tg(t:str)->None:
    send_message(
        chat_id=config.id_chat,
        text=t
    )


instrucrion = 'Отвечай кратко.'
cur_id = None
from collections import defaultdict
USERS = defaultdict(list)
USER_TIMER = {}

@bot.message_handler(func=lambda message: True)
def echo_message(message):
    global cur_id
    cur_id = message.chat.id
    if message.chat.id not in USER_TIMER:
        USER_TIMER[message.chat.id] = time.time() 
        USERS[message.chat.id].append(DEFAULT_SYSTEM_PROMPT) 
    elif int((time.time() - USER_TIMER[message.chat.id]) // config.FIVE_MINUTE) > 0:
        print('remove')
        del USERS[message.chat.id]
        USERS[message.chat.id].append(DEFAULT_SYSTEM_PROMPT)
    USERS[message.chat.id].append(message.text)
    out_text = ''
    temp_message_id = bot.send_message(message.chat.id, 'Пошел искать...').message_id
    #   mes = get_answer(message.text)
    out_text += message.text
    # giga_answer = qa.invoke({"query": message.text})
    # print(USERS[message.chat.id])
    req = '\n'.join(USERS[message.chat.id])
    print(req)
    giga_answer = qa.invoke({"query": req})
    USERS[message.chat.id].append(giga_answer['result'])
    answer_text = f'''{giga_answer['result']}\r\n'''
    out_text += f"\n{answer_text}"
    send2tg(out_text)
    bot.reply_to(message, answer_text, reply_markup=keyboard)
    bot.delete_message(message.chat.id, temp_message_id)



@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'button_pressed_Ok':
        send2tg('👍🏾')
        bot.answer_callback_query(call.id, 'Супер! Я запомнил🌟')
    elif call.data == 'button_pressed_error':
        temp_message_id = bot.send_message(call.message.json['chat']['id'], 'Секундочку...').message_id
        bot.answer_callback_query(call.id, '😫😫😫')
        send2tg('👎🏾')
        if 'reply_to_message' in call.message.json:
            text = call.message.json['reply_to_message']['text']
        else:
            text = call.message.json['text']
        messages = [
            config.SystemMessage(content=DEFAULT_SYSTEM_PROMPT),
            config.HumanMessage(content=text)
        ]
        res = chat(messages)
        messages.append(res)
        bot.send_message(call.message.json['chat']['id'], res.content)
        bot.delete_message(call.message.json['chat']['id'], temp_message_id)

if __name__=='__main__':
    # while True:
    #     try:
    llm = config.GigaChat(credentials=config.CREDS)
    qa = config.RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=ensemble_retriever,
        return_source_documents=True,
    )
    print('Started...')
    bot.polling()
        # except:
        #     bot.send_message(cur_id, 'Чет пошло не так. Попробуй еще☺️')
        #     pass
