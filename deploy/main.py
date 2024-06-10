import db
import subprocess
import os
import psycopg2
from typing import Optional


def get_env(key: str) -> Optional[str]:
    val = os.getenv(key)
    if val == "":
        raise KeyError("key is not exist: " + key)
    return val


class SupabaseConnectInfo:
    def __init__(self):
        self.host = get_env("SUPABASE_HOST")
        self.port = get_env("SUPABASE_PORT")
        self.user = get_env("SUPABASE_USER")
        self.password = get_env("SUPABASE_PASSWORD")
        self.db_name = get_env("SUPABASE_DB")


def run_os_cmd(command: list[str]) -> None:
    result = None
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except Exception as e:
        raise e

    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        print("Error output:", result.stderr)
        raise subprocess.CalledProcessError(
            result.returncode, command, output=result.stdout, stderr=result.stderr
        )


def run_scrapy_spider():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    main_py_path = os.path.join(parent_dir, "main.py")
    output_file = os.path.join(script_dir, "whatap-docs.json")

    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Existing file '{output_file}' has been deleted.")

    command = [
        "scrapy",
        "runspider",
        "--set",
        "FEED_EXPORT_ENCODING=utf-8",
        "--set",
        "FEED_EXPORT_INDENT=2",
        main_py_path,
        "-o",
        output_file,
    ]

    run_os_cmd(command)


def store_json_to_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)

    command = [
        "node",
        parent_dir + "/store.js",
    ]

    run_os_cmd(command)


if __name__ == "__main__":
    info: SupabaseConnectInfo = SupabaseConnectInfo()
    try:
        conn = psycopg2.connect(
            host=info.host,
            port=int(info.port),
            dbname=info.db_name,
            user=info.user,
            password=info.password,
        )

    except Exception as e:
        print(e)
        exit(1)

    conn.autocommit = False
    exit_code = 0

    try:
        db.drop_table_if_exists_and_not_empty(conn, "whatap_docs_temp")
        db.run_ddl(conn)
        print("ddl complete")
        run_scrapy_spider()
        print("scrap complete")
        store_json_to_db()
        print("store complete")
        db.promote_temp_table_to_main_table(conn)
        print("promote complete")
    except Exception as e:
        print(e)
        exit_code = 1
    finally:
        conn.close()
        exit(exit_code)
