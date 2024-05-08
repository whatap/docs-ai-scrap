import os
from uuid import uuid4
import json
import random
import openai
from langchain_openai import OpenAIEmbeddings
from supabase import create_client, Client

# Supabase 연결 설정
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_API_KEY")
supabase: Client = create_client(url, key)

# OpenAI 연결
openai.api_key = os.environ["OPENAI_API_KEY"]
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

# 외부 JSON 파일 읽기
with open('whatap-docs.json', 'r') as file:
    json_data = json.load(file)

# whatap_docs_temp 테이블 삭제
def drop_whatap_docs_temp_table():
    query = "DROP TABLE IF EXISTS whatap_docs_temp;"
    response = supabase.query(query)
    if response.error:
        print("테이블 삭제 중 오류 발생:", response.error)

# whatap_docs_temp 테이블 생성
def create_whatap_docs_temp_table():
    query = """
    CREATE EXTENSION IF NOT EXISTS vector;
    CREATE TABLE IF NOT EXISTS whatap_docs_temp (id uuid PRIMARY KEY, metadata jsonb, embedding vector(1536));
    CREATE OR REPLACE function match_whatap_docs_temp (
        query_embedding vector(1536),
        similarity_threshold float,
        match_count int
    )
    returns TABLE (id uuid, metadata jsonb, similarity float)
    LANGUAGE plpgsql
    AS $$
    BEGIN
        return query
        SELECT whatap_docs_temp.id, whatap_docs_temp.metadata, 1 - (whatap_docs_temp.embedding <=> query_embedding) AS similarity
        FROM whatap_docs_temp
        WHERE 1 - (whatap_docs_temp.embedding <=> query_embedding) > similarity_threshold
        ORDER BY whatap_docs_temp.embedding <=> query_embedding
        LIMIT match_count;
    END; $$;
    """
    response = supabase.query(query)
    if response.error:
        print("테이블 생성 중 오류 발생:", response.error)

# whatap_docs 테이블을 whatap_docs_temporary로 이름 변경
def rename_whatap_docs_table():
    query = "ALTER TABLE whatap_docs RENAME TO whatap_docs_temporary;"
    response = supabase.query(query)
    if response.error:
        print("테이블 이름 변경 중 오류 발생:", response.error)

# whatap_docs_temp 테이블을 whatap_docs로 이름 변경
def rename_temp_to_whatap_docs_table():
    query = "ALTER TABLE whatap_docs_temp RENAME TO whatap_docs;"
    response = supabase.query(query)
    if response.error:
        print("테이블 이름 변경 중 오류 발생:", response.error)

# whatap_docs_temporary 테이블 삭제
def drop_whatap_docs_temporary_table():
    query = "DROP TABLE IF EXISTS whatap_docs_temporary;"
    response = supabase.query(query)
    if response.error:
        print("테이블 삭제 중 오류 발생:", response.error)

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


# 1. whatap_docs_temp 테이블을 생성한다. 만약 테이블이 이미 있으면 먼저 삭제한다.
drop_whatap_docs_temp_table()
create_whatap_docs_temp_table()
# 2. whatap_docs_temp 에 docs 스크롤 데이터를 삽입한다. `insert_data(json_data)`
insert_data(json_data)
# 3. whatap_docs 테이블의 이름을 whatap_docs_temporary로 변경한다.
rename_whatap_docs_table()
# 4. whatap_docs_temp 테이블을 whatap_docs로 이름을 변경한다.
rename_temp_to_whatap_docs_table()
# 5. whatap_docs_temporary 테이블을 삭제한다.
drop_whatap_docs_temporary_table()