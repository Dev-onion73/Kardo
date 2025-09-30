import sqlite3
from datetime import date
from modules.security import hashpwd

    
def get_role(email):
    with sqlite3.connect("data/instance.db") as con:
        cur = con.cursor()
        cur.execute("SELECT role FROM users WHERE email = ?",(email,))
        user = cur.fetchone()
        if(user != None):
            return user[0]


class users:
    def add(self, user):
        """
        user = [full_name, phone_number, email, password, role]
        """
        with sqlite3.connect("data/instance.db") as con:
            try:
                full_name, phone, email, password, role = [u.strip() for u in user]
                hashed = hashpwd(password)
                cur = con.cursor()
                cur.execute(
                    '''INSERT INTO users (full_name, phone_number, email, password, role) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (full_name, phone, email, hashed, role)
                )
                con.commit()
                print(f"Added User: {full_name} ({role})")
                return True
            except Exception as e:
                print("Exception: " + str(e))
                return False

    def get(self, user_id=None):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            if user_id is None:
                cur.execute(
                    '''SELECT user_id, full_name, phone_number, email, role, registered_on 
                       FROM users'''
                )
                return cur.fetchall()
            else:
                cur.execute(
                    '''SELECT user_id, full_name, phone_number, email, role, registered_on 
                       FROM users WHERE user_id = ?''', (user_id,)
                )
                return cur.fetchone()

    def search(self, phone_number=None, email=None):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            if phone_number:
                cur.execute(
                    '''SELECT user_id, full_name, phone_number, email, password, role, registered_on 
                       FROM users WHERE phone_number = ?''', (phone_number,)
                )
            elif email:
                cur.execute(
                    '''SELECT user_id, full_name, phone_number, email, password, role, registered_on 
                       FROM users WHERE email = ?''', (email,)
                )
            else:
                return None

            user = cur.fetchone()
            if user:
                print(f"User found: ID={user[0]}, Name={user[1]}")
                return {
                    "id": user[0],
                    "full_name": user[1],
                    "phone_number": user[2],
                    "email": user[3],
                    "pwd": user[4],  # hashed password
                    "role": user[5],
                    "registered_on": user[6]
                }
            else:
                print("User not found.")
                return None

    def remove(self, user_id):
        if user_id == 0:
            print("Cannot delete the admin user!")
            return False
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                con.commit()
                print("User deleted successfully.")
                return True
            except Exception as e:
                print("Exception: " + str(e))
                return False

    def setup_admin(self, adm_pwd, adm_email="admin@example.com", adm_phone="0000000000"):
        """Create admin account with user_id=0 if it doesn't exist"""
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute("SELECT user_id FROM users WHERE user_id = 0")
            if cur.fetchone() is None:
                cur.execute(
                    '''INSERT INTO users (user_id, full_name, phone_number, email, password, role)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (0, "Admin User", adm_phone, adm_email, self.hashpwd(adm_pwd), "admin")
                )
                con.commit()
                print("Admin user created with user_id=0")
            else:
                print("Admin user already exists")