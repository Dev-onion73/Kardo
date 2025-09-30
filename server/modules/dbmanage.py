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
        user = [full_name, phone_number, email, password ]
        """
        with sqlite3.connect("data/instance.db") as con:
            try:
                full_name, phone, email, password = [u.strip() for u in user]
                hashed = hashpwd(password)
                cur = con.cursor()
                cur.execute(
                    '''INSERT INTO users (full_name, phone_number, email, password) 
                       VALUES (?, ?, ?, ?)''',
                    (full_name, phone, email, hashed)
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



class vendors:
    def add(self, vendor):
        """
        vendor = [business_name, category, contact_email, contact_phone, password]
        """
        with sqlite3.connect("data/instance.db") as con:
            try:
                business_name, category, contact_email, contact_phone, password = [
                    v.strip() if isinstance(v, str) else v for v in vendor
                ]
                hashed = hashpwd(password)

                cur = con.cursor()
                cur.execute(
                    '''INSERT INTO businesses 
                       (business_name, category, contact_email, contact_phone, password) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (business_name, category, contact_email, contact_phone, hashed)
                )
                con.commit()
                print(f"Added Business: {business_name}")
                return True
            except Exception as e:
                print("Exception: " + str(e))
                return False

    def get(self, business_id=None):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            if business_id is None:
                cur.execute(
                    '''SELECT business_id, business_name, category, 
                              contact_email, contact_phone, joined_on 
                       FROM businesses'''
                )
                return cur.fetchall()
            else:
                cur.execute(
                    '''SELECT business_id, business_name, category, 
                              contact_email, contact_phone, joined_on 
                       FROM businesses WHERE business_id = ?''',
                    (business_id,)
                )
                return cur.fetchone()

    def search(self, name=None, email=None, phone=None):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            if name:
                cur.execute(
                    '''SELECT business_id, business_name, category, 
                              contact_email, contact_phone, password, joined_on 
                       FROM businesses WHERE business_name = ?''', (name,)
                )
            elif email:
                cur.execute(
                    '''SELECT business_id, business_name, category, 
                              contact_email, contact_phone, password, joined_on 
                       FROM businesses WHERE contact_email = ?''', (email,)
                )
            elif phone:
                cur.execute(
                    '''SELECT business_id, business_name, category, 
                              contact_email, contact_phone, password, joined_on 
                       FROM businesses WHERE contact_phone = ?''', (phone,)
                )
            else:
                return None

            vendor = cur.fetchone()
            if vendor:
                print(f"Vendor found: ID={vendor[0]}, Name={vendor[1]}")
                return {
                    "id": vendor[0],
                    "business_name": vendor[1],
                    "category": vendor[2],
                    "contact_email": vendor[3],
                    "contact_phone": vendor[4],
                    "pwd": vendor[5],
                    "joined_on": vendor[6]
                }
            else:
                print("Vendor not found.")
                return None

    def remove(self, business_id):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute("DELETE FROM businesses WHERE business_id = ?", (business_id,))
                con.commit()
                print(f"Vendor ID {business_id} deleted successfully.")
                return True
            except Exception as e:
                print("Exception: " + str(e))
                return False