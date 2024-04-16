from dotenv import load_dotenv
import os
from uuid import uuid4
import json
import random
from supabase_py import create_client
import openai
from langchain_openai import OpenAIEmbeddings

load_dotenv()

# Supabase 연결 설정
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_API_KEY')
supabase = create_client(supabase_url, supabase_key)

# OpenAI 연결
openai.api_key = os.environ["OPENAI_API_KEY"]
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# 외부 JSON 파일 읽기
with open('whatap-temp.json', 'r') as file:
    json_data = json.load(file)

text = json.dumps(json_data[0], ensure_ascii=False)
print(text)

doc_result = embeddings.embed_documents([text])
print(doc_result[0][:5])


# 데이터 삽입 함수 정의
# def insert_data(data):
#     for doc in data:
#         # UUID 생성
#         id = str(uuid4())
#
#         # 임베딩 생성
#         embedding_vector = generate_embedding()
#
#         # 데이터베이스에 삽입할 데이터 준비
#         insert_data = {'id': id, 'metadata': doc, 'embedding': embedding_vector}
#
#         # 테이블에 데이터 삽입
#         response = supabase.table('whatap_java').insert([insert_data])
#         if response['status'] == 201:
#             print("새로운 행이 성공적으로 삽입되었습니다!")
#         else:
#             print("새로운 행을 삽입하는 데 실패했습니다!")

# 데이터 삽입 함수 호출
# insert_data(json_data)
