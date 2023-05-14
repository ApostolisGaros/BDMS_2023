import redis
import json
from datetime import datetime

# Suppress warnings
import warnings

warnings.filterwarnings("ignore")

# Connect to Redis
redis_db = redis.Redis(host="localhost", port=6379, decode_responses=True, db=0)


def check_user_in_meeting(user_id, meeting_instance_id):
    # select the main database
    redis_db.select(1)
    event_id = redis_db.get("event_id")

    # Check if the user has joined the meeting and is still in the meeting
    events = redis_db.keys(
        f"event:*:userID:{user_id}:meetingInstanceID:{meeting_instance_id}:event_type:join_meeting"
    )

    if not events:
        return False

    for event_key in events:
        keys = redis_db.keys(
            f"event:*:userID:{user_id}:meetingInstanceID:{meeting_instance_id}:event_type:*"
        )
        userEvents = []
        for key in keys:
            userEvents.append(redis_db.hgetall(key))

        # sort the events by timestamp
        userEvents.sort(key=lambda x: x["timestamp"])
        if userEvents[-1]["event_type"] == "join_meeting":
            return True

    return False


def join_meeting(user_id, meeting_instance_id):
    # select the main database
    redis_db.select(0)

    user = redis_db.hgetall(f"user:{user_id}")
    if not user:
        return "Invalid user ID"

    user_email = user["email"]

    meeting_instance = redis_db.hgetall(f"meeting_instance:{meeting_instance_id}")

    if not meeting_instance:
        return "Invalid meeting instance ID"

    # check if the meeting instance is active
    is_active = meeting_instance["isActive"] == "True"
    if not is_active:
        return "Meeting instance is not active"

    meeting_id = meeting_instance["meetingID"]
    meeting = redis_db.hgetall(f"meeting:{meeting_id}")
    if not meeting:
        return "Invalid meeting ID"

    is_public = meeting["isPublic"] == "True"
    audience = json.loads(meeting["audience"])

    if is_public or user_email in audience:
        # Check if the user has joined the meeting
        if check_user_in_meeting(user_id, meeting_instance_id):
            return "User is already in the meeting"

        # Update event log
        redis_db.select(1)
        event_id = redis_db.incr("event_id")
        event = {
            "eventID": event_id,
            "userID": user_id,
            "meetingInstanceID": meeting_instance_id,
            "event_type": "join_meeting",
            "timestamp": datetime.now().isoformat(),
        }

        redis_db.hmset(
            f"event:{event_id}:userID:{user_id}:meetingInstanceID:{meeting_instance_id}:event_type:join_meeting",
            event,
        )
        # select the main database
        redis_db.select(0)

        return f"User {user_id} successfully joined meeting"

    return f"User {user_id} not allowed to join the meeting"


def leave_meeting(user_id, meeting_instance_id):
    # select the main database
    redis_db.select(1)
    event_id = redis_db.get("event_id")

    # Check if the user has joined the meeting
    # Get the event log
    joined_arr = redis_db.keys(
        f"event:*:userID:{user_id}:meetingInstanceID:{meeting_instance_id}:event_type:join_meeting"
    )

    if joined_arr:
        still_online = check_user_in_meeting(user_id, meeting_instance_id)
        if still_online == False:
            return "User has already left the meeting"

        # Update event log
        redis_db.select(1)
        event_id = redis_db.incr("event_id")
        event = {
            "eventID": event_id,
            "userID": user_id,
            "meetingInstanceID": meeting_instance_id,
            "event_type": "leave_meeting",
            "timestamp": datetime.now().isoformat(),
        }
        redis_db.hmset(
            f"event:{event_id}:userID:{user_id}:meetingInstanceID:{meeting_instance_id}:event_type:leave_meeting",
            event,
        )
        redis_db.select(0)

        return "User successfully left the meeting"

    return "User has not joined the meeting"


def show_current_participants(meeting_instance_id):
    # select the main database
    redis_db.select(0)
    participants = []

    meeting_instance = redis_db.keys(f"meeting_instance:{meeting_instance_id}")
    if meeting_instance == []:
        return "Invalid meeting instance ID"

    # select the event database
    redis_db.select(1)

    events = redis_db.keys(
        f"event:*:userID:*:meetingInstanceID:{meeting_instance_id}:event_type:join_meeting"
    )

    usersChecked = {}

    for event_key in events:
        participant_id = int(event_key.split(":")[3])
        if participant_id in usersChecked:
            continue
        usersChecked[participant_id] = True

        # check if participant has left the meeting
        user_still_in_meeting = check_user_in_meeting(
            participant_id, meeting_instance_id
        )
        if user_still_in_meeting:
            participants.append(participant_id)

    return participants


def show_active_meetings():
    # select the main database
    redis_db.select(0)
    active_meetings = []
    meeting_instances = redis_db.keys("meeting_instance:*")
    for instance_key in meeting_instances:
        # instance = redis_db.hgetall(instance_key)
        instance = redis_db.hmget(instance_key, ["isActive", "meetingID"])
        if instance[0] == "True":
            meeting_id = int(instance[1])
            active_meetings.append(meeting_id)

    return active_meetings


def end_meeting(meeting_instance_id):
    # select the main database
    redis_db.select(0)

    # check if meeting instance exists
    meeting_instance = redis_db.hgetall(f"meeting_instance:{meeting_instance_id}")
    if not meeting_instance:
        return "Invalid meeting instance ID"

    # check if meeting instance is active
    if meeting_instance["isActive"] == "False":
        return "Meeting instance is not active"

    participants = show_current_participants(meeting_instance_id)
    # event for each participant leaving the meeting
    for participant in participants:
        leave_meeting(participant, meeting_instance_id)

    # Update event log
    redis_db.select(1)

    event_id = redis_db.incr("event_id")
    event = {
        "eventID": event_id,
        "meetingInstanceID": meeting_instance_id,
        "event_type": "timeout",
        "timestamp": datetime.now().isoformat(),
    }
    redis_db.hmset(f"event:{event_id}", event)
    redis_db.select(0)

    # Deactivate the meeting instance
    redis_db.hset(f"meeting_instance:{meeting_instance_id}", "isActive", "False")

    return f"Meeting instance {meeting_instance_id} ended"


def post_chat_message(user_id, meeting_instance_id, message):
    # select the main database
    redis_db.select(0)

    # check if meeting instance exists
    meeting_instance = redis_db.hgetall(f"meeting_instance:{meeting_instance_id}")
    if not meeting_instance:
        return "Invalid meeting instance ID"

    # check if user has joined the meeting
    user_joined = check_user_in_meeting(user_id, meeting_instance_id)
    if not user_joined:
        return "User is not in the meeting"

    # check if meeting instance is active
    if meeting_instance["isActive"] == "False":
        return "Meeting instance is not active"

    message_id = redis_db.incr("message_id")
    chat_message = {
        "messageID": message_id,
        "userID": user_id,
        "meetingInstanceID": meeting_instance_id,
        "message": message,
        "timestamp": datetime.now().isoformat(),
    }
    redis_db.select(0)
    redis_db.hmset(f"chat_message:{message_id}", chat_message)

    return "Chat message posted"


def get_chat_messages(meeting_instance_id):
    # select the main database
    redis_db.select(0)

    # check if meeting instance exists
    meeting_instance = redis_db.hgetall(f"meeting_instance:{meeting_instance_id}")
    if not meeting_instance:
        return "Invalid meeting instance ID"

    chat_messages = []
    messages = redis_db.keys(f"chat_message:*")

    for message_key in messages:
        message = redis_db.hgetall(message_key)
        if message["meetingInstanceID"] == str(meeting_instance_id):
            chat_messages.append(message)

    chat_messages.sort(key=lambda x: x["timestamp"])
    return chat_messages


def get_participant_join_time(meeting_instance_id):
    # select the main database
    redis_db.select(0)

    # check if meeting instance exists
    meeting_instance = redis_db.hgetall(f"meeting_instance:{meeting_instance_id}")
    if not meeting_instance:
        return "Invalid meeting instance ID"

    # check if meeting instance is active
    if meeting_instance["isActive"] == "False":
        return "Meeting instance is not active"

    participants = show_current_participants(meeting_instance_id)

    # select the event database
    redis_db.select(1)

    participants_join_time = {}

    for participant in participants:
        events = redis_db.keys(
            f"event:*:userID:{participant}:meetingInstanceID:{meeting_instance_id}:event_type:join_meeting"
        )
        join_events = []
        for event_key in events:
            event = redis_db.hgetall(event_key)
            join_events.append(event)

        join_events.sort(key=lambda x: x["timestamp"])
        participants_join_time[participant] = join_events[-1]["timestamp"]

    return participants_join_time


def get_user_messages(meeting_instance_id, user_id):
    # select the main database
    redis_db.select(0)

    # check if meeting instance exists
    meeting_instance = redis_db.hgetall(f"meeting_instance:{meeting_instance_id}")
    if not meeting_instance:
        return "Invalid meeting instance ID"

    messages = []

    message_keys = redis_db.keys(f"chat_message:*")

    for message_key in message_keys:
        message = redis_db.hgetall(message_key)
        if message["meetingInstanceID"] == str(meeting_instance_id) and message[
            "userID"
        ] == str(user_id):
            messages.append(message)

    messages.sort(key=lambda x: x["timestamp"])

    return messages
