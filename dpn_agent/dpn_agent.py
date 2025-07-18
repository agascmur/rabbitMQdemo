import pika
import time
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

channel.queue_declare(queue='fitxes_to_process', durable=True)  # Crea la cua durable sense necessitat de tenir productors declarats

def processa_fitxa(fitxa):
    print(f"⚙️  Processant fitxa: {fitxa['fitxa_id']}")
    #time.sleep(2)
    x = {
        "fitxa_id": fitxa["fitxa_id"],
        "status": "OK",
        "timestamp_confirmat": fitxa["timestamp"],
        "detall": "Fitxa processada i guardada correctament"
    }
    print(x)
    return x

def on_request(ch, method, props, body):
    fitxa = json.loads(body)
    resposta = processa_fitxa(fitxa)

    channel.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(resposta)
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='fitxes_to_process', on_message_callback=on_request)

print("🟥 DPN Agent esperant fitxes...")
channel.start_consuming()
