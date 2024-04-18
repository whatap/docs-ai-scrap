# WhaTap Docs 스크랩퍼

파이썬 scarpy 프레임워크를 이용해 WhaTap Docs(<https://docs.whatap.io>) 페이지의 콘텐츠를 스크래핑합니다. Open AI의 ChatGPT를 학습시키기 위한 데이터를 구축합니다.

## 주요 파일 구성

- main.py: WhaTap Docs를 스크랩하는 주요 코드입니다.
- store.py: 스크랩한 콘텐츠를 벡터 데이터에 업로드합니다. (supabase - whatap_docs 네임스페이스)
- .env: OpenAI 및 supabase 관련 api key 정보를 입력하세요.
  - OPENAI_API_KEY=""
  - SUPABASE_URL=""
  - SUPABASE_API_KEY=

## scrapy 설치

콘텐츠를 스크랩하기 전에 scrapy를 실행하세요.

```
pip install scrapy
```

## 주요 패키지 설치

- scrapy
- langchain-openai
- supabase
- uuid

## WhaTap Docs 스크랩하기

배치 파일을 실행해 콘텐츠를 스크랩합니다.

```
sh batch.sh
```

## 벡터 DB에 업로드

store.py 파일을 실행해 콘텐츠를 벡터 DB에 업로드하세요.