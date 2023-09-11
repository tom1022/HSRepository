import pymysql.cursors, yaml, sys, nltk, os


env = input("Environment([D]evelopment/[P]roduct): ")
if env == "P":
    env = "Product"
    print("Which DB do you want to use?")
    db = input("[M]aria DB/[S]QLite: ")
    if db == "M":
        database = "MySQL"
        username = input("Username: ")
        password = input("Password: ")
        dbname = input("Database Name:")
        host = input("Host: ")
        try:
            cn = pymysql.connect(
                host=host,
                user=username,
                password=password,
                database=dbname,
                cursorclass=pymysql.cursors.DictCursor)
            cn.close()
        except (pymysql.err.OperationalError):
            sys.exit("Something was incorrect")
    elif db == "S":
        database = "SQLite"
        username = "root"
        password = "password"
        dbname = "pdf-database"
        host = "localhost"
    else:
        sys.exit("The entered option was not supported")

    savedir = input("Fullpath of data saving directory: ")
    if not os.path.isdir(savedir):
        print("The entered directory path was not found.\nI'll make this...")
        try:
            os.makedirs()
        except(PermissionError):
            sys.exit("Permission Denined")
elif env == "D":
    env = "Dev"
    database = "SQLite"
    username = "root"
    password = "password"
    dbname = "pdf-database"
    host = "localhost"
    savedir = "/tmp/"

print("Downloading WordNet...")
nltk.download('all')

write_data = {"env": env, "database": database, "MySQL": {"host": host, "username": username, "password": password, "dbname": dbname}, "SaveDir": savedir}

with open('config.yml', 'w') as yml:
    yaml.dump(write_data, yml, default_flow_style=False)
