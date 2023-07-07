import os
from pathlib import Path
from abc import ABC, abstractmethod
import dotenv
import psycopg2
#  internals
from app.models import NewsDB, NewsSchema

BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(BASE_DIR / ".env")


########### TABLES #####################
t_news = "t_news"


class Database(ABC):
    """
    Database context manager
    """

    def __init__(self, driver) -> None:
        self.driver = driver

    @abstractmethod
    def connect_to_database(self):
        raise NotImplementedError()

    def __enter__(self):
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exception_type, exc_val, traceback):
        self.cursor.close()
        self.connection.close()


class PgDatabase(Database):
    """PostgreSQL Database context manager"""

    def __init__(self) -> None:
        self.driver = psycopg2
        super().__init__(self.driver)

    def connect_to_database(self):
        return self.driver.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )


def add_new_column_to_table(table: str, column: str, datatype: str):
    with PgDatabase() as db:
        db.cursor.execute(f"""
            ALTER TABLE {table} 
            ADD COLUMN {column} {datatype};
                         """)


def drop_tables():
    with PgDatabase() as db:
        db.cursor.execute(f"DROP TABLE IF EXISTS {t_news} CASCADE;")
        db.connection.commit()
        print("Tables are dropped...")


def create_tables():
    with PgDatabase() as db:
        db.cursor.execute(f"""CREATE TABLE {t_news} (
            id SERIAL PRIMARY KEY,
            published_date TIMESTAMPTZ,
            created_date TIMESTAMPTZ DEFAULT NOW(),
            created_by VARCHAR(140),
            context TEXT NOT NULL
            );
        """)
        db.connection.commit()
        print("Tables are created successfully...")


def insert_t_news(payload: NewsSchema, *args, **kwargs) -> NewsDB:
    with PgDatabase() as db:
        db.cursor.execute(f"""
        INSERT INTO {t_news}(created_by, context, published_date) 
        VALUES('{payload.created_by}', 
                '{payload.context}', 
                '{payload.published_date}'
                ) 
        RETURNING id;
                    """)
        db.connection.commit()
        inserted_id = db.cursor.fetchone()[0]

        obj = select_t_news_by_id(inserted_id)
    return obj


def select_t_news():
    with PgDatabase() as db:
        db.cursor.execute(f"""SELECT id, created_by, context, published_date 
                         FROM {t_news};""")
        objects = [
            {
                "id": data[0],
                "created_by": data[1],
                "context":data[2],
                "published_date":str(data[3])
            }
            for data in db.cursor.fetchall()
        ]
    return objects


def select_t_news_by_id(id: int) -> dict:
    with PgDatabase() as db:
        db.cursor.execute(f"""
        SELECT id, created_by, context, published_date FROM {t_news}
        WHERE id={id};
                        """)
        data = db.cursor.fetchone()
        if data is None:
            return None

    return {
        "id": data[0],
        "created_by": data[1],
        "context": data[2],
        "published_date": str(data[3])
    }


def delete_t_news_by_id(id: int):
    with PgDatabase() as db:
        db.cursor.execute(f"""
        DELETE FROM {t_news}
        WHERE id={id};
                        """)
        db.connection.commit()
        res = db.cursor.statusmessage
    if res == "DELETE 1":
        return True
    return False


def update_t_news_by_id(id: int, payload: NewsSchema):
    with PgDatabase() as db:
        db.cursor.execute(f"""
        UPDATE {t_news}
        SET created_by='{payload.created_by}', 
            context='{payload.context}', 
            published_date='{payload.published_date}'
        WHERE id='{id}'
        RETURNING id;
                        """)
        db.connection.commit()
        result = db.cursor.fetchone()
        if not result:
            return None
        updated_id = result[0]
        obj = select_t_news_by_id(updated_id)
    return obj
