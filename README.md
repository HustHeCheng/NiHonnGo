# NiHonnGo - 日语学习网站

一个简单而高效的日语学习网站，帮助用户通过交互式练习掌握日语词汇。

## 主要功能

1. **多源词汇获取**
   - 集成 EDICT/JMdict 日语词典数据库
   - 备用 Jisho API 支持
   - 自动刷新词库
   - 智能缓存管理
   - 离线词典支持

2. **多级别支持**
   - N5 (基础) 到 N1 (高级) 的 JLPT 词汇
   - 每个级别独立的进度跟踪
   - 自适应难度

3. **发音功能**
   - 自动发音开关
   - 点击播放功能
   - 使用 Google TTS 进行准确发音

4. **学习功能**
   - 假名/汉字输入模式
   - 即时反馈
   - 进度统计
   - 错误提示

5. **用户体验**
   - 简洁的界面设计
   - 实时进度显示
   - 错误处理和自动重试
   - 加载状态提示

## 技术特点

- Flask 后端
- 原生 JavaScript 前端
- RESTful API 设计
- 实时词汇获取和缓存
- 错误处理和重试机制
- 响应式设计

## 使用说明

1. 选择合适的 JLPT 级别
2. 查看中文提示词
3. 输入对应的日语（假名或汉字）
4. 获得即时反馈
5. 跟踪学习进度

## 开发环境

- Python 3.x
- Flask
- Requests
- Google TTS