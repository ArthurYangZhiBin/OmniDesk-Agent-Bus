import pika
import json
import uuid

class RabbitMQTicketPublisher:
    def __init__(self, host='localhost'):
        self.host = host
        self.queue_name = 'it_support_tickets'

    def publish_ticket(self, payload: dict):
        """将结构化的工单数据发送到 RabbitMQ"""
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
            channel = connection.channel()
            
            # 声明队列，确保队列存在
            channel.queue_declare(queue=self.queue_name, durable=True)
            
            # 丰富工单信息
            ticket_data = {
                "ticket_id": f"IT-{uuid.uuid4().hex[:8].upper()}",
                "source": "Agent_Bus",
                "details": payload
            }
            
            channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(ticket_data),
                properties=pika.BasicProperties(
                    delivery_mode=pika.DeliveryMode.Persistent # 消息持久化
                )
            )
            print(f"[RabbitMQ] 成功将工单投递到队列: {ticket_data['ticket_id']}")
            connection.close()
            return ticket_data['ticket_id']
        except Exception as e:
            print(f"[RabbitMQ报错] 消息投递失败: {e}")
            return None
