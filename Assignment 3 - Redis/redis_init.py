import redis
import json

# Suppress warnings
import warnings

warnings.filterwarnings("ignore")

# Connect to Redis
redis_db = redis.Redis(host="localhost", decode_responses=True, port=6379, db=0)


def initialize_redis():
    # Clear existing data
    redis_db.flushall()

    # Sample Users
    users = [
        {
            "userID": 1,
            "name": "John Doe",
            "age": 25,
            "gender": "Male",
            "email": "john.doe@example.com",
        },
        {
            "userID": 2,
            "name": "Jane Smith",
            "age": 30,
            "gender": "Female",
            "email": "jane.smith@example.com",
        },
    ]

    # Sample Meetings
    meetings = [
        {
            "meetingID": 1,
            "title": "Team Standup",
            "description": "Daily standup meeting for the team",
            "isPublic": "True",
            "audience": "[]",
        },
        {
            "meetingID": 2,
            "title": "Product Demo",
            "description": "Demo of new product features",
            "isPublic": "False",
            "audience": json.dumps(["john.doe@example.com"]),
        },
    ]

    # Sample Meeting Instances
    meeting_instances = [
        {
            "meetingInstanceID": 1,
            "meetingID": 1,
            "fromdatetime": "2023-05-08T10:00:00",
            "todatetime": "2023-05-08T11:00:00",
            "isActive": "False",
        },
        {
            "meetingInstanceID": 2,
            "meetingID": 2,
            "fromdatetime": "2023-05-08T14:00:00",
            "todatetime": "2023-05-08T15:00:00",
            "isActive": "True",
        },
    ]

    # Sample Event Logs
    event_logs = [
        # {
        #     'eventID': 1,
        #     'userID': 1,
        #     'meetingInstanceID': 1,
        #     'event_type': 'join_meeting',
        #     'timestamp': '2023-05-08T10:05:00'
        # },
        # {
        #     'eventID': 2,
        #     'userID': 2,
        #     'meetingInstanceID': 1,
        #     'event_type': 'join_meeting',
        #     'timestamp': '2023-05-08T10:07:00'
        # },
        # {
        #     'eventID': 3,
        #     'userID': 1,
        #     'meetingInstanceID': 1,
        #     'event_type': 'leave_meeting',
        #     'timestamp': '2023-05-08T10:30:00'
        # }
    ]

    # Sample Chat Messages
    chat_messages = [
        {
            "messageID": 1,
            "userID": 1,
            "meetingInstanceID": 1,
            "message": "Hello, everyone!",
            "timestamp": "2023-05-08T10:10:00",
        },
        {
            "messageID": 2,
            "userID": 2,
            "meetingInstanceID": 1,
            "message": "Hi, John!",
            "timestamp": "2023-05-08T10:12:00",
        },
    ]

    # DB 0 is used for the main database
    redis_db.select(0)

    # Initialize Users
    for user in users:
        redis_db.hmset(f'user:{user["userID"]}', user)

    # Initialize Meetings
    for meeting in meetings:
        redis_db.hmset(f'meeting:{meeting["meetingID"]}', meeting)

    # Initialize Meeting Instances
    for instance in meeting_instances:
        redis_db.hmset(f'meeting_instance:{instance["meetingInstanceID"]}', instance)

    # Initialize Chat Messages
    for message in chat_messages:
        redis_db.hmset(f'chat_message:{message["messageID"]}', message)

    # DB 1 is used for the event logs

    redis_db.select(1)
    # Initialize Event Logs
    for event in event_logs:
        redis_db.hmset(f'event:{event["eventID"]}', event)

    print("Redis initialized with sample data.")


# Call init funciton
initialize_redis()
