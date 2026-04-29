from openai import OpenAI
import json

class ActionAgent:
    def __init__(self, client: OpenAI):
        self.client = client
        # 预设必须收集的槽位 (Slots)
        self.required_info = ["fault_description", "device_mac_address"]

    def process_ticket_request(self, chat_history: list) -> dict:
        """
        利用大模型的函数调用 (Function Calling) 能力来判断是否该提单了
        """
        tools = [{
            "type": "function",
            "function": {
                "name": "create_it_ticket",
                "description": "当且仅当用户明确提供了故障现象 AND 设备的MAC地址后，调用此函数创建工单。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fault_description": {"type": "string", "description": "故障详细描述"},
                        "device_mac_address": {"type": "string", "description": "设备的MAC地址，如 AA:BB:CC:11:22:33"}
                    },
                    "required": ["fault_description", "device_mac_address"]
                }
            }
        }]

        system_msg = {"role": "system", "content": "你是IT支持助手。要报修设备，你必须向用户收集'故障描述'和'MAC地址'。缺一不可。如果不全，请温和地询问用户。"}
        messages = [system_msg] + chat_history

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message
        
        # 判断大模型是否决定调用创建工单的 Tool
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            return {"status": "ready_to_execute", "payload": args}
        else:
            # 信息不全，大模型回复的追问话术
            return {"status": "need_more_info", "reply": message.content}
