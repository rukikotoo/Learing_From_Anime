import os
import re
import genanki
import openai
from openai import OpenAI
import tqdm
import signal

import re

def extract_dialogues_from_ass(file_path):
    """
    从 .ass 文件中提取中日文对话，并自动识别语言类型。
    返回配对的日文和中文列表。
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    japanese_dialogues = []
    chinese_dialogues = []


    for line in lines:
        # 匹配 Dialogue 行，并提取对话内容
        if line.startswith("Dialogue:"):
            # 提取对话内容（忽略特效标签如 {\blur3}）
            dialogue_match = re.search(r",,(.*)", line)
            if dialogue_match:
                dialogue_text = dialogue_match.group(1)
                # 去除字幕中的特效标记（如 {\blur3}）
                cleaned_text = re.sub(r"{.*?}", "", dialogue_text).strip()

                # 判断语言类型
                if re.search(r"[\u3040-\u30FF\u4E00-\u9FFF]", cleaned_text):  # 包含日文
                    if re.search(r"[\u3040-\u30FF]", cleaned_text):  # 假名检测 -> 判定为日文
                        japanese_dialogues.append(cleaned_text)
                    elif re.search(r"[\u4E00-\u9FFF]", cleaned_text):  # 如果只含中文汉字 -> 判定为中文
                        chinese_dialogues.append(cleaned_text)

    # 确保两边字幕数量一致（通过时间戳对齐）
    if len(japanese_dialogues) != len(chinese_dialogues):
        print(f"警告：文件 {file_path} 的日文和中文字幕数量不一致！")
        print(f"日文对话数量: {len(japanese_dialogues)}, 中文对话数量: {len(chinese_dialogues)}")

    return list(zip(japanese_dialogues, chinese_dialogues))


def generate_grammar_explanation(llm_api_key, japanese_sentence):
    """
    使用 LLM 为日文句子生成语法解释。
    """
    try:
        client = OpenAI(
            api_key="",
            base_url=""
        )
        with open('prompt.txt', 'r', encoding='utf-8') as file:
            prompt = file.read()

        response = client.chat.completions.create(
            model="",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",
                 "content": f"解释该句子的语法结构和每一个词的意思，分词并注音。将所有动词标注原型并解释动词词尾语法变换：{japanese_sentence}"}
            ],
            temperature=0.7,
        )
        explanation = response.choices[0].message.content
        return explanation
    except Exception as e:
        print(f"生成语法解释时出错：{e}")
        return "语法解释生成失败，请稍后重试。"


def process_file_into_deck(file_path, llm_api_key, model, output_file):
    """
    修改后的函数：处理文件并每10次API调用保存一次
    """
    dialogues = extract_dialogues_from_ass(file_path)
    deck_name = os.path.splitext(os.path.basename(file_path))[0]
    deck = genanki.Deck(
        deck_id=abs(hash(deck_name)) % (10 ** 10),
        name=f"{deck_name} 卡片库（含语法解释）"
    )

    api_call_count = 0  # API调用计数器

    with tqdm.tqdm(total=len(dialogues), desc=f"处理 {deck_name}", unit="卡片") as pbar:
        for japanese, chinese in dialogues:
            grammar_explanation = generate_grammar_explanation(llm_api_key, japanese)
            back_content = f"{chinese}<br><br>{grammar_explanation}"

            note = genanki.Note(
                model=model,
                fields=[japanese, back_content]
            )
            deck.add_note(note)

            # 更新计数器并检查保存条件
            api_call_count += 1
            if api_call_count % 1 == 0:
                save_deck_to_file(deck, output_file)

            pbar.update(1)

    # 处理剩余不足10次的卡片
    if api_call_count % 1 != 0:
        save_deck_to_file(deck, output_file)

    return deck


def save_deck_to_file(deck, output_file):
    """
    将 Anki 卡片组保存为 .apkg 文件。
    """
    genanki.Package(deck).write_to_file(output_file)
    print(f"Anki 卡片包已保存到文件：{output_file}")


if __name__ == "__main__":
    # 配置参数
    ass_directory = "./"
    llm_api_key = openai.api_key

    # 创建 Anki 模型
    model = genanki.Model(
        1607392319,
        'Subtitle Model with Grammar',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Front}}',
                'afmt': '{{Front}}<hr id="answer">{{Back}}',
            },
        ]
    )

    # 注册中断信号处理函数
    def handle_interrupt(signum, frame):
        print("\n捕获到中断信号，程序终止。")
        exit(0)

    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)

    try:
        for filename in os.listdir(ass_directory):
            if filename.endswith(".ass"):
                file_path = os.path.join(ass_directory, filename)
                output_file = os.path.splitext(filename)[0] + ".apkg"
                print(f"正在处理文件：{file_path}")

                # 处理文件并自动保存
                process_file_into_deck(file_path, llm_api_key, model, output_file)

    except Exception as e:
        print(f"程序运行出错：{str(e)}")
        exit(1)