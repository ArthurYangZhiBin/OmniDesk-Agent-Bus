import json
from openai import OpenAI

class RouterAgent:
    def __init__(self, client: OpenAI):
        self.client = client

    def analyze_intent(self, user_query: str) -> dict:
        """
        对用户输入进行意图识别与路由分发
        """
        prompt = f"""
        你是一个企业内部 IT/HR 服务总线的路由中枢。
        请分析以下用户输入，并严格输出 JSON 格式的结果。
        
        可选意图 (intent) 只能是以下两种：
        1. "knowledge_query": 流程咨询、政策解读（如HR休假规定、IT报销流程）。
        2. "action_ticket": 故障报修、权限申请等需要人为介入或系统操作的（如电脑蓝屏、申请VPN）。
        
        用户输入: "{user_query}"
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",  # 实际开发中可替换为具体模型
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1 # 路由任务需要确定性，调低温度
        )
        
        return json.loads(response.choices[0].message.content)

# 测试示例
# client = OpenAI(api_key="your_key")
# router = RouterAgent(client)
# print(router.analyze_intent("我的 MacBook 突然死机了，开不了机"))
# 输出: {'intent': 'action_ticket', 'reason': '用户报告设备故障，需要报修'}
