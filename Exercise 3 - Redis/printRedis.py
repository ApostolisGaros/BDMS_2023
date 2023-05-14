import redis

# Connect to Redis
r = redis.Redis(host='localhost', decode_responses=True, port=6379, db=0)


def print_users():
    r.select(0)  # Select the user database

    users = r.keys('user:*')
    print("Users:")
    for user_key in users:
        user_id = user_key.split(':')[1]
        user_data = r.hgetall(user_key)
        print(f"User ID: {user_id}")
        for field, value in user_data.items():
            print(f"    {field}: {value}")

        print()


def print_meetings():
    r.select(0)  # Select the meeting database

    meetings = r.keys('meeting:*')
    print("Meetings:")
    for meeting_key in meetings:
        meeting_id = meeting_key.split(':')[1]
        meeting_data = r.hgetall(meeting_key)
        print(f"Meeting ID: {meeting_id}")
        for field, value in meeting_data.items():
            print(f"    {field}: {value}")
        print()


def print_meeting_instances():
    r.select(0)  # Select the meeting instance database

    instances = r.keys('meeting_instance:*')
    print("Meeting Instances:")
    for instance_key in instances:
        instance_id = instance_key.split(':')[1]
        instance_data = r.hgetall(instance_key)
        print(f"Instance ID: {instance_id}")
        for field, value in instance_data.items():
            print(f"    {field}: {value}")
        print()

def print_chat_messages():
    r.select(0)  # Select the chat messages database

    chat_messages = r.keys('chat_message:*')
    print("Chat Messages:")
    for message_key in chat_messages:
        message_id = message_key.split(':')[1]
        message_data = r.hgetall(message_key)
        print(f"Message ID: {message_id}")
        for field, value in message_data.items():
            print(f"    {field}: {value}")
        print()



def print_events():
    r.select(1)  # Select the events database

    events = r.keys('event:*')
    print("Events:")
    for event_key in events:
        event_id = event_key.split(':')[1]
        event_data = r.hgetall(event_key)
        print(f"Event ID: {event_id}")
        for field, value in event_data.items():
            print(f"    {field}: {value}")
        print()
    r.select(0)  # Select the main database


# Call the print functions
print_users()
print_meetings()
print_meeting_instances()
print_chat_messages()
print_events()
