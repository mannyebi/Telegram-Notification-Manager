import psycopg2
import os
import logging

logger = logging.getLogger(__name__)


async def get_connection():
    """Connect to postgresql database
    """
    try:
        connection = psycopg2.connect(
            user = os.getenv("db_user"),
            password = os.getenv("db_password"),
            host = os.getenv("db_host"),
            port = os.getenv("db_port"),
            dbname =os.getenv("db_dbname")
        )
        logger.info('successfull connection with database')
        return connection
    except Exception as e:
        logger.exception('connection failed with database -> %s', e)




async def execute_query(query: str, values: tuple, fetch: bool):
    """Executes a SQL query with provided values asynchronously.

    Args:
        query (str): The SQL query to execute.
        values (list): A list of values to be used in the query parameters.
        fetch (bool): Whether to fetch data from the query. Defaults to False.

    Returns:
        Union[bool, list]: Returns True if the query executes successfully (for non-SELECT queries),
        or a list of rows if fetching data (for SELECT queries).
    """
    conn = await get_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute(query, values)
            if fetch:
                result = cursor.fetchall()
                logger.info("Fetching query was successfull !")

                return result
            else:
                conn.commit()
                logger.info("query was successfull !")

                return True
            
        except Exception as e:
            logger.exception("an ERROR occured in executing query -> %s", e)
            return False
        finally:
            if conn:
                conn.close()




async def creating_tables():

    query1 = """
            CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            user_name VARCHAR(255),
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            phone_number VARCHAR(50)
        );
    """

    query2 = """
            CREATE TABLE IF NOT EXISTS keywords (
            id BIGINT PRIMARY KEY,
            keyword VARCHAR(255),
            user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE
        );
    """

    query3= """
            CREATE TABLE IF NOT EXISTS messages (
            id BIGINT PRIMARY KEY,
            telegram_id BIGINT,
            content TEXT,
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
"""
    try:
        await execute_query(query1, None, False)
        await execute_query(query2, None, False)
        await execute_query(query3, None, False)
        return True
    except:
        return False

    




async def add_newMessage(telegram_id, content, status, created_at, updated_at=None, deleted_at=None):
    query = """
                INSERT INTO messages (telegram_id, content, status, created_at, updated_at, deleted_at)
                VALUES (%s, %s, %s, %s, %s, %s) 
            """
    values = (telegram_id, content, status, created_at, updated_at, deleted_at)
    result = await execute_query(query, values, False)
    return result



async def update_message(telegram_id, content, status, updated_at):
    query = """
                UPDATE messages
                SET content = %s, status = %s, updated_at = %s 
                WHERE telegram_id = %s
            """
    values = (content, status, updated_at, telegram_id)
    result = await execute_query(query, values, False)
    return result



async def delete_message(telegram_id, deleted_at):
    query = """
                UPDATE messages
                SET status = %s, deleted_at=%s
                WHERE telegram_id = %s
            """
    values = ("deleted",deleted_at, telegram_id)
    result = await execute_query(query, values, False)
    return result


async def retrieve_message(message_id):
    query = """
                SELECT content
                FROM messages
                WHERE telegram_id = %s
            """
    value = (message_id,)
    result = await execute_query(query, value, True)
    return result



async def add_user(user_id: int, username: str| None, first_name: str| None, last_name:str| None, phone_number:str| None):
    """add a user recored to users table in database

    Args:
        id (str) : user's id
        username (str) : user's username
        first_name (str) : user's first_name
        last_name (str) : user's last_name
        phone_number (str) : user's phone_number
    """
    query = """
                INSERT INTO users (user_id, user_name, first_name, last_name, phone_number)
                VALUES (%s, %s, %s, %s, %s) 
                ON CONFLICT (user_id) DO NOTHING;
            """
    values = (user_id, username, first_name, last_name, phone_number)
    result = await execute_query(query, values, False)
    return result

            

async def add_keyword(keyword, user_id):
    """add a keyword table to keywords table in database.

    Args:
        keyword(str) : the keyword user wants to add
        user_id(int) : user_id colmun of users table which is an identifier.
    """
    query = """INSERT INTO keywords (keyword, user_id) VALUES (%s, %s) """
    values = (keyword, user_id)
    result = await execute_query(query, values, False)
    return result



async def retireve_keywords(user_id):
    """retrieving all keywords belongs to user_id

    Args:
        user_id(int): the user's id
    """
    query = """SELECT id,keyword FROM keywords WHERE user_id=%s"""
    value = (user_id,)
    result = await execute_query(query, value, True)
    
    return result



async def retireve_keyword(keyword_id):
    """retrieving a keyword with its keyword_id 

    Args:
        keyword_id(int): the keyword's id
    """
    query = """SELECT id,keyword FROM keywords WHERE id=%s"""
    value = (keyword_id,)
    result = await execute_query(query, value, True)
    
    return result



async def retrieve_all_keywords():
    query = """SELECT user_id,keyword FROM keywords"""
    result = await execute_query(query, None, True)
    return result



async def delete_keyword(keyword_id):
    """Edit keyword which its id is keyword_id

    Args:
        keyword_id(int): the keyword's id
    """
    query = """DELETE FROM keywords WHERE id= %s"""
    values = (keyword_id,)
    result = await execute_query(query, values, False)
    return result



async def count_user_keywords(user_id):
    query = """
                SELECT Count(*) FROM keywords WHERE user_id = %s
            """
    value = (user_id,)
    result = await execute_query(query, value, True)
    return result



async def retrieve_all_users():
    query = """
        SELECT * FROM users
    """
    value = None
    result = await execute_query(query, value, True)
    return result