import sqlite3


class DBHelper:
    def __init__(self, db_filename):
        self.db_filename = db_filename

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_filename)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


def initialize_database(filename):
    with DBHelper(filename) as cursor:
        cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    joined DATE,
    reminder TEXT,
    lang TEXT);""")
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task_number INTEGER,
    name TEXT,
    creation DATE,
    deadline DATE,
    priority_id TEXT,
    reward TEXT,
    description TEXT,
    timezone TEXT,
    overdue BOOLEAN DEFAULT FALSE,
    finished BOOLEAN DEFAULT FALSE,
    daily BOOLEAN DEFAULT FALSE,
    FOREIGN KEY(user_id) REFERENCES Users(id),
    FOREIGN KEY(priority_id) REFERENCES Priority(id)
);
""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS Priority (
    id INTEGER PRIMARY KEY,
    name TEXT,
    level INTEGER,
    description TEXT);
    """)


database_name = "storage.db"


def user_exists(cursor, user_id):
    cursor.execute("SELECT id FROM Users WHERE id=?", (user_id,))
    return cursor.fetchone() is not None


def create_task(user_id):
    with DBHelper(database_name) as cursor:
        cursor.execute("INSERT INTO Tasks (user_id, name, creation) VALUES (?, datetime('now'))",
                       (user_id,))
        return cursor.lastrowid  # Returns the ID of the last inserted row


def update_task_priority(task_id, priority):
    with DBHelper(database_name) as cursor:
        cursor.execute("UPDATE Tasks SET priority_id=? WHERE id=?",
                       (priority, task_id))


def update_task_deadline(task_id, deadline):
    with DBHelper(database_name) as cursor:
        cursor.execute("UPDATE Tasks SET deadline=datetime(?) WHERE id=?",
                       (deadline, task_id))


def update_task_name(task_id, name):
    with DBHelper(database_name) as cursor:
        cursor.execute("UPDATE Tasks SET name=? WHERE id=?",
                       (name, task_id))


def update_task_description(task_id, description):
    with DBHelper(database_name) as cursor:
        cursor.execute("UPDATE Tasks SET description=? WHERE id=?",
                       (description, task_id))


def add_user(user_id, name, username, date):
    with DBHelper(database_name) as cursor:
        if not user_exists(cursor, user_id):
            cursor.execute("INSERT INTO Users VALUES (?, ?, ?, ?, ?)", (user_id, name, username, date, "en"))
        return "User already exists!"


def update_user_name(user_id, new_name):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("UPDATE Users SET name = ? WHERE id = ?", (new_name, user_id))
        return "User not found!"


def get_name(user_id):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("SELECT name FROM Users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else "It seems that you don't have a name."
        return "User not found!"


def get_priority_level(user_id, name):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("SELECT level FROM Priority WHERE id = ? AND name = ?", (user_id, name))
            result = cursor.fetchone()
            return result[0] if result else None
        return "User not found!"


def get_priority_name(user_id, level):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("SELECT name FROM Priority WHERE id = ? AND level = ?", (user_id, level))
            result = cursor.fetchone()
            return result[0] if result else None
        return "User not found!"


def add_priority(user_id, name, level):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            if get_priority_level(user_id, name) is not None:
                return "There is a priority with the same name already exist!"
            if get_priority_name(user_id, level) is not None:
                return "There is a priority with the same level already exist!"
            cursor.execute("INSERT INTO Priority VALUES (?, ?, ?)", (user_id, name, level))
            return "Priority added!"
        return "User not found!"


def remove_priority(user_id, name):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("DELETE FROM Priority WHERE id = ? AND name = ?", (user_id, name))
            return "Priority removed!"
        return "User not found!"


def get_all_priority(user_id):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("SELECT name, value FROM Priority WHERE id = ?", (user_id,))
            return list(map(lambda x: x[0], cursor.fetchall()))
        return "User not found!"


def add_task(user_id, name, creation, deadline, priority_id, reward, description, timezone, overdue=False,
             finished=False, daily=False):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("SELECT COUNT(user_id) FROM Tasks")
            n = cursor.fetchone()[0] + 1
            cursor.execute("""
                           INSERT INTO Tasks (user_id, task_number, name, creation, deadline, priority_id, reward, description, timezone, overdue, finished, daily)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                           """,
                           (user_id, n, name, creation, deadline, priority_id, reward, description, timezone,
                            overdue, finished, daily))
            return "Task added!"
        return "User not found"


def update_deadline(user_id, task_number, deadline):
    with DBHelper(database_name) as cursor:
        cursor.execute("UPDATE Tasks SET deadline = ? WHERE id = ? AND n = ?", (deadline, user_id, task_number))
        return "Deadline updated!"


def get_tasks(user_id):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("SELECT task_number, name, priority_id, deadline FROM Tasks WHERE user_id = ? ORDER BY task_number",
                           (user_id,))
            return cursor.fetchall()


def get_task(user_id, n):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("SELECT n, name, priority, deadline, finished FROM Tasks WHERE id = ? AND n = ?",
                           (user_id, n))
            return cursor.fetchone()


def remove_task(user_id, n):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("DELETE FROM Tasks WHERE id = ? AND n = ?", (user_id, n))
            # Assuming tasks are reordered after deletion, potentially needed here.
            cursor.execute(f"UPDATE Tasks SET task_number = task_number - 1 WHERE user_id = ? AND task_number > ?"
                           , (user_id, n))
            # while get_task(user_id, n):
            #     cursor.execute("UPDATE Tasks SET n = ? WHERE id = ? AND n = ?", (n - 1, user_id, n))
            #     n += 1
            return "Removed!"


def mark_task(user_id, n):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("UPDATE Tasks SET finished = TRUE WHERE id = ? AND n = ?", (user_id, n))
            return "Task marked as completed!"


def clear_priorities(user_id):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            cursor.execute("DELETE FROM Priority WHERE id = ?", (user_id,))
            return "Cleared!"
        return "User not found!"


def set_default(user_id):
    with DBHelper(database_name) as cursor:
        if user_exists(cursor, user_id):
            add_priority(user_id, 'Critical', 4)
            add_priority(user_id, 'High', 3)
            add_priority(user_id, 'Medium', 2)
            add_priority(user_id, 'Low', 1)


# Initialization call
initialize_database("storage.db")
