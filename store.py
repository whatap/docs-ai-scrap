import os
from uuid import uuid4
import json
import random
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from supabase import create_client, Client

# Supabase 연결 설정
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_API_KEY")
supabase: Client = create_client(url, key)

# OpenAI 연결
OpenAI.api_key = os.environ["OPENAI_API_KEY"]
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# 외부 JSON 파일 읽기
with open('whatap-docs.json', 'r') as file:
    json_data = json.load(file)

# 데이터 삽입 함수 정의
def insert_data(data):
    i = 1
    for doc in data:
        # UUID 생성
        id = str(uuid4())

        # 임베딩 생성
        text = json.dumps(doc, ensure_ascii=False)
        embedding_vector = embeddings.embed_documents([text])[0]  # 리스트 내 첫 번째 요소 사용

        # 데이터베이스에 삽입할 데이터 준비
        insert_data = {'id': id, 'metadata': text, 'embedding': embedding_vector}
        
        # 테이블에 데이터 삽입
        response = supabase.table('whatap_docs_temp').insert(insert_data).execute()
        metadata_json = json.loads(insert_data['metadata'])
        url = metadata_json.get('url')
        print(f"{i} :: 새로운 행이 성공적으로 삽입되었습니다! URL: {url}")
        i = i + 1
    print("complete!!")


insert_data(json_data)