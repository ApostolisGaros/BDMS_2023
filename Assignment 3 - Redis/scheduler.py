import redis
from datetime import datetime
import time

from program import end_meeting

# Connect to Redis
redis_db = redis.Redis(host="localhost", port=6379, decode_responses=True, db=0)


def activate_meeting_instances():
    current_time = datetime.now()

    meeting_instances = redis_db.keys("meeting_instance:*")
    for instance_key in meeting_instances:
        instance = redis_db.hgetall(instance_key)
        from_datetime = datetime.fromisoformat(instance["fromdatetime"])
        to_datetime = datetime.fromisoformat(instance["todatetime"])
        is_active = instance["isActive"] == "True"
        instance_id = instance_key.split(":")[-1]

        if is_active and current_time > to_datetime:
            # Deactivate meeting instance
            print("Deactivating meeting instance: ", instance_id)
            end_meeting(instance_id)
        elif (
            not is_active
            and current_time >= from_datetime
            and current_time <= to_datetime
        ):
            # Activate meeting instance
            print("Activating meeting instance: ", instance_id)
            redis_db.hset(instance_key, "isActive", "True")

    print("Scan finished.\n")


def scheduler():
    while True:
        print(time.ctime())
        activate_meeting_instances()

        # Sleep for 1 minute
        time.sleep(60)


# Call the scheduler function
scheduler()
