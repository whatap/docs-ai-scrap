import dotenv from 'dotenv';
import { v4 as uuid } from 'uuid';
import OpenAI from 'openai';
import pLimit from 'p-limit';
import { createClient } from '@supabase/supabase-js';
import { promises as fs } from 'fs';

console.log(process.env.SUPABASE_URL)
console.log(process.env.SUPABASE_API_KEY)
const limit = pLimit(31);

// Supabase 연결 설정
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_API_KEY);

// OpenAI 연결
const openai = new OpenAI(process.env.OPENAI_API_KEY);
// const embeddings = new OpenAI.OpenAIEmbeddings({ model: "text-embedding-ada-002" });

// 외부 JSON 파일 읽기

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

async function insertJsonVector(doc, i) {
    // UUID 생성
    const id = uuid();
    // 임베딩 생성
    const text = JSON.stringify(doc);
    const embeddingResponse = await openai.embeddings.create({
        model: "text-embedding-ada-002",
        input: [text]
    });
    if (embeddingResponse.error) {
        throw new Error(`Error embedding data for doc ${i}: ${embeddingResponse.error.message}`);
    }

    const embeddingVector = embeddingResponse.data[0].embedding;
    // console.log(embeddingVector);
    // 데이터베이스에 삽입할 데이터 준비
    const insertData = { id: id, metadata: text, embedding: embeddingVector };
    // console.log(insertData);
    // 테이블에 데이터 삽입
    const { data: responseData, error } = await supabase.from('whatap_docs_temp').insert(insertData);
    if (error) {
        throw new Error(`Error inserting data for doc ${i}: ${error.message}`);
    } 
    
    const metadataJson = JSON.parse(insertData.metadata);
    const url = metadataJson.url;
    console.log(`${i} :: 새로운 행이 성공적으로 삽입되었습니다! URL: ${url}`);
}

// 데이터 삽입 함수 정의
async function insertDataParallel(data) {
    const promises = [];
    let i = 1;
    for (const doc of data) {
        promises.push(limit(() => insertJsonVector(doc, i)));
        i++;
    }

    try {
        const results = await Promise.all(promises);
        console.log('All tasks completed:', results);
    } catch (err) {
        console.error('One of the tasks failed:', err);
        process.exit(1);
    }
}

// JSON 파일을 읽고 파싱
async function loadData() {
    const data = await fs.readFile('./whatap-docs.json', 'utf8');
    return JSON.parse(data);
}

// 데이터 로드 후 함수 호출
loadData().then(data => {
    insertDataParallel(data);
}).catch(err => {
    console.error('Failed to load data:', err);
    process.exit(1);
});
