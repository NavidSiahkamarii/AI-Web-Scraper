import pymysql

def get_connection():
    timeout = 10
    connection = pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db="defaultdb",
        host="data-ai-web-scraper.d.aivencloud.com",
        password="AVNS_vXefrJYtYdAMfKfERON",
        read_timeout=timeout,
        port=10523,
        user="avnadmin",
        write_timeout=timeout,
    )
    return connection
#
# connection = get_connection()
# cursor = connection.cursor()
# cursor.execute("DELETE FROM accounts")
# connection.commit()