import json

# 파일 읽기
with open('whatap-temp.json', 'r', encoding='utf-8') as file:
    data = json.load(file)


# 토큰 수 계산을 위한 함수 (여기서는 단순히 문자열 길이를 사용)
def count_tokens(text):
    return len(text)


# 새 JSON 데이터 생성
splitted_data = []

# 분할 사이즈 설정 (예제에서는 간소화된 처리를 위해 문자열 길이 기준으로 처리)
split_size = 7500  # 실제 토큰 수와는 다를 수 있음

for item in data:
    current_contents = item['contents']
    if count_tokens(current_contents) > split_size:
        # 필요한 분할 횟수 계산
        num_splits = count_tokens(current_contents) // split_size + (
            1 if count_tokens(current_contents) % split_size > 0 else 0)

        for i in range(num_splits):
            start = i * split_size
            end = start + split_size
            # 새로운 아이템 생성
            new_item = item.copy()
            new_item['url'] = f"{item['url']}?{i + 1}"
            new_item['contents'] = current_contents[start:end]
            splitted_data.append(new_item)
    else:
        # 분할 필요 없는 경우 그대로 추가
        splitted_data.append(item)

# 결과 파일 저장
output_file_path = 'whatap-docs.json'
with open(output_file_path, 'w', encoding='utf-8') as file:
    json.dump(splitted_data, file, ensure_ascii=False, indent=4)

output_file_path
