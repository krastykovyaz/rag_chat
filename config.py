import os
from langchain.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PDFMinerLoader,
    TextLoader,
    UnstructuredEmailLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.docstore.document import Document
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import HumanMessage, SystemMessage
from langchain.vectorstores import Chroma
from chromadb.config import Settings
from langchain.chains import RetrievalQA
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.llms.gigachat import GigaChat
from langchain.chat_models import GigaChat

import string
import telebot
from telebot import types
import string
from credentials import CREDS, TG_API_TOKEN, id_chat


embedder_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
directory = './dataset_word/word'
file_paths = [os.path.join(directory, f) for f in os.listdir(directory)]
file_paths = [file for file in file_paths if file.split('.')[-1] in ['pdf', 'docx', 'txt']]
directory = './dataset_word/pdf'
for f in os.listdir(directory):
    file_paths.append(os.path.join(directory, f))

chunk_size = 350 #500 #1000
chunk_overlap = 100
k_documents = 2
FIVE_MINUTE = 60