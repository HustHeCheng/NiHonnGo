from flask import Flask, render_template_string, request, jsonify, Response
import requests
import random
import time
from collections import deque
import os

app = Flask(__name__)

# 词汇级别定义
LEVELS = {
    'N5': '基础词汇',
    'N4': '初级词汇',
    'N3': '中级词汇',
    'N2': '中高级词汇',
    'N1': '高级词汇'
}

# 词汇缓存
word_cache = {
    'N5': deque(maxlen=20),
    'N4': deque(maxlen=20),
    'N3': deque(maxlen=20),
    'N2': deque(maxlen=20),
    'N1': deque(maxlen=20),
    'last_fetch': {},  # 记录每个级别最后一次获取时间
}

# 英文到中文的映射词典
en_to_zh = {
    # 名词
    'school': '学校',
    'river': '河流',
    'hand': '手',
    'door': '门',
    'glasses': '眼镜',
    'tobacco': '烟',
    'work': '工作',
    'english': '英语',
    'japanese': '日语',
    'chinese': '中文',
    'question': '问题',
    'room': '房间',
    'child': '孩子',
    'student': '学生',
    'time': '时间',
    'rain': '雨',
    'teacher': '老师',
    'year': '年',
    'letter': '信',
    'telephone': '电话',
    'water': '水',
    'illness': '病',
    'book': '书',
    'cat': '猫',
    'dog': '狗',
    'house': '房子',
    'car': '车',
    'train': '电车',
    'station': '车站',
    'hospital': '医院',
    'library': '图书馆',
    'store': '商店',
    'restaurant': '餐厅',
    'money': '钱',
    'person': '人',
    'friend': '朋友',
    'family': '家族',
    'mother': '母亲',
    'father': '父亲',
    'sister': '姐妹',
    'brother': '兄弟',
    
    # 形容词
    'red': '红色',
    'blue': '蓝色',
    'white': '白色',
    'black': '黑色',
    'yellow': '黄色',
    'green': '绿色',
    'big': '大',
    'small': '小',
    'tall': '高',
    'short': '矮',
    'fast': '快',
    'slow': '慢',
    'hot': '热',
    'cold': '冷',
    'difficult': '难',
    'easy': '容易',
    'expensive': '贵',
    'cheap': '便宜',
    'new': '新',
    'old': '旧',
    'good': '好',
    'bad': '坏',
    'busy': '忙',
    'free': '空闲',
    'happy': '开心',
    'sad': '伤心',
    
    # 动词
    'eat': '吃',
    'drink': '喝',
    'sleep': '睡觉',
    'wake': '醒',
    'study': '学习',
    'teach': '教',
    'work': '工作',
    'play': '玩',
    'read': '读',
    'write': '写',
    'speak': '说',
    'listen': '听',
    'watch': '看',
    'see': '看见',
    'buy': '买',
    'sell': '卖',
    'give': '给',
    'take': '拿',
    'make': '做',
    'use': '使用',
    'come': '来',
    'go': '去',
    'walk': '走',
    'run': '跑',
    
    # 时间相关
    'morning': '早上',
    'afternoon': '下午',
    'evening': '晚上',
    'night': '夜晚',
    'today': '今天',
    'tomorrow': '明天',
    'yesterday': '昨天',
    'week': '星期',
    'month': '月',
    'year': '年',
    'hour': '小时',
    'minute': '分钟',
    'second': '秒',
    'day': '天',
    'season': '季节',
    'spring': '春天',
    'summer': '夏天',
    'autumn': '秋天',
    'winter': '冬天'
}

def get_jisho_words(level):
    """从Jisho API获取词汇"""
    print(f"\n开始获取 {level} 级别的词汇...")
    
    # 根据级别设置不同的搜索参数
    if level == 'N5':
        # N5级别：使用基础词汇和常用词
        tags = ['jlpt-n5', 'common']
        search_params = '#jlpt-n5 #common'
    elif level == 'N4':
        tags = ['jlpt-n4', 'common']
        search_params = '#jlpt-n4 #common'
    elif level == 'N3':
        tags = ['jlpt-n3']
        search_params = '#jlpt-n3'
    elif level == 'N2':
        tags = ['jlpt-n2']
        search_params = '#jlpt-n2'
    else:  # N1
        tags = ['jlpt-n1']
        search_params = '#jlpt-n1'
    
    print(f"使用搜索参数: {search_params}")
    
    words = []
    page = random.randint(1, 5)  # 随机获取不同页面的词汇
    print(f"随机选择页面: {page}")
    
    try:
        # 构建API请求
        url = 'https://jisho.org/api/v1/search/words'
        params = {'keyword': search_params, 'page': page}
        print(f"发送API请求: {url}?keyword={search_params}&page={page}")
        
        # 发送请求并获取响应
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' not in data:
            print("API响应中没有找到数据字段")
            return []
            
        print(f"\n找到 {len(data['data'])} 个词条，开始处理...")
        
        # 处理每个词条
        for idx, item in enumerate(data['data'], 1):
            if len(words) >= 20:
                print("已达到20个词的上限，停止处理")
                break
                
            print(f"\n处理第 {idx} 个词条:")
            
            # 检查必要的字段
            if not item.get('japanese'):
                print("- 跳过：没有日语读音信息")
                continue
                
            japanese = item['japanese'][0]
            kanji = japanese.get('word', '')
            kana = japanese.get('reading', '')
            
            print(f"- 汉字: {kanji}")
            print(f"- 假名: {kana}")
            
            if not kanji and not kana:
                print("- 跳过：既没有汉字也没有假名")
                continue
                
            if not kanji:
                print("- 没有汉字，使用假名代替")
                kanji = kana
            
            # 获取词义
            if not item.get('senses'):
                print("- 跳过：没有词义信息")
                continue
            
            print("- 开始处理词义:")
            chinese = None
            
            # 尝试从所有释义中找到合适的中文翻译
            for sense_idx, sense in enumerate(item['senses'], 1):
                print(f"  处理第 {sense_idx} 个释义:")
                
                # 首选：直接的中文释义
                if sense.get('chinese_definitions'):
                    chinese = sense['chinese_definitions'][0]
                    print(f"  - 找到中文释义: {chinese}")
                    break
                
                # 次选：通过映射转换英文释义
                elif sense.get('english_definitions'):
                    print("  - 处理英文释义:")
                    for eng_def in sense['english_definitions']:
                        # 清理英文释义
                        eng_def = eng_def.lower()
                        eng_def = eng_def.split('(')[0].strip()
                        eng_def = eng_def.split(',')[0].strip()
                        eng_def = eng_def.split(';')[0].strip()
                        
                        print(f"    尝试映射: {eng_def}")
                        if eng_def in en_to_zh:
                            chinese = en_to_zh[eng_def]
                            print(f"    - 成功映射为: {chinese}")
                            break
                    
                    if chinese:  # 如果找到了映射，就跳出外层循环
                        break
            
            # 如果找不到中文释义，尝试使用词性标签
            if not chinese and 'tags' in item:
                print("- 尝试通过词性标签推测含义:")
                tags = [tag.lower() for tag in item.get('tags', [])]
                print(f"  词性标签: {tags}")
                
                if 'adjective' in tags or 'verb' in tags:
                    for eng_def in item['senses'][0].get('english_definitions', []):
                        eng = eng_def.lower().split()[0]
                        print(f"  尝试映射第一个词: {eng}")
                        if eng in en_to_zh:
                            chinese = en_to_zh[eng]
                            print(f"  - 成功映射为: {chinese}")
                            break
            
            # 添加词条
            if chinese and kanji and kana:
                words.append({
                    'kanji': kanji,
                    'kana': kana,
                    'chinese': chinese
                })
                print(f"\n✓ 成功添加词条: {kanji} ({kana}) - {chinese}")
            else:
                print("\n✗ 跳过词条：缺少必要信息")
                if not chinese:
                    print("  - 缺少中文释义")
                if not kanji:
                    print("  - 缺少汉字")
                if not kana:
                    print("  - 缺少假名")
        
        print(f"\n处理完成，共获取 {len(words)} 个词条")
        
    except requests.RequestException as e:
        print(f"网络错误: {e}")
    except ValueError as e:
        print(f"JSON解析错误: {e}")
    except Exception as e:
        print(f"未预期的错误: {e}")
    
    # 如果没有获取到足够的词，返回基本词汇
    if len(words) < 4:
        print("\n获取的词汇不足，使用基本词汇")
        basic_words = [
            {'kanji': '本', 'kana': 'ほん', 'chinese': '书'},
            {'kanji': '猫', 'kana': 'ねこ', 'chinese': '猫'},
            {'kanji': '犬', 'kana': 'いぬ', 'chinese': '狗'},
            {'kanji': '水', 'kana': 'みず', 'chinese': '水'},
            {'kanji': '月', 'kana': 'つき', 'chinese': '月亮'},
            {'kanji': '日', 'kana': 'ひ', 'chinese': '太阳'},
            {'kanji': '火', 'kana': 'ひ', 'chinese': '火'},
            {'kanji': '木', 'kana': 'き', 'chinese': '树'},
        ]
        return basic_words[:20]
    
    print("\n返回获取的词汇")
    return words

def get_vocabulary(level='N5'):
    """获取指定级别的词汇，如果缓存不足则从API获取新词"""
    current_time = time.time()
    
    # 如果缓存为空或者已经过了5分钟，重新获取词汇
    if (len(word_cache[level]) < 5 or 
        level not in word_cache['last_fetch'] or 
        current_time - word_cache['last_fetch'].get(level, 0) > 300):
        
        new_words = get_jisho_words(level)
        word_cache[level].extend(new_words)
        word_cache['last_fetch'][level] = current_time
    
    return list(word_cache[level])

# HTML 模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>日语学习</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }
        .container {
            text-align: center;
            background: white;
            padding: 2em;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            max-width: 600px;
            width: 90%;
        }
        .word {
            font-size: 2em;
            margin-bottom: 1em;
        }
        input {
            padding: 0.5em;
            margin: 0.5em;
            width: 200px;
            font-size: 1em;
        }
        .result {
            margin-top: 1em;
            color: #666;
            min-height: 3em;
        }
        .correct {
            color: green;
        }
        .incorrect {
            color: red;
        }
        .level-select {
            margin-bottom: 2em;
            padding: 1em;
            border-bottom: 1px solid #eee;
        }
        .level-btn {
            padding: 0.5em 1em;
            margin: 0.2em;
            border: none;
            border-radius: 5px;
            background-color: #f0f0f0;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .level-btn.active {
            background-color: #4CAF50;
            color: white;
        }
        .stats {
            margin-top: 1em;
            font-size: 0.9em;
            color: #666;
        }
        .loading {
            margin-top: 1em;
            color: #666;
            font-style: italic;
        }
        #remainingWords {
            color: #2196F3;
            font-weight: bold;
        }
        .level-btn {
            position: relative;
        }
        .level-btn.loading::after {
            content: '...';
            position: absolute;
            right: 0;
            animation: dots 1s infinite;
        }
        @keyframes dots {
            0% { content: '.'; }
            33% { content: '..'; }
            66% { content: '...'; }
        }
        .sound-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
        }
        .sound-toggle input[type="checkbox"] {
            width: auto;
            margin: 0;
        }
        .word-container {
            position: relative;
            display: inline-block;
        }
        .sound-icon {
            position: absolute;
            top: -10px;
            right: -25px;
            width: 20px;
            height: 20px;
            cursor: pointer;
            opacity: 0.6;
            transition: opacity 0.3s;
        }
        .sound-icon:hover {
            opacity: 1;
        }
        .sound-icon svg {
            width: 100%;
            height: 100%;
            fill: #666;
            transition: fill 0.3s;
        }
        .sound-icon.playing svg {
            fill: #4CAF50;
        }
        .sound-loading {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.8);
        }
        .spinner {
            width: 12px;
            height: 12px;
            border: 2px solid #4CAF50;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to {transform: rotate(360deg);}
        }
        .error-message {
            color: #f44336;
            font-size: 0.9em;
            margin-top: 0.5em;
            min-height: 1.2em;
        }
        .sound-icon:hover svg {
            fill: #4CAF50;
        }
        .sound-icon.disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
    </style>
</head>
<body>
    <div class="sound-toggle">
        <input type="checkbox" id="autoSound" checked>
        <label for="autoSound">自动发音</label>
    </div>
    <div class="container">
        <div class="level-select" id="levelSelect">
            <div style="margin-bottom: 0.5em">选择词汇级别：</div>
            <button class="level-btn active" data-level="N5">N5 基础</button>
            <button class="level-btn" data-level="N4">N4 初级</button>
            <button class="level-btn" data-level="N3">N3 中级</button>
            <button class="level-btn" data-level="N2">N2 中高级</button>
            <button class="level-btn" data-level="N1">N1 高级</button>
        </div>
        <div class="word-container">
            <div class="word" id="chinese"></div>
            <div class="sound-icon" onclick="playCurrentWord()" title="点击播放" id="soundIcon">
                <svg viewBox="0 0 24 24">
                    <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                </svg>
                <div class="sound-loading" style="display: none;">
                    <div class="spinner"></div>
                </div>
            </div>
        </div>
        <div id="soundError" class="error-message" style="display: none;"></div>
        <div>
            <input type="text" id="answerInput" placeholder="输入答案" />
        </div>
        <div class="result" id="result"></div>
        <div class="stats">
            <span>正确: <span id="correctCount">0</span></span>
            &nbsp;|&nbsp;
            <span>错误: <span id="incorrectCount">0</span></span>
            &nbsp;|&nbsp;
            <span>正确率: <span id="accuracy">0</span>%</span>
            &nbsp;|&nbsp;
            <span>剩余词汇: <span id="remainingWords">0</span></span>
        </div>
        <div id="loading" class="loading" style="display: none;">
            正在获取新词汇...
        </div>
    </div>
    <script>
        let currentWord = null;
        let currentMode = null;
        let currentLevel = 'N5';
        let stats = {
            correct: 0,
            incorrect: 0
        };
        let currentAudio = null;

        // 创建音频元素
        const audioElement = new Audio();
        
        // 播放当前词汇的发音
        async function playCurrentWord() {
            if (!currentWord || !currentWord.kanji) return;
            
            try {
                // 使用Google TTS API生成语音URL
                const text = currentWord.kanji;
                const url = `https://translate.google.com/translate_tts?ie=UTF-8&tl=ja&client=tw-ob&q=${encodeURIComponent(text)}`;
                
                // 如果有正在播放的音频，停止它
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio.currentTime = 0;
                }
                
                // 创建新的音频实例
                currentAudio = new Audio(url);
                await currentAudio.play();
            } catch (error) {
                console.error('播放失败:', error);
            }
        }

        // 检查是否启用自动发音
        function isAutoSoundEnabled() {
            return document.getElementById('autoSound').checked;
        }
        let remainingWords = 0;
        let isLoadingWords = false;

        function updateStats() {
            document.getElementById('correctCount').textContent = stats.correct;
            document.getElementById('incorrectCount').textContent = stats.incorrect;
            const total = stats.correct + stats.incorrect;
            const accuracy = total > 0 ? Math.round((stats.correct / total) * 100) : 0;
            document.getElementById('accuracy').textContent = accuracy;
            document.getElementById('remainingWords').textContent = remainingWords;
        }

        async function fetchNewWords(retryCount = 0) {
            const maxRetries = 3;
            const loadingDiv = document.getElementById('loading');
            
            if (isLoadingWords) return;
            isLoadingWords = true;
            
            try {
                // 显示加载状态
                loadingDiv.textContent = '正在获取新词汇...';
                loadingDiv.style.display = 'block';
                
                const response = await fetch(`/get_word?level=${currentLevel}&refresh=true`);
                if (!response.ok) {
                    throw new Error('获取词汇失败');
                }

                const data = await response.json();
                if (data.error) {
                    throw new Error(data.error);
                }

                remainingWords = data.remaining_words;
                console.log(`成功获取新词汇，剩余数量: ${remainingWords}`);
                
                // 更新级别按钮状态
                document.querySelectorAll('.level-btn').forEach(btn => {
                    if (btn.dataset.level === currentLevel) {
                        btn.classList.remove('loading');
                    }
                });

            } catch (error) {
                console.error('获取新词失败:', error);
                
                if (retryCount < maxRetries) {
                    // 重试
                    console.log(`重试获取新词 (${retryCount + 1}/${maxRetries})...`);
                    loadingDiv.textContent = `获取失败，正在重试 (${retryCount + 1}/${maxRetries})...`;
                    setTimeout(() => fetchNewWords(retryCount + 1), 1000);
                    return;
                } else {
                    // 达到最大重试次数
                    loadingDiv.textContent = '获取新词汇失败，请稍后再试';
                    throw new Error('获取新词汇失败，已达到最大重试次数');
                }
            } finally {
                isLoadingWords = false;
                // 如果成功获取了词汇，隐藏加载提示
                if (remainingWords > 0) {
                    loadingDiv.style.display = 'none';
                }
            }
        }

        // 初始化事件监听器
        document.addEventListener('DOMContentLoaded', () => {
            // 级别选择事件处理
            document.querySelectorAll('.level-btn').forEach(button => {
                button.addEventListener('click', async function() {
                    const newLevel = this.dataset.level;
                    if (newLevel === currentLevel) return;
                    
                    // 更新按钮状态
                    document.querySelector('.level-btn.active').classList.remove('active');
                    this.classList.add('active');
                    this.classList.add('loading');
                    
                    // 更新当前级别并重置统计
                    currentLevel = newLevel;
                    stats.correct = 0;
                    stats.incorrect = 0;
                    remainingWords = 0;
                    
                    try {
                        // 获取新词
                        await fetchNewWords();
                        await getNewWord();
                    } catch (error) {
                        console.error('切换级别失败:', error);
                    } finally {
                        // 移除加载状态
                        this.classList.remove('loading');
                    }
                    
                    updateStats();
                });
            });

            // 输入框回车事件
            document.getElementById('answerInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !this.disabled) {
                    checkAnswer();
                }
            });

            // 自动发音开关事件
            document.getElementById('autoSound').addEventListener('change', function() {
                if (this.checked && currentWord) {
                    playCurrentWord().catch(error => {
                        console.error('自动发音失败:', error);
                    });
                }
            });

            // 初始加载
            fetchNewWords().then(() => getNewWord()).catch(error => {
                console.error('初始化失败:', error);
            });
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    """渲染主页"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_word')
def get_word():
    """获取词汇"""
    level = request.args.get('level', 'N5')
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # 如果请求刷新或词汇不足，获取新词
    if refresh or len(word_cache[level]) < 5:
        new_words = get_jisho_words(level)
        if new_words:
            word_cache[level].extend(new_words)
            word_cache['last_fetch'][level] = time.time()
    
    words = list(word_cache[level])
    if not words:
        return jsonify({'error': f'No words available for level {level}'}), 404
    
    word = random.choice(words)
    word_id = words.index(word)
    mode = random.choice(['kana', 'kanji'])
    
    return jsonify({
        'word': {
            'id': word_id,
            'chinese': word['chinese'],
            'kanji': word['kanji'],
            'kana': word['kana']
        },
        'mode': mode,
        'remaining_words': len(words)
    })

@app.route('/check_answer', methods=['POST'])
def check_answer():
    """检查答案"""
    try:
        data = request.get_json()
        level = data.get('level', 'N5')
        words = list(word_cache[level])
        
        if data['word_id'] >= len(words):
            return jsonify({'error': 'Invalid word ID'}), 400
            
        word = words[data['word_id']]
        mode = data['mode']
        user_answer = data['answer']
        
        correct_answer = word[mode]
        is_correct = user_answer == correct_answer
        
        # 如果答对了，从缓存中移除这个词
        if is_correct and word in word_cache[level]:
            word_cache[level].remove(word)
        
        return jsonify({
            'correct': is_correct,
            'correct_answer': correct_answer,
            'remaining_words': len(word_cache[level])
        })
    except Exception as e:
        print(f"Error checking answer: {e}")
        return jsonify({'error': 'Failed to check answer'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=56459)
                    ...data.word,
                    kanji: data.word_info.kanji,
                    kana: data.word_info.kana
                };
                currentMode = data.mode;
                remainingWords = data.remaining_words;
                
                // 更新显示
                document.getElementById('chinese').textContent = currentWord.chinese;
                document.getElementById('answerInput').value = '';
                document.getElementById('answerInput').placeholder = currentMode === 'kana' ? '输入假名' : '输入汉字';
                document.getElementById('result').textContent = '';
                document.getElementById('answerInput').focus();
                updateStats();

                // 如果启用了自动发音，播放当前词汇
                if (isAutoSoundEnabled()) {
                    // 延迟一小段时间再播放，确保界面已更新
                    setTimeout(() => {
                        playCurrentWord();
                    }, 100);
                }
            } catch (error) {
                console.error('获取新词失败:', error);
                document.getElementById('result').textContent = '获取词汇失败，请刷新页面重试';
                document.getElementById('result').className = 'result incorrect';
            }
        }

        // 播放当前词汇的发音
        async function playCurrentWord() {
            const soundIcon = document.getElementById('soundIcon');
            const soundError = document.getElementById('soundError');
            const loadingSpinner = soundIcon.querySelector('.sound-loading');
            
            if (!currentWord || (!currentWord.kanji && !currentWord.kana)) {
                soundError.textContent = '没有可用的发音文本';
                soundError.style.display = 'block';
                return;
            }
            
            // 如果正在播放或加载中，不执行任何操作
            if (soundIcon.classList.contains('playing') || loadingSpinner.style.display === 'flex') {
                return;
            }
            
            try {
                // 优先使用汉字进行发音，如果没有汉字则使用假名
                const text = currentWord.kanji || currentWord.kana;
                
                // 显示加载动画
                loadingSpinner.style.display = 'flex';
                soundIcon.classList.add('disabled');
                soundError.style.display = 'none';

                // 如果有正在播放的音频，停止它
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio.currentTime = 0;
                }

                // 发送发音请求
                const response = await fetch('/speak', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: text })
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.details || '发音请求失败');
                }

                const audioBlob = await response.blob();
                const audioUrl = URL.createObjectURL(audioBlob);
                
                // 创建新的音频实例
                currentAudio = new Audio(audioUrl);
                
                // 音频加载完成时的处理
                currentAudio.oncanplaythrough = () => {
                    loadingSpinner.style.display = 'none';
                    soundIcon.classList.remove('disabled');
                    soundIcon.classList.add('playing');
                };

                // 音频播放结束时的处理
                currentAudio.onended = () => {
                    URL.revokeObjectURL(audioUrl);
                    soundIcon.classList.remove('playing');
                };

                // 错误处理
                currentAudio.onerror = (error) => {
                    console.error('音频加载失败:', error);
                    soundError.textContent = '音频加载失败';
                    soundError.style.display = 'block';
                    loadingSpinner.style.display = 'none';
                    soundIcon.classList.remove('disabled');
                };

                // 播放音频
                await currentAudio.play();
            } catch (error) {
                console.error('播放失败:', error);
                soundError.textContent = error.message || '发音失败';
                soundError.style.display = 'block';
                loadingSpinner.style.display = 'none';
                soundIcon.classList.remove('disabled');
            }
        }

        // 在获取新词时自动播放
        async function getNewWord(retryCount = 0) {
            const maxRetries = 3;
            const resultDiv = document.getElementById('result');
            const answerInput = document.getElementById('answerInput');

            try {
                // 显示加载状态
                resultDiv.textContent = '加载中...';
                resultDiv.className = 'result';
                answerInput.disabled = true;

                // 检查是否需要获取新词
                if (remainingWords < 5) {
                    await fetchNewWords();
                }

                const response = await fetch(`/get_word?level=${currentLevel}`);
                if (!response.ok) {
                    throw new Error('获取词汇失败');
                }

                const data = await response.json();
                if (data.error) {
                    throw new Error(data.error);
                }

                // 更新当前词汇
                currentWord = data.word;
                currentMode = data.mode;
                remainingWords = data.remaining_words;
                
                // 更新显示
                document.getElementById('chinese').textContent = currentWord.chinese;
                answerInput.value = '';
                answerInput.placeholder = currentMode === 'kana' ? '输入假名' : '输入汉字';
                resultDiv.textContent = '';
                
                // 重新启用输入
                answerInput.disabled = false;
                answerInput.focus();
                
                // 更新统计
                updateStats();

                // 如果启用了自动发音，播放当前词汇
                if (isAutoSoundEnabled()) {
                    setTimeout(() => {
                        playCurrentWord().catch(error => {
                            console.error('自动发音失败:', error);
                        });
                    }, 300);
                }

            } catch (error) {
                console.error('获取新词失败:', error);
                
                if (retryCount < maxRetries) {
                    // 重试
                    console.log(`重试获取新词 (${retryCount + 1}/${maxRetries})...`);
                    resultDiv.textContent = `加载失败，正在重试 (${retryCount + 1}/${maxRetries})...`;
                    setTimeout(() => getNewWord(retryCount + 1), 1000);
                } else {
                    // 达到最大重试次数
                    resultDiv.textContent = '获取词汇失败，请点击任意级别按钮重试';
                    resultDiv.className = 'result incorrect';
                    answerInput.disabled = false;
                    answerInput.placeholder = '暂时无法获取新词';
                }
            }
        }

        async function checkAnswer() {
            const userInput = document.getElementById('answerInput').value;
            const resultDiv = document.getElementById('result');
            
            if (!userInput) return;

            try {
                const response = await fetch('/check_answer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        answer: userInput,
                        word_id: currentWord.id,
                        mode: currentMode,
                        level: currentLevel
                    })
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                const result = await response.json();
                
                if (result.correct) {
                    resultDiv.textContent = '正确！';
                    resultDiv.className = 'result correct';
                    stats.correct++;
                    remainingWords--;
                    setTimeout(getNewWord, 300);
                } else {
                    resultDiv.innerHTML = `错误！<br>正确答案：${result.correct_answer}`;
                    resultDiv.className = 'result incorrect';
                    stats.incorrect++;
                }
                updateStats();
            } catch (error) {
                console.error('提交答案时出错:', error);
                resultDiv.textContent = '网络错误，请重试';
                resultDiv.className = 'result incorrect';
                
                // 启用输入框和回车键，允许用户重试
                const answerInput = document.getElementById('answerInput');
                answerInput.disabled = false;
                answerInput.focus();
            }
        }

        // 级别选择事件处理
        document.querySelectorAll('.level-btn').forEach(button => {
            button.addEventListener('click', async function() {
                const newLevel = this.dataset.level;
                if (newLevel === currentLevel) return;
                
                // 更新按钮状态
                document.querySelector('.level-btn.active').classList.remove('active');
                this.classList.add('active');
                
                // 添加加载状态
                this.classList.add('loading');
                
                // 更新当前级别并重置统计
                currentLevel = newLevel;
                stats.correct = 0;
                stats.incorrect = 0;
                remainingWords = 0;
                
                // 获取新词
                await fetchNewWords();
                await getNewWord();
                
                // 移除加载状态
                this.classList.remove('loading');
                
                updateStats();
            });
        });

        document.getElementById('answerInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') checkAnswer();
        });

        // 初始加载
        fetchNewWords().then(() => getNewWord());
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_word')
def get_word():
    level = request.args.get('level', 'N5')
    refresh = request.args.get('refresh', 'false').lower() == 'true'
    
    # 如果请求刷新或词汇不足，获取新词
    if refresh or len(word_cache[level]) < 5:
        new_words = get_jisho_words(level)
        if new_words:
            word_cache[level].extend(new_words)
            word_cache['last_fetch'][level] = time.time()
    
    words = list(word_cache[level])
    if not words:
        return jsonify({'error': f'No words available for level {level}'}), 404
    
    word = random.choice(words)
    word_id = words.index(word)
    mode = random.choice(['kana', 'kanji'])
    
    return jsonify({
        'word': {
            'id': word_id,
            'chinese': word['chinese'],
            'kanji': word['kanji'],
            'kana': word['kana']
        },
        'mode': mode,
        'remaining_words': len(words)
    })

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    level = data.get('level', 'N5')
    words = list(word_cache[level])
    
    if data['word_id'] >= len(words):
        return jsonify({'error': 'Invalid word ID'}), 400
        
    word = words[data['word_id']]
    mode = data['mode']
    user_answer = data['answer']
    
    correct_answer = word[mode]
    is_correct = user_answer == correct_answer
    
    # 如果答对了，从缓存中移除这个词
    if is_correct and word in word_cache[level]:
        word_cache[level].remove(word)
    
    return jsonify({
        'correct': is_correct,
        'correct_answer': correct_answer,
        'remaining_words': len(word_cache[level])
    })

@app.route('/speak', methods=['POST'])
def speak():
    """处理文本到语音的转换请求"""
    try:
        # 获取请求数据
        data = request.get_json()
        text = data.get('text', '').strip()
        print(f"Received text for speech synthesis: {text}")
        
        # 验证输入
        if not text:
            print("Error: No text provided")
            return jsonify({'error': 'No text provided'}), 400
        
        # 限制文本长度
        if len(text) > 100:
            print("Error: Text too long")
            return jsonify({'error': 'Text too long (max 100 characters)'}), 400

        try:
            # 构建 Google TTS URL
            encoded_text = text.replace(' ', '%20')
            audio_url = f'https://translate.google.com/translate_tts?ie=UTF-8&tl=ja&client=tw-ob&q={encoded_text}'
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # 发送请求获取音频
            response = requests.get(audio_url, headers=headers, timeout=5)
            response.raise_for_status()

            # 检查响应内容类型
            if 'audio/mpeg' not in response.headers.get('Content-Type', ''):
                raise ValueError('Invalid response content type')

            # 返回音频流
            return Response(
                response.content,
                mimetype='audio/mpeg',
                headers={
                    'Content-Disposition': 'attachment; filename=speech.mp3',
                    'Cache-Control': 'no-cache'
                }
            )

        except requests.Timeout:
            print("Error: Request timeout")
            return jsonify({
                'error': 'Speech synthesis timeout',
                'details': 'The request took too long to complete'
            }), 504

        except requests.RequestException as e:
            print(f"Network error: {e}")
            return jsonify({
                'error': 'Network error',
                'details': str(e)
            }), 503

        except Exception as e:
            print(f"Unexpected error: {e}")
            return jsonify({
                'error': 'Internal server error',
                'details': str(e)
            }), 500

    except Exception as e:
        print(f"Request processing error: {e}")
        return jsonify({
            'error': 'Bad request',
            'details': str(e)
        }), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=56459)
                'error': 'Failed to generate speech',
                'details': str(e)
            }), 500

    except Exception as e:
        print(f"Error in speech route: {e}")
        return jsonify({
            'error': 'Failed to process speech request',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=56459)