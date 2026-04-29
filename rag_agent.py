from openai import OpenAI

class KnowledgeRAGAgent:
    def __init__(self, client: OpenAI):
        self.client = client

    def _retrieve_context(self, query: str) -> str:
        """模拟多跳检索 (Multi-hop Retrieval) 获取内部规章制度"""
        # 实际项目中，这里是 Embedding + 向量数据库查询的代码
        print(f"[RAG模块] 正在企业知识库中检索与 '{query}' 相关的制度...")
        return "《2026年企业IT设备管理办法》：员工非人为损坏的电脑设备维修，请提交MAC地址并在报修单选择'硬件故障'，将由IT部在2小时内响应并提供备用机。"

    def handle_query(self, query: str) -> str:
        context = self._retrieve_context(query)
        
        system_prompt = f"""
        你是一个企业 HR/IT 政策咨询专家。请严格基于以下内部知识库内容回答员工问题。
        如果知识库中没有相关信息，请明确告知，不要编造。
        
        【知识库上下文】
        {context}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
        )
        return response.choices[0].message.content
