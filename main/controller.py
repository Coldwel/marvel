# controller.py
import hashlib
from model import MarvelAPI, Database

class SearchController:
    def __init__(self, config, db_config):
        self.public_key = config['MARVEL_PUBLIC_KEY']
        self.private_key = config['MARVEL_PRIVATE_KEY']
        self.marvel_api = MarvelAPI(self.public_key, self.private_key)
        self.db_config = db_config
        self.setup_database()

    def setup_database(self):
        with Database(self.db_config) as conn:
            cursor = conn.cursor()
            create_users_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                email VARCHAR(255) UNIQUE,
                password VARCHAR(255)
            )
            """
            cursor.execute(create_users_table_query)

            create_favorites_table_query = """
            CREATE TABLE IF NOT EXISTS favorites (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                comic_title VARCHAR(255),
                comic_description TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
            cursor.execute(create_favorites_table_query)

            conn.commit()

    def search(self, query, page=1):
        # Implement the search logic using MarvelAPI
        return self.marvel_api.search_characters(query, page)

    def generate_hash(self, timestamp):
        hash_input = timestamp + self.private_key + self.public_key
        md5_hash = hashlib.md5(hash_input.encode('utf-8')).hexdigest()
        return md5_hash

    def register_user(self, name, email, password):
        with Database(self.db_config) as conn:
            cursor = conn.cursor()
            check_email_query = "SELECT COUNT(*) FROM users WHERE email = %s"
            print(f"Executing query: {check_email_query}, params: {email}")
            cursor.execute(check_email_query, (email,))
            email_count = cursor.fetchone()[0]
            print(f"Email count: {email_count}")

            if email_count > 0:
                print("Email already exists.")
                return False

            insert_user_query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
            print(f"Executing query: {insert_user_query}, params: {name}, {email}, {password}")
            cursor.execute(insert_user_query, (name, email, password))
            conn.commit()

            print("User registered successfully.")
            return True

    def login_user(self, username, password):
        with Database(self.db_config) as conn:
            cursor = conn.cursor()
            login_query = "SELECT * FROM users WHERE email = %s AND password = %s"
            print(f"Executing query: {login_query}, params: {username}, {password}")
            cursor.execute(login_query, (username, password))
            user = cursor.fetchone()

            if user:
                print("Login successful.")
                return user
            else:
                print("Invalid username or password.")
                return None

    def add_favorite_comic(self, user_id, comic_title, comic_description):
        with Database(self.db_config) as conn:
            cursor = conn.cursor()
            add_favorite_query = "INSERT INTO favorites (user_id, comic_title, comic_description) VALUES (%s, %s, %s)"
            print(f"Executing query: {add_favorite_query}, params: {user_id}, {comic_title}, {comic_description}")
            cursor.execute(add_favorite_query, (user_id, comic_title, comic_description))
            conn.commit()

            return True

    def get_favorite_comics(self, user_id):
        with Database(self.db_config) as conn:
            cursor = conn.cursor(dictionary=True)
            get_favorites_query = "SELECT id, comic_title, comic_description FROM favorites WHERE user_id = %s"
            print(f"Executing query: {get_favorites_query}, params: {user_id}")
            cursor.execute(get_favorites_query, (user_id,))
            favorite_comics = cursor.fetchall()

            return favorite_comics

    def remove_favorite_comic(self, user_id, comic_id):
        with Database(self.db_config) as conn:
            cursor = conn.cursor()
            remove_favorite_query = "DELETE FROM favorites WHERE user_id = %s AND id = %s"
            print(f"Executing query: {remove_favorite_query}, params: {user_id}, {comic_id}")
            cursor.execute(remove_favorite_query, (user_id, comic_id))
            conn.commit()

            return True
