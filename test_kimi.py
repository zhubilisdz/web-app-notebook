import requests
import json

# 测试Kimi API连接
KIMI_API_KEY = "sk-O198uTzpdVGH7OaDrBCBoPJbcSKpx6zfmn9IRyPLgbxEIuoT"
KIMI_API_BASE = "https://api.moonshot.cn/v1"

def test_kimi_api():
    try:
        # 测试获取模型列表
        headers = {
            "Authorization": f"Bearer {KIMI_API_KEY}"
        }
        
        print("测试Kimi API连接...")
        response = requests.get(f"{KIMI_API_BASE}/models", headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        
        if response.status_code == 200:
            print("\n✅ API连接成功")
            
            # 测试聊天接口
            print("\n测试聊天接口...")
            chat_data = {
                "model": "moonshot-v1-8k",
                "messages": [
                    {"role": "user", "content": "你好"}
                ],
                "max_tokens": 100
            }
            
            chat_response = requests.post(
                f"{KIMI_API_BASE}/chat/completions",
                headers={**headers, "Content-Type": "application/json"},
                json=chat_data,
                timeout=30
            )
            
            print(f"聊天接口状态码: {chat_response.status_code}")
            if chat_response.status_code == 200:
                result = chat_response.json()
                print(f"聊天响应: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
                print("\n✅ 聊天接口正常")
            else:
                print(f"聊天接口错误: {chat_response.text}")
        else:
            print(f"\n❌ API连接失败: {response.text}")
            
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

if __name__ == "__main__":
    test_kimi_api()