from pathlib import Path
import psycopg2


def drop_table_if_exists_and_not_empty(
    conn: psycopg2.extensions.connection, table_name: str
) -> None:
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);",
            (table_name,),
        )
        result = cursor.fetchone()
        table_exists = result[0] if result else False

        if not table_exists:
            print(f"Table '{table_name}' does not exist.")
            return

        # 테이블에 행이 있는지 확인
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        result = cursor.fetchone()
        row_count = result[0] if result else 0

        if row_count == 0:
            print(f"Table '{table_name}' is empty.")
            return

        # 테이블 삭제
        cursor.execute(f"DROP TABLE {table_name};")
        conn.commit()
        print(f"Table '{table_name}' has been dropped.")
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        print(f"Failed to drop table '{table_name}': {e}")
        raise e
    finally:
        if cursor:
            cursor.close()


def run_ddl(conn: psycopg2.extensions.connection) -> None:
    ddl: str = Path("ddl.sql").read_text()
    cursor = conn.cursor()
    try:
        cursor.execute(ddl)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Failed to execute query or commit: {e}")
    finally:
        if cursor:
            cursor.close()


def promote_temp_table_to_main_table(conn: psycopg2.extensions.connection) -> None:
    cur = conn.cursor()
    try:
        cur.execute("DROP TABLE IF EXISTS whatap_docs_backup;")
        cur.execute("ALTER TABLE whatap_docs RENAME TO whatap_docs_backup;")
        cur.execute("ALTER TABLE whatap_docs_temp RENAME TO whatap_docs;")

        conn.commit()
        print("Table promotion completed successfully.")
    except psycopg2.Error as e:
        conn.rollback()
        raise Exception(f"Failed to promote temp table: {e}")
    finally:
        cur.close()
