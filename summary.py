import requests, os
from bs4 import BeautifulSoup
import getpass
from langchain.document_loaders import PDFPlumberLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI

from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import LLMChain
from langchain.output_parsers import CommaSeparatedListOutputParser

os.environ['OPENAI_API_KEY'] = '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' #getpass.getpass('OpenAI API Key:')
llm_16k = ChatOpenAI(model="gpt-3.5-turbo-1106")

def annual_report(id,y):
    url = 'https://doc.twse.com.tw/server-java/t57sb01'
    # 建立 POST 請求的表單
    data = {
        "id":"",
        "key":"",
        "step":"1",
        "co_id":id,
        "year":y,
        "seamon":"",
        "mtype":'F',
        "dtype":'F04'
    }
    try:
        # 發送 POST 請求
        response = requests.post(url, data=data)
        # 取得回應後擷取檔案名稱
        link=BeautifulSoup(response.text, 'html.parser')
        link1=link.find('a').text
        print(link1)
    except Exception as e:
        print(f"發生{e}錯誤")
    # 建立第二個 POST 請求的表單
    data2 = {
        'step':'9',
        'kind':'F',
        'co_id':id,
        'filename':link1 # 檔案名稱
    }
    try:
        # 發送 POST 請求
        response = requests.post(url, data=data2)
        link=BeautifulSoup(response.text, 'html.parser')
        link1=link.find('a')
        # 取得 PDF 連結
        link2 = link1.get('href')
        print(link2)
    except Exception as e:
        print(f"發生{e}錯誤")
    # 發送 GET 請求
    try:
        response = requests.get('https://doc.twse.com.tw' + link2)
        # 取得 PDF 資料
        folder_path = 'content'
        
        file_path = os.path.join(folder_path, y + '_' + id + '.pdf')
        print(file_path)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print('OK')
    except Exception as e:
        print(f"發生{e}錯誤")

def pdf_loader(file,size,overlap):  #檔案 分割字元數 重覆字元數
    loader = PDFPlumberLoader(file)
    doc = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=size,
                            chunk_overlap=overlap)
    new_doc = text_splitter.split_documents(doc)
    db = FAISS.from_documents(new_doc, OpenAIEmbeddings())
    return db

def get_db(y,stock_id):
    file_name =  y + '_' + stock_id + '.pdf'
    annual_report(stock_id,y)
    db = pdf_loader(f'./content/{file_name}',500,50)
    return db


##年報總結##
def get_summary(db):
    # 建立關鍵字串列
    key_word = ['有關市場策略的調整或變化有何提及？',
            '公司對未來一年的展望是什麼？',
            '公司的總收入是否增長，淨利潤的正負情況是否有變化？',
            '國際競爭及海外市場情況',
            '目前的研發狀況?']
    data_list = []
    for word in key_word:
        data = db.max_marginal_relevance_search(word)
        # 整合 Document 串列
        data_list += data

    # 建立提示訊息串列
    prompt_template = [("system","你的任務是生成年報摘要。"
                    "我們提供年報{text}請你負責生成,"
                    "且要保留重點如營收漲跌、開發項目等,"
                    "最後請使用繁體中文輸出報告")]
    prompt = ChatPromptTemplate.from_messages(messages=prompt_template)

    chain_refine_16k = load_summarize_chain(llm=llm_16k,
                                            chain_type='stuff',
                                            prompt=prompt)

    summary = chain_refine_16k.run(data_list) #摘要文字
    return summary


##關鍵字分析##
def analyze_chain(db,input):
    output_parser = CommaSeparatedListOutputParser()

    word_prompt=ChatPromptTemplate.from_messages(messages=[
        ("human","從{input}聯想出4個與年報分析有關的重要關鍵字,"\
        "請確保回答具有具有關聯性、多樣性和變化性。 \n "
        "僅回覆關鍵字, 並以半形逗號與空格來分隔。不要加入其他內容"
        "")]
    )
    word_chain = LLMChain(llm=llm_16k, prompt=word_prompt)

    data_prompt = ChatPromptTemplate.from_messages(messages=[
        ("system","你現在是一位專業的股票分析師,"
        "你會以詳細、嚴謹的角度進行年報分析, 針對{output}作分析並提及重要數字\
        ,然後生成一份專業的趨勢分析報告。"),
        ("human","{text}")])
    data_chain = LLMChain(llm=llm_16k, prompt=data_prompt)
    
    
    # 搜尋「問題」的相關資料
    data = db.max_marginal_relevance_search(input)

    # 第一個 Chain 元件, 建立「關鍵字」串列
    word = word_chain(input)
    word_list = output_parser.parse(word['text'])

    # 搜尋「關鍵字」的相關資料
    for i in word_list:
        data += db.max_marginal_relevance_search(i,k=2)
        
    word_list.append(input)

    # 第二個 Chain 元件, 生成分析報告
    result = data_chain({'output':word_list,'text':data})

    return result['text']


