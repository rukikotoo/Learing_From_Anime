# LearningFromAnime
扔掉新标日吧，通过动画学习日语。将目录中的ass字幕文件转换为可以通过anki进行复习的apkg文件。当然你要准备好你自己的api_key。看的是内嵌字幕版本没有字幕文件？实在找不到字幕可以OCR。

## 简介
这是一个用于从日文字幕文件（`.ass` 格式）中提取对话，并生成 Anki 卡片包的工具。它结合了 OpenAI 的语言模型（LLM），为每个日文句子生成语法解释，帮助用户更好地学习日语。generate_grammar_explanation这个函数里填写api和model。

## 功能
1. **从 `.ass` 文件中提取日文和中文字幕**：
   - 自动识别并提取日文和中文字幕。
   - 确保日文和中文字幕数量一致。

2. **生成语法解释**：
   - 使用 OpenAI 的 LLM 为每个日文句子生成语法解释，包括：
     - 语法结构分析。
     - 每个词的意思。
     - 动词原型及词尾变化解释。

3. **生成 Anki 卡片包**：
   - 将提取的对话和语法解释生成 Anki 卡片包（`.apkg` 文件）。

## 依赖项
1. **Python 3.8+**：
   - 确保安装了 Python 3.8 或更高版本。

2. **第三方库**：
   - `genanki`：用于生成 Anki 卡片包。
   - `openai`：用于调用 OpenAI 的 LLM API。
   - `tqdm`：用于显示进度条。
   - `re`：用于正则表达式操作（Python 内置库）。

3. **OpenAI API Key**：
   - 需要一个有效的 OpenAI API Key，用于调用 LLM。

## 安装
1. **克隆代码**：
   ```bash
   git clone https://github.com/your-username/subtitle-anki-generator.git
   cd subtitle-anki-generator
