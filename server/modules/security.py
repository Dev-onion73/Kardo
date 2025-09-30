import hashlib, os, pickle, sqlite3, secrets, json
from datetime import date
import modules.dbmanage as dbm

def get_secrets():
    try:
        with open("data/secrets.json", "r") as file:
            return json.load(file)
    except Exception as e:
        print("Secrets file missing, Exception: "+str(e))

def start_checkup():
    if(not setup_check()):
        print("Creating new instance....")
        create_instance()
    else:
        print("Instance exists proceeding")

def setup_check():
    if(not os.path.exists("data/instance.db")):
        return False
    try:
        with open("data/admin_lock.pkl","rb") as f:
            setup = pickle.load(f)
            if(setup["dbstat"] == True):
                return True
            return False
            
    except FileNotFoundError:
        print("New Instance, Setup needed")
        return False

def create_instance():
    setup = {"dbstat":False,"admin":"admin","instDate":date.today() }
    try:
        with sqlite3.connect("data/instance.db") as con:
            with open("data/dbschema.sql", "r") as f:
                con.executescript(f.read())
                print("Database initialized successfully!")
                print("Getting Secrets.....")
                secrets = get_secrets()
                if(secrets != None):
                    adm_pwd = secrets["ADMIN_PWD"]
                else:
                    print("Secrets Missing..")
                    exit()
                setup["dbstat"] = True
                cur = con.cursor()
                cur.execute(f'''INSERT INTO Users (user_id, full_name, phone_number, email, password, role) VALUES (0,'admin', '9999900000 ','admin@kardo.com','{hashpwd(adm_pwd)}', 'admin')''')
                con.commit()
                print("Admin added with defaults.")
            with open("data/admin_lock.pkl","wb") as lock:
                pickle.dump(setup,lock)
    except FileNotFoundError:
        print("Schema not found verify if all files are present and correct")

def hashpwd(password): 
    return hashlib.sha256(password.encode()).hexdigest()
    
def verify_hash(password, pwdhash):
    return hashpwd(password) == pwdhash

def verify_login(usermail,enteredpwd):
    from modules.dbmanage import users
    obj = users()
    user = obj.search(email=usermail)
    if  user != None:
        if verify_hash(enteredpwd,user["pwd"]):
            del user["pwd"]
            return (True,user)
        return (False,"pwd")
    return (False,"usr")

