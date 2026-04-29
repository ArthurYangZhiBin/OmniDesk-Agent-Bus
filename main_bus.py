from openai import OpenAI
from router_agent import RouterAgent
from rag_agent import KnowledgeRAGAgent
from action_agent import ActionAgent
from ticket_mq_publisher import RabbitMQTicketPublisher

def run_omnidesk_bus():
    # 初始化你的 OpenAI Client
    client = OpenAI(api_key="sk-xxxxxx") # 替换为真实 API Key
    
    router = RouterAgent(client)
    rag_agent = KnowledgeRAGAgent(client)
    action_agent = ActionAgent(client)
    mq_publisher = RabbitMQTicketPublisher()

    print("=== 欢迎使用企业智能 IT/HR 服务总线 (输入 'quit' 退出) ===")
    
    chat_history = []
    
    while True:
        user_input = input("\n员工: ")
        if user_input.lower() == 'quit':
            break
            
        chat_history.append({"role": "user", "content": user_input})
        
        # 1. 中枢 Agent 进行意图识别
        print("[总线日志] 正在进行意图路由...")
        routing_result = router.analyze_intent(user_input)
        intent = routing_result.get("intent")
        
        # 2. 根据意图分发任务
        if intent == "knowledge_query":
            print("[总线日志] 路由至 -> RAG 知识库 Agent")
            reply = rag_agent.handle_query(user_input)
            print(f"\n智能助理: {reply}")
            chat_history.append({"role": "assistant", "content": reply})
            
        elif intent == "action_ticket":
            print("[总线日志] 路由至 -> 动作执行 Agent")
            result = action_agent.process_ticket_request(chat_history)
            
            if result["status"] == "need_more_info":
                # Agent 认为信息不全，主动追问
                reply = result["reply"]
                print(f"\n智能助理: {reply}")
                chat_history.append({"role": "assistant", "content": reply})
                
            elif result["status"] == "ready_to_execute":
                # Agent 提取到了所有关键参数，准备执行
                payload = result["payload"]
                print(f"\n[总线日志] 槽位收集完毕，准备调用 API: {payload}")
                
                # 3. 投递到 RabbitMQ 进行异步工单创建
                ticket_id = mq_publisher.publish_ticket(payload)
                
                final_reply = f"已为您自动提交故障报修！工单号：{ticket_id}。请耐心等待 IT 人员联系您。"
                print(f"\n智能助理: {final_reply}")
                chat_history.append({"role": "assistant", "content": final_reply})
        else:
            print("\n智能助理: 抱歉，我没有理解您的需求，请尝试重新描述。")

if __name__ == "__main__":
    # 提示：运行前确保本地 RabbitMQ 已启动 (例如通过 Docker: docker run -p 5672:5672 rabbitmq)
    # 并且已配置好 OpenAI 环境变量或传入 API_KEY
    run_omnidesk_bus()
