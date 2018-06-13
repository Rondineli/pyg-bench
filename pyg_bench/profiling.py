from redis_queue import RedisQueue

from sqlalchemy import event
from sqlalchemy.engine import Engine
import time

queue_data = RedisQueue(
    name="data_count",
    namespace="data_count"
)


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement,
                          parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement,
                         parameters, context, executemany):

    type_statement = ""

    if "SELECT" in statement.upper():
        type_statement = "select"

    if "UPDATE" in statement.upper():
        type_statement = "update"

    if "INSERT" in statement.upper():
        type_statement = "insert"

    total = time.time() - conn.info['query_start_time'].pop(-1)

    queue_data.put({
        "type": type_statement,
        "total_seconds": total
    })
