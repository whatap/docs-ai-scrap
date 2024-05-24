require('dotenv').config();
const { v4: uuid } = require('uuid');
const OpenAI = require('openai');
const { createClient } = require('@supabase/supabase-js');

// Supabase 연결 설정
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_API_KEY);

// OpenAI 연결
const openai = new OpenAI(process.env.OPENAI_API_KEY);
// const embeddings = new OpenAI.OpenAIEmbeddings({ model: "text-embedding-ada-002" });

// 외부 JSON 파일 읽기
const jsonData = require('./whatap-docs.json');

// 데이터 삽입 함수 정의
async function insertData(data) {
    let i = 1;
    for (const doc of data) {
        // UUID 생성
        const id = uuid();

        // 임베딩 생성
        const text = JSON.stringify(doc);
        const embeddingResponse = await openai.embeddings.create({
            model: "text-embedding-ada-002",
            input: [text]
        });
        if (embeddingResponse.error) {
            console.error(`Error embedding data for doc ${i}: ${embeddingResponse.error.message}`);
            continue;
        }

        const embeddingVector = embeddingResponse.data[0].embedding;
        // console.log(embeddingVector);
        // 데이터베이스에 삽입할 데이터 준비
        const insertData = { id: id, metadata: text, embedding: embeddingVector };
        // console.log(insertData);
        // 테이블에 데이터 삽입
        const { data: responseData, error } = await supabase.from('whatap_docs_temp').insert(insertData);
        if (error) {
            console.error(`Error inserting data for doc ${i}: ${error.message}`);
        } else {
            const metadataJson = JSON.parse(insertData.metadata);
            const url = metadataJson.url;
            console.log(`${i} :: 새로운 행이 성공적으로 삽입되었습니다! URL: ${url}`);
        }
        i++;
    }
    console.log("complete!!");
}

insertData(jsonData);