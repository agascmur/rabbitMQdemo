import pika, uuid, json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()

callback_queue = 'scraper_callback_queue'
channel.queue_declare(queue=callback_queue, durable=True)
channel.queue_declare(queue='fitxes_to_process', durable=True)  # Crea la cua durable sense necessitat de tenir consumidors declarats

NUM_MESSAGES = 100000
corr_ids = []
responses = {}

def on_response(ch, method, props, body):
    if props.correlation_id in corr_ids:
        resposta = json.loads(body)
        print(f"✅ Resposta rebuda per {props.correlation_id}:")
        print(json.dumps(resposta, indent=2))
        responses[props.correlation_id] = resposta
        if len(responses) == NUM_MESSAGES:
            print("🎉 Totes les respostes rebudes!")
            connection.close()

channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)

for i in range(NUM_MESSAGES):
    fitxa = {
        "fitxa_id": f"DPN-{1000+i}",
        "timestamp": "2025-07-15T09:42:00Z",
        "tipus": "DPN",
        "contingut": {
            "DPN1": f"DATA-{i}-1",
            "DPN2": f"DATA-{i}-2",
            "DPN3": f"DATA-{i}-3",
            "DPN4": f"DATA-{i}-4"
        }
    }
    corr_id = str(uuid.uuid4())
    corr_ids.append(corr_id)
    channel.basic_publish(
        exchange='',
        routing_key='fitxes_to_process',
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id,
            delivery_mode=2
        ),
        body=json.dumps(fitxa)
    )
    print(f"📤 Fitxa enviada amb corr_id {corr_id}")

print("Esperant respostes...")
channel.start_consuming()
