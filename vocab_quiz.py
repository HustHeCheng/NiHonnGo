import random
import readmdict
import re

class VocabQuiz:
    def __init__(self, mdx_path):
        self.mdx = readmdict.MDX(mdx_path)
        self.vocab_list = []
        self._load_vocab()

    def _load_vocab(self):
        for word_bytes, definition_bytes in self.mdx.items():
            try:
                # 解码字节为字符串
                word = word_bytes.decode('utf-8')
                definition = definition_bytes.decode('utf-8')
                
                # 提取汉字（word标签）
                kanji_match = re.search(r'<span class="word">(.*?)</span>', definition)
                if not kanji_match:
                    continue
                    
                kanji = kanji_match.group(1).strip()
                if kanji in ['⇒', '→']:  # 跳过箭头符号
                    continue
                
                # 提取假名（在日语解释之前的假名）
                kana = word.strip()
                
                # 在ncdata-sense-wrap中寻找含义
                sense_matches = re.findall(r'<ul class="ncdata-sense-wrap">(.*?)</ul>', definition, re.DOTALL)
                if not sense_matches:
                    continue
                    
                for sense in sense_matches:
                    # 提取含义（在span标签中的纯文本）
                    meaning_matches = re.findall(r'<span>(.*?)</span>', sense)
                    if not meaning_matches:
                        continue
                    
                    # 找到中文解释（通常是最后一个包含汉字的span）
                    chinese_meaning = None
                    for meaning in meaning_matches:
                        if any('\u4e00' <= char <= '\u9fff' for char in meaning):
                            chinese_meaning = meaning.strip()
                    
                    if chinese_meaning and kanji and kana:
                        # 确保假名和汉字不同
                        if kanji != kana and len(kanji) > 1 and len(kana) > 1:
                            self.vocab_list.append({
                                'kanji': kanji,
                                'kana': kana,
                                'meaning': chinese_meaning
                            })
                        break
            except Exception as e:
                print(f"Error processing entry: {e}")
                continue
        
        print(f"Loaded {len(self.vocab_list)} vocabulary items.")

    def get_random_word(self):
        return random.choice(self.vocab_list)

    def check_answer(self, word, user_answer, answer_type):
        if answer_type == 'kanji':
            # 从【】中提取汉字部分
            kanji_match = re.search(r'【(.*?)】', word['kanji'] if '【' in word['kanji'] else word['kana'])
            if kanji_match:
                kanji = kanji_match.group(1)
            else:
                kanji = word['kanji']
            return user_answer.strip() == kanji
        else:  # kana
            # 移除注释部分（【】及其内容）和空格
            kana = re.sub(r'【.*?】', '', word['kana']).strip()
            return user_answer.strip() == kana

    def format_answer(self, word, answer_type):
        """格式化答案显示"""
        if answer_type == 'kanji':
            # 当要求输入汉字时，显示汉字为主要答案
            # 从【】中提取汉字部分
            kanji_match = re.search(r'【(.*?)】', word['kanji'] if '【' in word['kanji'] else word['kana'])
            if kanji_match:
                kanji = kanji_match.group(1)
            else:
                kanji = word['kanji']
            return f"{kanji}（{word['kana']}）"
        else:
            # 当要求输入假名时，显示假名为主要答案
            kana = re.sub(r'【.*?】', '', word['kana']).strip()
            return f"{kana}（{word['kanji']}）"

def main():
    quiz = VocabQuiz('./dict/xsj/xsjrihanshuangjie.mdx')
    print("\n=== 欢迎使用日语单词测试程序！===")
    print("* 每次会显示一个单词的中文含义")
    print("* 系统会随机要求你输入假名或汉字写法")
    print("* 输入答案后按回车确认")
    print("* 输入 'q' 退出程序")
    print("* 输入 's' 跳过当前单词")
    print("================================\n")
    
    current_word = None
    current_type = None
    correct_count = 0
    total_count = 0
    
    while True:
        if current_word is None:
            current_word = quiz.get_random_word()
            current_type = random.choice(['kanji', 'kana'])
            print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"第 {total_count + 1} 题")
            print(f"单词解释：")
            print(f"【中文】{current_word['meaning']}")
            other_type = 'kana' if current_type == 'kanji' else 'kanji'
            print(f"【日语】{current_word[other_type]}")
            print(f"请输入这个单词的{'汉字' if current_type == 'kanji' else '假名'}写法：")
        
        answer = input().strip()
        
        if answer.lower() == 'q':
            print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"测试结束！共完成 {total_count} 题，答对 {correct_count} 题")
            if total_count > 0:
                print(f"正确率：{(correct_count/total_count*100):.1f}%")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            break
            
        if answer.lower() == 's':
            print(f"跳过！正确答案是：{quiz.format_answer(current_word, current_type)}")
            current_word = None
            total_count += 1
            continue
            
        if quiz.check_answer(current_word, answer, current_type):
            print("✓ 回答正确！")
            correct_count += 1
            total_count += 1
            current_word = None
        else:
            print(f"✗ 回答错误！正确答案是：{quiz.format_answer(current_word, current_type)}")
            print("请重试：")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已终止。再见！")
    except Exception as e:
        print(f"\n程序发生错误：{e}")