from flask import Blueprint, request, jsonify
import os
from datetime import datetime
import json
import requests

ai_bp = Blueprint('ai', __name__)

# 配置Kimi API
KIMI_API_KEY = "sk-O198uTzpdVGH7OaDrBCBoPJbcSKpx6zfmn9IRyPLgbxEIuoT"
KIMI_API_BASE = "https://api.moonshot.cn/v1"

# 简单的AI响应模拟器
class SimpleAI:
    def __init__(self):
        self.responses = {
            '你好': '你好！我是史迪仔的AI助手，很高兴为你服务！🤖',
            'hello': 'Hello! I\'m Stitch\'s AI assistant, nice to meet you! 🤖',
            '帮助': '我可以帮你：\n• 总结和分析笔记内容\n• 提供学习建议和计划\n• 回答各种问题\n• 协助整理思路',
            '总结': '我可以帮你总结笔记内容，请告诉我你想总结哪些笔记。',
            '学习': '学习建议：\n• 制定明确的学习目标\n• 使用番茄钟技术保持专注\n• 定期复习和总结\n• 保持良好的学习习惯',
            '计划': '制定计划的建议：\n• 设定SMART目标（具体、可测量、可达成、相关、有时限）\n• 将大任务分解为小任务\n• 合理安排时间\n• 留出缓冲时间',
            '番茄钟': '番茄钟是一种时间管理技术：\n• 25分钟专注工作\n• 5分钟短休息\n• 每4个番茄钟后长休息15分钟\n\n点击右上角的番茄钟按钮开始使用！🍅',
            '笔记': '关于笔记管理的建议：\n• 使用清晰的标题和标签\n• 定期整理和分类\n• 添加关键词便于搜索\n• 定期回顾重要内容',
        }
        
        self.default_responses = [
            '这是一个很有趣的问题！让我想想... 🤔',
            '根据我的理解，这个问题需要更多的上下文信息。',
            '我建议你可以从以下几个角度来思考这个问题...',
            '这让我想到了一些相关的概念，或许对你有帮助。',
            '很好的问题！我觉得可以这样来分析...',
            '基于你的描述，我有一些想法可以分享。',
        ]
    
    def get_response(self, message, context=None):
        message_lower = message.lower().strip()
        
        # 检查关键词匹配
        for keyword, response in self.responses.items():
            if keyword in message_lower:
                return response
        
        # 特殊处理
        if '总结' in message_lower and '笔记' in message_lower:
            return '我可以帮你总结笔记内容！请告诉我：\n• 你想总结哪个时间段的笔记？\n• 有特定的主题或标签吗？\n• 需要什么样的总结格式？'
        
        if '建议' in message_lower:
            return '我很乐意给你建议！请告诉我更多详细信息：\n• 你遇到了什么具体问题？\n• 你的目标是什么？\n• 你已经尝试过什么方法？'
        
        if '时间' in message_lower or '管理' in message_lower:
            return '时间管理的几个要点：\n• 优先级排序（重要且紧急的事情优先）\n• 使用番茄钟技术保持专注\n• 避免多任务处理\n• 定期休息和反思\n\n你可以尝试使用我们的番茄钟功能！'
        
        if '学习方法' in message_lower or '如何学习' in message_lower:
            return '高效学习方法推荐：\n• 主动学习：提问、总结、教授他人\n• 间隔重复：定期复习已学内容\n• 费曼技巧：用简单语言解释复杂概念\n• 思维导图：可视化知识结构\n• 实践应用：将理论与实际结合'
        
        # 默认响应
        import random
        return random.choice(self.default_responses) + '\n\n如果你有具体的问题，请详细描述，我会尽力帮助你！'

simple_ai = SimpleAI()

@ai_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        context = data.get('context', [])
        
        if not message:
            return jsonify({
                'error': '消息不能为空'
            }), 400
        
        # 记录聊天日志
        chat_log = {
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'context_length': len(context) if context else 0
        }
        
        # 获取AI响应
        try:
            # 优先使用Kimi API
            print(f"尝试调用Kimi API，消息: {message[:50]}...")
            response = get_kimi_response(message, context)
            print(f"Kimi API响应成功: {response[:50]}...")
            
        except Exception as ai_error:
            print(f"Kimi API调用失败，错误详情: {str(ai_error)}")
            print(f"错误类型: {type(ai_error).__name__}")
            # 如果Kimi API失败，回退到模拟响应
            try:
                print("使用模拟响应...")
                response = simple_ai.get_response(message, context)
                print(f"模拟响应成功: {response[:50]}...")
            except Exception as fallback_error:
                print(f"模拟响应也失败: {fallback_error}")
                response = "抱歉，我现在遇到了一些技术问题，请稍后再试。"
        
        chat_log['ai_response'] = response
        
        # 可以选择将聊天记录保存到数据库
        # save_chat_log(chat_log)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"AI聊天接口错误: {e}")
        return jsonify({
            'error': '服务器内部错误',
            'response': '抱歉，我现在无法正常工作，请稍后再试。'
        }), 500

@ai_bp.route('/suggestions', methods=['POST'])
def get_suggestions():
    """获取基于笔记内容的建议"""
    try:
        data = request.get_json()
        notes = data.get('notes', [])
        suggestion_type = data.get('type', 'general')  # general, study, organize
        
        suggestions = []
        
        if suggestion_type == 'study':
            suggestions = [
                "建议使用番茄钟技术，25分钟专注学习，5分钟休息",
                "定期回顾和总结学过的内容，加深记忆",
                "尝试用自己的话重新表述学到的概念",
                "制作思维导图来整理知识结构"
            ]
        elif suggestion_type == 'organize':
            suggestions = [
                "为笔记添加清晰的标签和分类",
                "定期整理和归档旧笔记",
                "使用统一的笔记格式和结构",
                "创建笔记索引便于快速查找"
            ]
        else:
            suggestions = [
                "保持每日记录的习惯",
                "定期回顾和反思",
                "设定明确的学习目标",
                "合理安排时间和任务优先级"
            ]
        
        return jsonify({
            'suggestions': suggestions,
            'type': suggestion_type,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"获取建议错误: {e}")
        return jsonify({
            'error': '获取建议失败'
        }), 500

@ai_bp.route('/polish', methods=['POST'])
def polish_text():
    """AI文本润色功能"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'error': '文本内容不能为空'
            }), 400
        
        # 构建润色提示
        polish_prompt = f"请帮我润色以下文本，使其更加流畅、准确、有条理。保持原意不变，但提升表达质量：\n\n{text}"
        
        try:
            # 使用Kimi API进行润色
            polished_text = get_kimi_response(polish_prompt)
            
            return jsonify({
                'original_text': text,
                'polished_text': polished_text,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as ai_error:
            print(f"AI润色失败: {ai_error}")
            return jsonify({
                'error': 'AI润色服务暂时不可用，请稍后再试',
                'original_text': text
            }), 500
        
    except Exception as e:
        print(f"文本润色错误: {e}")
        return jsonify({
            'error': '文本润色失败'
        }), 500

@ai_bp.route('/generate-tags', methods=['POST'])
def generate_tags():
    """AI标签生成功能"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({
                'error': '内容不能为空'
            }), 400
        
        # 构建标签生成提示
        tag_prompt = f"请为以下内容生成3-5个相关的标签，标签应该简洁明了，能够概括内容的主要主题。请只返回标签，用逗号分隔：\n\n{content}"
        
        try:
            # 使用Kimi API生成标签
            tags_response = get_kimi_response(tag_prompt)
            
            # 解析标签
            tags = [tag.strip() for tag in tags_response.split(',') if tag.strip()]
            
            return jsonify({
                'content': content,
                'tags': tags,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as ai_error:
            print(f"AI标签生成失败: {ai_error}")
            return jsonify({
                'error': 'AI标签生成服务暂时不可用，请稍后再试',
                'content': content
            }), 500
        
    except Exception as e:
        print(f"标签生成错误: {e}")
        return jsonify({
            'error': '标签生成失败'
        }), 500

def get_kimi_response(message, context=None):
    """使用Kimi API获取响应"""
    try:
        messages = [
            {
                "role": "system",
                "content": "你是史迪仔笔记应用的AI助手。你的任务是帮助用户管理笔记、提供学习建议、回答问题。请用友好、有帮助的语气回答，并尽量提供实用的建议。"
            }
        ]
        
        # 添加上下文
        if context:
            for ctx in context[-4:]:  # 只保留最近4轮对话
                if ctx['type'] == 'user':
                    messages.append({"role": "user", "content": ctx['content']})
                elif ctx['type'] == 'ai':
                    messages.append({"role": "assistant", "content": ctx['content']})
        
        # 添加当前消息
        messages.append({"role": "user", "content": message})
        
        # 调用Kimi API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {KIMI_API_KEY}"
        }
        
        data = {
            "model": "moonshot-v1-8k",
            "messages": messages,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(
            f"{KIMI_API_BASE}/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            print(f"Kimi API错误: {response.status_code} - {response.text}")
            raise Exception(f"Kimi API调用失败: {response.status_code}")
        
    except Exception as e:
        print(f"Kimi API错误: {e}")
        raise e

def save_chat_log(chat_log):
    """保存聊天记录到文件（可选）"""
    try:
        log_file = 'chat_logs.jsonl'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(chat_log, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"保存聊天记录错误: {e}")