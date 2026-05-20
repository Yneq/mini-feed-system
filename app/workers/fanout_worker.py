import json
import time

from app.core.redis import redis_client
from app.core.database import SessionLocal
from app.models.user import Follow

db = SessionLocal()

print("🚀 Fanout worker started...")

while True:

    # blocking pop
    task = redis_client.brpop("post_queue", timeout=0)

    if task:
        _, data = task

        payload = json.loads(data)

        post_id = payload["post_id"]
        user_id = payload["user_id"]
        score = payload["score"]

        print(f"Processing post {post_id}")

        followers = db.query(Follow).filter(
            Follow.follow_id == user_id
        ).all()

        # fan-out
        for f in followers:

            redis_client.zadd(
                f"feed:user:{f.user_id}",
                {post_id: score}
            )

            # trimming
            redis_client.zremrangebyrank(
                f"feed:user:{f.user_id}",
                0,
                -1001
            )

        # 自己
        redis_client.zadd(
            f"feed:user:{user_id}",
            {post_id: score}
        )

        redis_client.zremrangebyrank(
            f"feed:user:{user_id}",
            0,
            -1001
        )

        print(f"Done post {post_id}")