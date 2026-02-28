import os
import sys
import subprocess
import shutil
import datetime
import getpass
import platform
from pathlib import Path

# Ranglar va formatlash
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    BOLD = '\033[1m'
    NC = '\033[0m'

# Global o'zgaruvchilar
SCRIPT_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = SCRIPT_DIR / "db_configs"
BACKUP_DIR = SCRIPT_DIR / "db_backups"
LOG_DIR = SCRIPT_DIR / "db_logs"
SSL_DIR = SCRIPT_DIR / "db_ssl"
TEMP_DIR = SCRIPT_DIR / "db_temp"
CACHE_DIR = SCRIPT_DIR / "db_cache"
DATA_DIR = SCRIPT_DIR / "db_data"
ARCHIVE_DIR = SCRIPT_DIR / "db_archive"
CONNECTION_FILE = CONFIG_DIR / "connections.db"
HISTORY_FILE = LOG_DIR / "command_history.log"
ERROR_LOG = LOG_DIR / "error.log"
DEBUG_LOG = LOG_DIR / "debug.log"

# Papkalarni yaratish
for directory in [CONFIG_DIR, BACKUP_DIR, LOG_DIR, SSL_DIR, TEMP_DIR, CACHE_DIR, DATA_DIR, ARCHIVE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

for file in [CONNECTION_FILE, HISTORY_FILE, ERROR_LOG, DEBUG_LOG]:
    file.touch(exist_ok=True)

# ============================================================================
# LOGGING FUNKSIYALARI
# ============================================================================

class Logger:
    @staticmethod
    def log(level, message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(LOG_DIR / "db_manager.log", 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
        
        if level == "ERROR":
            print(f"{Colors.RED}[XATOLIK]{Colors.NC} {message}")
        elif level == "SUCCESS":
            print(f"{Colors.GREEN}[OK]{Colors.NC} {message}")
        elif level == "WARNING":
            print(f"{Colors.YELLOW}[OGOHLANTIRISH]{Colors.NC} {message}")
        elif level == "INFO":
            print(f"{Colors.CYAN}[MA'LUMOT]{Colors.NC} {message}")
        else:
            print(message)
    
    @staticmethod
    def error(message):
        Logger.log("ERROR", message)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(ERROR_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    @staticmethod
    def success(message):
        Logger.log("SUCCESS", message)
    
    @staticmethod
    def warning(message):
        Logger.log("WARNING", message)
    
    @staticmethod
    def info(message):
        Logger.log("INFO", message)
    
    @staticmethod
    def debug(message):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(DEBUG_LOG, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {message}\n")

# ============================================================================
# UI FUNKSIYALARI
# ============================================================================

class UI:
    @staticmethod
    def show_header():
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{Colors.BLUE}╔══════════════════════════════════════════════════════════════╗{Colors.NC}")
        print(f"{Colors.BLUE}║{Colors.WHITE}{Colors.BOLD}              PROFESSIONAL DATABASE MANAGEMENT                {Colors.BLUE}║{Colors.NC}")
        print(f"{Colors.BLUE}║{Colors.WHITE}                 Version: 1.0 | Python Edition                {Colors.BLUE}║{Colors.NC}")
        print(f"{Colors.BLUE}╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
        print("")
    
    @staticmethod
    def show_menu_header(title):
        print(f"\n{Colors.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
        print(f"{Colors.WHITE}{Colors.BOLD}   {title}{Colors.NC}")
        print(f"{Colors.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}\n")
    
    @staticmethod
    def press_enter():
        input(f"\n{Colors.YELLOW}{Colors.BOLD}[Enter]{Colors.NC} tugmasini bosing davom etish uchun...")
    
    @staticmethod
    def confirm_action(message):
        response = input(f"{Colors.YELLOW}{message} (y/n): {Colors.NC}").strip().lower()
        return response in ['y', 'yes']
    
    @staticmethod
    def get_input(prompt, default=None):
        if default:
            value = input(f"{prompt} [{default}]: ").strip()
            return value if value else default
        else:
            return input(f"{prompt}: ").strip()
    
    @staticmethod
    def get_password(prompt):
        return getpass.getpass(f"{prompt}: ")

# ============================================================================
# DATABASE FUNKSIYALARI
# ============================================================================

class DatabaseManager:
    @staticmethod
    def run_command(cmd, shell=True, capture=True):
        try:
            if capture:
                result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=30)
                return result.stdout.strip(), result.stderr.strip(), result.returncode
            else:
                result = subprocess.run(cmd, shell=shell, timeout=30)
                return "", "", result.returncode
        except subprocess.TimeoutExpired:
            return "", "Timeout", 1
        except Exception as e:
            return "", str(e), 1

# ============================================================================
# MYSQL FUNKSIYALARI
# ============================================================================

class MySQLManager:
    @staticmethod
    def check():
        stdout, stderr, code = DatabaseManager.run_command("command -v mysql")
        return code == 0
    
    @staticmethod
    def status():
        UI.show_menu_header("MySQL HOLATI")
        
        if not MySQLManager.check():
            Logger.error("MySQL o'rnatilmagan")
            return
        
        stdout, stderr, code = DatabaseManager.run_command("sudo systemctl status mysql --no-pager -l")
        print(f"{Colors.CYAN}{Colors.BOLD}Xizmat holati:{Colors.NC}")
        for line in stdout.split('\n'):
            if "Active" in line or "Loaded" in line:
                print(line)
        
        stdout, stderr, code = DatabaseManager.run_command("mysql --version")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Versiya:{Colors.NC}")
        print(stdout)
        
        stdout, stderr, code = DatabaseManager.run_command("sudo ss -tlnp | grep mysql || echo '3306'")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Port:{Colors.NC}")
        print(stdout[:100])
        
        stdout, stderr, code = DatabaseManager.run_command("sudo mysql -e \"SHOW STATUS LIKE 'Threads_connected';\" 2>/dev/null")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Faol ulanishlar:{Colors.NC}")
        if stdout:
            print(stdout)
        else:
            print("Ma'lumot olish imkonsiz")
    
    @staticmethod
    def list_users():
        UI.show_menu_header("MYSQL FOYDALANUVCHILARI")
        
        if not MySQLManager.check():
            Logger.error("MySQL o'rnatilmagan")
            return
        
        stdout, stderr, code = DatabaseManager.run_command(
            "sudo mysql -e \"SELECT User, Host, plugin FROM mysql.user ORDER BY User;\" 2>/dev/null"
        )
        print(f"{Colors.GREEN}{Colors.BOLD}Barcha foydalanuvchilar:{Colors.NC}\n")
        if stdout:
            lines = stdout.split('\n')
            for line in lines:
                print(line)
        else:
            print("Ma'lumot olish imkonsiz")
    
    @staticmethod
    def create_user():
        UI.show_menu_header("YANGI MYSQL FOYDALANUVCHI")
        
        username = UI.get_input("Foydalanuvchi nomi")
        host = UI.get_input("Xost (localhost/192.168.%/%)", "localhost")
        password = UI.get_password("Parol")
        
        print("\nAuth plugin tanlang:")
        print("1) mysql_native_password (default)")
        print("2) caching_sha2_password")
        print("3) sha256_password")
        auth_choice = UI.get_input("Tanlov (1-3)", "1")
        
        if auth_choice == "1":
            auth_plugin = "mysql_native_password"
        elif auth_choice == "2":
            auth_plugin = "caching_sha2_password"
        elif auth_choice == "3":
            auth_plugin = "sha256_password"
        else:
            auth_plugin = "mysql_native_password"
        
        cmd = f"sudo mysql -e \"CREATE USER '{username}'@'{host}' IDENTIFIED WITH {auth_plugin} BY '{password}';\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success(f"Foydalanuvchi yaratildi: {username}@{host}")
            
            print("\nQo'shimcha sozlamalar:")
            print("1) Parol muddatini belgilash")
            print("2) Hisobni bloklash")
            print("3) Resurs limitlari")
            print("4) O'tkazib yuborish")
            extra_choice = UI.get_input("Tanlov", "4")
            
            if extra_choice == "1":
                days = UI.get_input("Parol amal qilish muddati (kun)", "30")
                cmd = f"sudo mysql -e \"ALTER USER '{username}'@'{host}' PASSWORD EXPIRE INTERVAL {days} DAY;\" 2>/dev/null"
                DatabaseManager.run_command(cmd)
                Logger.info(f"Parol muddati: {days} kun")
            elif extra_choice == "2":
                cmd = f"sudo mysql -e \"ALTER USER '{username}'@'{host}' ACCOUNT LOCK;\" 2>/dev/null"
                DatabaseManager.run_command(cmd)
                Logger.info("Hisob bloklandi")
            elif extra_choice == "3":
                queries = UI.get_input("So'rovlar limiti/soat", "0")
                connections = UI.get_input("Ulanishlar limiti/soat", "0")
                updates = UI.get_input("Yangilanishlar limiti/soat", "0")
                cmd = f"sudo mysql -e \"ALTER USER '{username}'@'{host}' WITH MAX_QUERIES_PER_HOUR {queries} MAX_CONNECTIONS_PER_HOUR {connections} MAX_UPDATES_PER_HOUR {updates};\" 2>/dev/null"
                DatabaseManager.run_command(cmd)
                Logger.info("Resurs limitlari o'rnatildi")
        else:
            Logger.error("Foydalanuvchi yaratishda xatolik")
    
    @staticmethod
    def delete_user():
        UI.show_menu_header("MYSQL FOYDALANUVCHI O'CHIRISH")
        
        MySQLManager.list_users()
        
        username = UI.get_input("Foydalanuvchi nomi")
        host = UI.get_input("Xost")
        
        if UI.confirm_action(f"Foydalanuvchi {username}@{host} ni o'chirishni tasdiqlaysizmi?"):
            cmd = f"sudo mysql -e \"DROP USER IF EXISTS '{username}'@'{host}'; FLUSH PRIVILEGES;\" 2>/dev/null"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            
            if code == 0:
                Logger.success(f"Foydalanuvchi o'chirildi: {username}@{host}")
            else:
                Logger.error("Foydalanuvchi o'chirishda xatolik")
    
    @staticmethod
    def change_password():
        UI.show_menu_header("MYSQL PAROL O'ZGARTIRISH")
        
        username = UI.get_input("Foydalanuvchi nomi")
        host = UI.get_input("Xost")
        new_password = UI.get_password("Yangi parol")
        new_password2 = UI.get_password("Yangi parol (takror)")
        
        if new_password != new_password2:
            Logger.error("Parollar mos kelmadi")
            return
        
        cmd = f"sudo mysql -e \"ALTER USER '{username}'@'{host}' IDENTIFIED BY '{new_password}'; FLUSH PRIVILEGES;\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success("Parol o'zgartirildi")
        else:
            Logger.error("Parol o'zgartirishda xatolik")
    
    @staticmethod
    def grant_privileges():
        UI.show_menu_header("MYSQL RUXSATLAR BERISH")
        
        MySQLManager.list_users()
        
        username = UI.get_input("Foydalanuvchi nomi")
        host = UI.get_input("Xost")
        
        stdout, stderr, code = DatabaseManager.run_command("sudo mysql -e \"SHOW DATABASES;\" 2>/dev/null")
        print(f"\n{Colors.CYAN}Ma'lumotlar bazalari:{Colors.NC}")
        print(stdout)
        
        database = UI.get_input("Ma'lumotlar bazasi nomi (* - barchasi)")
        if database == "*":
            database = "*"
        
        print("\nRuxsat turlari:")
        print("1) Barcha ruxsatlar (ALL PRIVILEGES)")
        print("2) O'qish (SELECT)")
        print("3) O'qish/Yozish (SELECT, INSERT, UPDATE, DELETE)")
        print("4) Ma'lumotlar strukturasi (CREATE, ALTER, DROP)")
        print("5) Maxsus ruxsatlar")
        print("6) Grant option bilan")
        
        priv_choice = UI.get_input("Tanlov (1-6)", "1")
        
        if priv_choice == "1":
            privileges = "ALL PRIVILEGES"
        elif priv_choice == "2":
            privileges = "SELECT"
        elif priv_choice == "3":
            privileges = "SELECT, INSERT, UPDATE, DELETE"
        elif priv_choice == "4":
            privileges = "CREATE, ALTER, DROP, INDEX"
        elif priv_choice == "5":
            privileges = UI.get_input("Ruxsatlarni vergul bilan yozing")
        elif priv_choice == "6":
            base_priv = UI.get_input("Ruxsatlar")
            privileges = f"{base_priv} WITH GRANT OPTION"
        else:
            Logger.error("Noto'g'ri tanlov")
            return
        
        cmd = f"sudo mysql -e \"GRANT {privileges} ON {database}.* TO '{username}'@'{host}'; FLUSH PRIVILEGES;\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success(f"Ruxsatlar berildi: {privileges}")
            
            cmd = f"sudo mysql -e \"SHOW GRANTS FOR '{username}'@'{host}';\" 2>/dev/null"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            print(f"\n{Colors.CYAN}Yangi grantlar:{Colors.NC}")
            print(stdout)
        else:
            Logger.error("Ruxsat berishda xatolik")
    
    @staticmethod
    def show_grants():
        UI.show_menu_header("MYSQL GRANTLAR")
        
        username = UI.get_input("Foydalanuvchi nomi")
        host = UI.get_input("Xost")
        
        cmd = f"sudo mysql -e \"SHOW GRANTS FOR '{username}'@'{host}';\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(stdout)
    
    @staticmethod
    def revoke_privileges():
        UI.show_menu_header("MYSQL RUXSATLARNI OLIB TASHLASH")
        
        username = UI.get_input("Foydalanuvchi nomi")
        host = UI.get_input("Xost")
        database = UI.get_input("Ma'lumotlar bazasi")
        
        cmd = f"sudo mysql -e \"SHOW GRANTS FOR '{username}'@'{host}';\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"\n{Colors.CYAN}Mavjud grantlar:{Colors.NC}")
        print(stdout)
        
        privileges = UI.get_input("Olib tashlanadigan ruxsatlar")
        
        cmd = f"sudo mysql -e \"REVOKE {privileges} ON {database}.* FROM '{username}'@'{host}'; FLUSH PRIVILEGES;\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success("Ruxsatlar olib tashlandi")
        else:
            Logger.error("Ruxsatlarni olib tashlashda xatolik")
    
    @staticmethod
    def list_databases():
        UI.show_menu_header("MYSQL MA'LUMOTLAR BAZALARI")
        
        cmd = "sudo mysql -e \"SELECT SCHEMA_NAME as 'Database' FROM information_schema.SCHEMATA ORDER BY SCHEMA_NAME;\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"{Colors.GREEN}{Colors.BOLD}Barcha ma'lumotlar bazalari:{Colors.NC}\n")
        print(stdout)
    
    @staticmethod
    def create_database():
        UI.show_menu_header("YANGI MYSQL MA'LUMOTLAR BAZASI")
        
        dbname = UI.get_input("Ma'lumotlar bazasi nomi")
        
        cmd = "sudo mysql -e \"SHOW CHARACTER SET;\" 2>/dev/null | head -10"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"\n{Colors.CYAN}Mavjud charsetlar:{Colors.NC}")
        print(stdout)
        
        charset = UI.get_input("Charset", "utf8mb4")
        collation = UI.get_input("Collation", "utf8mb4_unicode_ci")
        
        cmd = f"sudo mysql -e \"CREATE DATABASE IF NOT EXISTS {dbname} CHARACTER SET {charset} COLLATE {collation};\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success(f"Ma'lumotlar bazasi yaratildi: {dbname}")
            
            if UI.confirm_action("Foydalanuvchiga ruxsat berilsinmi?"):
                username = UI.get_input("Foydalanuvchi nomi")
                host = UI.get_input("Xost", "localhost")
                cmd = f"sudo mysql -e \"GRANT ALL PRIVILEGES ON {dbname}.* TO '{username}'@'{host}'; FLUSH PRIVILEGES;\" 2>/dev/null"
                DatabaseManager.run_command(cmd)
                Logger.success(f"Ruxsat berildi: {username}@{host}")
        else:
            Logger.error("Ma'lumotlar bazasi yaratishda xatolik")
    
    @staticmethod
    def drop_database():
        UI.show_menu_header("MYSQL MA'LUMOTLAR BAZASINI O'CHIRISH")
        
        MySQLManager.list_databases()
        
        dbname = UI.get_input("O'chiriladigan ma'lumotlar bazasi")
        
        if UI.confirm_action(f"DIQQAT! {dbname} butunlay o'chiriladi. Tasdiqlaysizmi?"):
            cmd = f"sudo mysql -e \"DROP DATABASE {dbname};\" 2>/dev/null"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            
            if code == 0:
                Logger.success(f"Ma'lumotlar bazasi o'chirildi: {dbname}")
            else:
                Logger.error("O'chirishda xatolik")
    
    @staticmethod
    def generate_url():
        UI.show_menu_header("MYSQL ULANISH URL GENERATSIYASI")
        
        host = UI.get_input("Host", "localhost")
        port = UI.get_input("Port", "3306")
        user = UI.get_input("User")
        password = UI.get_password("Password")
        database = UI.get_input("Database")
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}MySQL Ulanish URL'lari:{Colors.NC}\n")
        print(f"{Colors.WHITE}Standard URL:{Colors.NC}")
        print(f"mysql://{user}:{password}@{host}:{port}/{database}")
        print(f"\n{Colors.WHITE}JDBC URL:{Colors.NC}")
        print(f"jdbc:mysql://{host}:{port}/{database}?user={user}&password={password}")
        print(f"\n{Colors.WHITE}Python SQLAlchemy URL:{Colors.NC}")
        print(f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}")
        print(f"\n{Colors.WHITE}Command line:{Colors.NC}")
        print(f"mysql -h {host} -P {port} -u {user} -p{password} {database}")

# ============================================================================
# POSTGRESQL FUNKSIYALARI
# ============================================================================

class PostgreSQLManager:
    @staticmethod
    def check():
        stdout, stderr, code = DatabaseManager.run_command("command -v psql")
        return code == 0
    
    @staticmethod
    def status():
        UI.show_menu_header("POSTGRESQL HOLATI")
        
        if not PostgreSQLManager.check():
            Logger.error("PostgreSQL o'rnatilmagan")
            return
        
        stdout, stderr, code = DatabaseManager.run_command("sudo systemctl status postgresql --no-pager -l")
        print(f"{Colors.CYAN}{Colors.BOLD}Xizmat holati:{Colors.NC}")
        for line in stdout.split('\n'):
            if "Active" in line or "Loaded" in line:
                print(line)
        
        stdout, stderr, code = DatabaseManager.run_command("sudo -u postgres psql -c \"SELECT version();\" 2>/dev/null")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Versiya:{Colors.NC}")
        for line in stdout.split('\n'):
            if "PostgreSQL" in line:
                print(line)
                break
        
        stdout, stderr, code = DatabaseManager.run_command("sudo ss -tlnp | grep postgres || echo '5432'")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Port:{Colors.NC}")
        print(stdout[:100])
        
        stdout, stderr, code = DatabaseManager.run_command("sudo -u postgres psql -c \"SELECT count(*) as active_connections FROM pg_stat_activity;\" 2>/dev/null")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Faol ulanishlar:{Colors.NC}")
        print(stdout)
    
    @staticmethod
    def list_users():
        UI.show_menu_header("POSTGRESQL FOYDALANUVCHILARI")
        
        stdout, stderr, code = DatabaseManager.run_command("sudo -u postgres psql -c \"\\du\" 2>/dev/null")
        print(f"{Colors.GREEN}{Colors.BOLD}Barcha foydalanuvchilar:{Colors.NC}\n")
        print(stdout)
    
    @staticmethod
    def create_user():
        UI.show_menu_header("YANGI POSTGRESQL FOYDALANUVCHI")
        
        username = UI.get_input("Foydalanuvchi nomi")
        password = UI.get_password("Parol")
        
        options = ""
        
        print("\nRuxsatlar:")
        print("1) Oddiy foydalanuvchi")
        print("2) Superuser")
        print("3) Ma'lumotlar bazasi yaratish huquqi bilan")
        print("4) Replikatsiya huquqi bilan")
        
        priv_choice = UI.get_input("Tanlov (1-4)", "1")
        
        if priv_choice == "1":
            options = ""
        elif priv_choice == "2":
            options = "SUPERUSER"
        elif priv_choice == "3":
            options = "CREATEDB"
        elif priv_choice == "4":
            options = "REPLICATION"
        
        if UI.confirm_action("Ulanish limiti belgilansinmi?"):
            conn_limit = UI.get_input("Maksimal ulanishlar soni", "100")
            options += f" CONNECTION LIMIT {conn_limit}"
        
        if UI.confirm_action("Parol amal qilish muddati belgilansinmi?"):
            valid_until = UI.get_input("Muddat (YYYY-MM-DD)")
            options += f" VALID UNTIL '{valid_until}'"
        
        cmd = f"sudo -u postgres psql -c \"CREATE USER {username} WITH PASSWORD '{password}' {options};\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success(f"Foydalanuvchi yaratildi: {username}")
        else:
            Logger.error("Foydalanuvchi yaratishda xatolik")
    
    @staticmethod
    def delete_user():
        UI.show_menu_header("POSTGRESQL FOYDALANUVCHI O'CHIRISH")
        
        PostgreSQLManager.list_users()
        
        username = UI.get_input("Foydalanuvchi nomi")
        
        if UI.confirm_action(f"Foydalanuvchi {username} ni o'chirishni tasdiqlaysizmi?"):
            cmd = f"sudo -u postgres psql -c \"REASSIGN OWNED BY {username} TO postgres; DROP OWNED BY {username}; DROP USER IF EXISTS {username};\" 2>/dev/null"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            
            if code == 0:
                Logger.success(f"Foydalanuvchi o'chirildi: {username}")
            else:
                Logger.error("Foydalanuvchi o'chirishda xatolik")
    
    @staticmethod
    def change_password():
        UI.show_menu_header("POSTGRESQL PAROL O'ZGARTIRISH")
        
        username = UI.get_input("Foydalanuvchi nomi")
        new_password = UI.get_password("Yangi parol")
        new_password2 = UI.get_password("Yangi parol (takror)")
        
        if new_password != new_password2:
            Logger.error("Parollar mos kelmadi")
            return
        
        cmd = f"sudo -u postgres psql -c \"ALTER USER {username} WITH PASSWORD '{new_password}';\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success("Parol o'zgartirildi")
        else:
            Logger.error("Parol o'zgartirishda xatolik")
    
    @staticmethod
    def grant_privileges():
        UI.show_menu_header("POSTGRESQL RUXSATLAR BERISH")
        
        PostgreSQLManager.list_users()
        
        username = UI.get_input("Foydalanuvchi nomi")
        database = UI.get_input("Ma'lumotlar bazasi nomi")
        
        print("\nRuxsat turlari:")
        print("1) Barcha ruxsatlar (ALL PRIVILEGES)")
        print("2) O'qish (SELECT)")
        print("3) O'qish/Yozish (SELECT, INSERT, UPDATE, DELETE)")
        print("4) Ma'lumotlar strukturasi (CREATE, ALTER, DROP)")
        print("5) Maxsus ruxsatlar")
        print("6) Grant option bilan")
        
        priv_choice = UI.get_input("Tanlov (1-6)", "1")
        
        if priv_choice == "1":
            privileges = "ALL PRIVILEGES"
        elif priv_choice == "2":
            privileges = "SELECT"
        elif priv_choice == "3":
            privileges = "SELECT, INSERT, UPDATE, DELETE"
        elif priv_choice == "4":
            privileges = "CREATE, ALTER, DROP"
        elif priv_choice == "5":
            privileges = UI.get_input("Ruxsatlarni vergul bilan yozing")
        elif priv_choice == "6":
            base_priv = UI.get_input("Ruxsatlar")
            privileges = f"{base_priv} WITH GRANT OPTION"
        else:
            Logger.error("Noto'g'ri tanlov")
            return
        
        cmd = f"sudo -u postgres psql -c \"GRANT CONNECT ON DATABASE {database} TO {username};\" 2>/dev/null"
        DatabaseManager.run_command(cmd)
        
        cmd = f"sudo -u postgres psql -c \"GRANT {privileges} ON ALL TABLES IN SCHEMA public TO {username};\" 2>/dev/null"
        DatabaseManager.run_command(cmd)
        
        cmd = f"sudo -u postgres psql -c \"GRANT {privileges} ON ALL SEQUENCES IN SCHEMA public TO {username};\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success(f"Ruxsatlar berildi: {username}")
            
            cmd = f"sudo -u postgres psql -c \"\\dp {database}.*\" 2>/dev/null | head -20"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            print(f"\n{Colors.CYAN}Yangi grantlar:{Colors.NC}")
            print(stdout)
        else:
            Logger.error("Ruxsat berishda xatolik")
    
    @staticmethod
    def show_grants():
        UI.show_menu_header("POSTGRESQL GRANTLAR")
        
        username = UI.get_input("Foydalanuvchi nomi")
        
        cmd = f"sudo -u postgres psql -c \"\\du {username}\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(stdout)
        
        cmd = f"sudo -u postgres psql -c \"\\dp\" 2>/dev/null | grep {username} || echo 'Grantlar topilmadi'"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(stdout)
    
    @staticmethod
    def revoke_privileges():
        UI.show_menu_header("POSTGRESQL RUXSATLARNI OLIB TASHLASH")
        
        username = UI.get_input("Foydalanuvchi nomi")
        database = UI.get_input("Ma'lumotlar bazasi")
        
        cmd = f"sudo -u postgres psql -c \"\\dp {database}.*\" 2>/dev/null | grep {username}"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"\n{Colors.CYAN}Mavjud grantlar:{Colors.NC}")
        print(stdout)
        
        privileges = UI.get_input("Olib tashlanadigan ruxsatlar")
        
        cmd = f"sudo -u postgres psql -c \"REVOKE {privileges} ON ALL TABLES IN SCHEMA public FROM {username};\" 2>/dev/null"
        DatabaseManager.run_command(cmd)
        
        cmd = f"sudo -u postgres psql -c \"REVOKE {privileges} ON ALL SEQUENCES IN SCHEMA public FROM {username};\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success("Ruxsatlar olib tashlandi")
        else:
            Logger.error("Ruxsatlarni olib tashlashda xatolik")
    
    @staticmethod
    def list_databases():
        UI.show_menu_header("POSTGRESQL MA'LUMOTLAR BAZALARI")
        
        cmd = "sudo -u postgres psql -c \"\\l+\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"{Colors.GREEN}{Colors.BOLD}Barcha ma'lumotlar bazalari:{Colors.NC}\n")
        print(stdout)
    
    @staticmethod
    def create_database():
        UI.show_menu_header("YANGI POSTGRESQL MA'LUMOTLAR BAZASI")
        
        dbname = UI.get_input("Ma'lumotlar bazasi nomi")
        owner = UI.get_input("Egasi", "postgres")
        
        print("\nEncoding tanlang:")
        print("1) UTF8 (default)")
        print("2) LATIN1")
        print("3) SQL_ASCII")
        enc_choice = UI.get_input("Tanlov", "1")
        
        if enc_choice == "1":
            encoding = "UTF8"
        elif enc_choice == "2":
            encoding = "LATIN1"
        elif enc_choice == "3":
            encoding = "SQL_ASCII"
        else:
            encoding = "UTF8"
        
        cmd = f"sudo -u postgres psql -c \"CREATE DATABASE {dbname} OWNER {owner} ENCODING '{encoding}';\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success(f"Ma'lumotlar bazasi yaratildi: {dbname}")
        else:
            Logger.error("Ma'lumotlar bazasi yaratishda xatolik")
    
    @staticmethod
    def drop_database():
        UI.show_menu_header("POSTGRESQL MA'LUMOTLAR BAZASINI O'CHIRISH")
        
        PostgreSQLManager.list_databases()
        
        dbname = UI.get_input("O'chiriladigan ma'lumotlar bazasi")
        
        if UI.confirm_action(f"DIQQAT! {dbname} butunlay o'chiriladi. Tasdiqlaysizmi?"):
            cmd = f"sudo -u postgres psql -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{dbname}';\" 2>/dev/null"
            DatabaseManager.run_command(cmd)
            
            cmd = f"sudo -u postgres psql -c \"DROP DATABASE {dbname};\" 2>/dev/null"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            
            if code == 0:
                Logger.success(f"Ma'lumotlar bazasi o'chirildi: {dbname}")
            else:
                Logger.error("O'chirishda xatolik")
    
    @staticmethod
    def generate_url():
        UI.show_menu_header("POSTGRESQL ULANISH URL GENERATSIYASI")
        
        host = UI.get_input("Host", "localhost")
        port = UI.get_input("Port", "5432")
        user = UI.get_input("User")
        password = UI.get_password("Password")
        database = UI.get_input("Database")
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}PostgreSQL Ulanish URL'lari:{Colors.NC}\n")
        print(f"{Colors.WHITE}Standard URL:{Colors.NC}")
        print(f"postgresql://{user}:{password}@{host}:{port}/{database}")
        print(f"\n{Colors.WHITE}JDBC URL:{Colors.NC}")
        print(f"jdbc:postgresql://{host}:{port}/{database}?user={user}&password={password}")
        print(f"\n{Colors.WHITE}Python SQLAlchemy URL:{Colors.NC}")
        print(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
        print(f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}")
        print(f"\n{Colors.WHITE}Command line:{Colors.NC}")
        print(f"psql -h {host} -p {port} -U {user} -d {database}")

# ============================================================================
# KESH TOZALASH FUNKSIYALARI
# ============================================================================

class CacheManager:
    @staticmethod
    def clean_cache():
        UI.show_menu_header("KESH TOZALASH")
        
        print("1) 🧹 Barcha kesh fayllarni tozalash")
        print("2) 📁 Log fayllarni tozalash")
        print("3) 📦 Backup fayllarni tozalash")
        print("4) 🔧 Konfiguratsiya fayllarini tozalash")
        print("5) 🗑️ Temp fayllarni tozalash")
        print("6) 📊 Kesh statistikasi")
        print("7) 🔄 Barchasini tozalash")
        print("8) ◀️ Orqaga")
        
        choice = UI.get_input("Tanlov", "8")
        
        if choice == "1":
            if UI.confirm_action("Barcha kesh fayllar o'chirilsinmi?"):
                for f in CACHE_DIR.glob("*"):
                    if f.is_file():
                        f.unlink()
                Logger.success("Barcha kesh fayllar tozalandi")
        elif choice == "2":
            if UI.confirm_action("Log fayllar tozalansinmi?"):
                for f in LOG_DIR.glob("*.log"):
                    if f.stat().st_mtime < (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp():
                        f.unlink()
                with open(LOG_DIR / "db_manager.log", 'w'): pass
                with open(ERROR_LOG, 'w'): pass
                with open(DEBUG_LOG, 'w'): pass
                Logger.success("Log fayllar tozalandi")
        elif choice == "3":
            if UI.confirm_action("Backup fayllar tozalansinmi?"):
                days = int(UI.get_input("Necha kundan eski backup'lar o'chirilsin?", "7"))
                cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
                for f in BACKUP_DIR.glob("*.sql.gz"):
                    if datetime.datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                        f.unlink()
                Logger.success(f"{days} kundan eski backup'lar tozalandi")
        elif choice == "4":
            if UI.confirm_action("Konfiguratsiya fayllari tozalansinmi?"):
                cutoff = datetime.datetime.now() - datetime.timedelta(days=30)
                for f in CONFIG_DIR.glob("*.conf"):
                    if datetime.datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                        f.unlink()
                for f in CONFIG_DIR.glob("*.old"):
                    f.unlink()
                for f in CONFIG_DIR.glob("*.bak"):
                    f.unlink()
                Logger.success("Eski konfiguratsiya fayllari tozalandi")
        elif choice == "5":
            if UI.confirm_action("Temp fayllar tozalansinmi?"):
                for f in TEMP_DIR.glob("*"):
                    if f.is_file():
                        f.unlink()
                Logger.success("Temp fayllar tozalandi")
        elif choice == "6":
            print(f"\n{Colors.CYAN}Kesh statistikasi:{Colors.NC}")
            print(f"📁 Log fayllar: {len(list(LOG_DIR.glob('*.log')))} ta")
            print(f"📦 Backup fayllar: {len(list(BACKUP_DIR.glob('*.sql.gz')))} ta")
            print(f"🔧 Konfiguratsiya: {len(list(CONFIG_DIR.glob('*')))} ta")
            print(f"🗑️ Temp fayllar: {len(list(TEMP_DIR.glob('*')))} ta")
            print(f"🧹 Kesh fayllar: {len(list(CACHE_DIR.glob('*')))} ta")
        elif choice == "7":
            if UI.confirm_action("BARCHA fayllar tozalansinmi? (ehtiyot bo'ling!)"):
                for f in CACHE_DIR.glob("*"): f.unlink()
                for f in TEMP_DIR.glob("*"): f.unlink()
                for f in DATA_DIR.glob("*"): f.unlink()
                for f in LOG_DIR.glob("*.log"): f.unlink()
                with open(LOG_DIR / "db_manager.log", 'w'): pass
                with open(ERROR_LOG, 'w'): pass
                with open(DEBUG_LOG, 'w'): pass
                cutoff = datetime.datetime.now() - datetime.timedelta(days=1)
                for f in BACKUP_DIR.glob("*.sql.gz"):
                    if datetime.datetime.fromtimestamp(f.stat().st_mtime) < cutoff:
                        f.unlink()
                Logger.success("Barcha kesh va temp fayllar tozalandi")

# ============================================================================
# UMUMIY FUNKSIYALAR
# ============================================================================

class Utils:
    @staticmethod
    def system_info():
        UI.show_menu_header("TIZIM MA'LUMOTLARI")
        
        print(f"{Colors.CYAN}Ubuntu:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("lsb_release -d 2>/dev/null")
        print(stdout)
        
        print(f"\n{Colors.CYAN}Kernel:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("uname -r")
        print(stdout)
        
        print(f"\n{Colors.CYAN}CPU:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("nproc")
        print(f"{stdout} core")
        
        print(f"\n{Colors.CYAN}RAM:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("free -h | grep Mem | awk '{print $2}'")
        print(stdout)
        
        print(f"\n{Colors.CYAN}Disk:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("df -h / | awk 'NR==2 {print $2}'")
        print(stdout)
        
        print(f"\n{Colors.CYAN}MySQL:{Colors.NC}")
        if MySQLManager.check():
            stdout, stderr, code = DatabaseManager.run_command("mysql --version 2>/dev/null")
            print(stdout)
        else:
            print("O'rnatilmagan")
        
        print(f"\n{Colors.CYAN}PostgreSQL:{Colors.NC}")
        if PostgreSQLManager.check():
            stdout, stderr, code = DatabaseManager.run_command("psql --version 2>/dev/null")
            print(stdout)
        else:
            print("O'rnatilmagan")

# ============================================================================
# ASOSIY MENYU
# ============================================================================

class MainMenu:
    @staticmethod
    def mysql_menu():
        while True:
            UI.show_menu_header("MYSQL BOSHQARUVI")
            
            print("1) 📊 Holat")
            print("2) 👥 Foydalanuvchilar")
            print("3) ➕ Foydalanuvchi qo'shish")
            print("4) 🗑️ Foydalanuvchi o'chirish")
            print("5) 🔑 Parol o'zgartirish")
            print("6) 🔐 Ruxsatlar berish")
            print("7) 🔓 Ruxsatlarni ko'rish")
            print("8) 🔒 Ruxsatlarni olib tashlash")
            print("9) 🗄️ Ma'lumotlar bazalari")
            print("10) ➕ DB qo'shish")
            print("11) 🗑️ DB o'chirish")
            print("12) 🔗 URL generatsiya")
            print("13) ◀️ Orqaga")
            
            choice = UI.get_input("Tanlov", "13")
            
            if choice == "1":
                MySQLManager.status()
            elif choice == "2":
                MySQLManager.list_users()
            elif choice == "3":
                MySQLManager.create_user()
            elif choice == "4":
                MySQLManager.delete_user()
            elif choice == "5":
                MySQLManager.change_password()
            elif choice == "6":
                MySQLManager.grant_privileges()
            elif choice == "7":
                MySQLManager.show_grants()
            elif choice == "8":
                MySQLManager.revoke_privileges()
            elif choice == "9":
                MySQLManager.list_databases()
            elif choice == "10":
                MySQLManager.create_database()
            elif choice == "11":
                MySQLManager.drop_database()
            elif choice == "12":
                MySQLManager.generate_url()
            elif choice == "13":
                break
            else:
                Logger.error("Noto'g'ri tanlov")
            
            UI.press_enter()
    
    @staticmethod
    def postgresql_menu():
        while True:
            UI.show_menu_header("POSTGRESQL BOSHQARUVI")
            
            print("1) 📊 Holat")
            print("2) 👥 Foydalanuvchilar")
            print("3) ➕ Foydalanuvchi qo'shish")
            print("4) 🗑️ Foydalanuvchi o'chirish")
            print("5) 🔑 Parol o'zgartirish")
            print("6) 🔐 Ruxsatlar berish")
            print("7) 🔓 Ruxsatlarni ko'rish")
            print("8) 🔒 Ruxsatlarni olib tashlash")
            print("9) 🗄️ Ma'lumotlar bazalari")
            print("10) ➕ DB qo'shish")
            print("11) 🗑️ DB o'chirish")
            print("12) 🔗 URL generatsiya")
            print("13) ◀️ Orqaga")
            
            choice = UI.get_input("Tanlov", "13")
            
            if choice == "1":
                PostgreSQLManager.status()
            elif choice == "2":
                PostgreSQLManager.list_users()
            elif choice == "3":
                PostgreSQLManager.create_user()
            elif choice == "4":
                PostgreSQLManager.delete_user()
            elif choice == "5":
                PostgreSQLManager.change_password()
            elif choice == "6":
                PostgreSQLManager.grant_privileges()
            elif choice == "7":
                PostgreSQLManager.show_grants()
            elif choice == "8":
                PostgreSQLManager.revoke_privileges()
            elif choice == "9":
                PostgreSQLManager.list_databases()
            elif choice == "10":
                PostgreSQLManager.create_database()
            elif choice == "11":
                PostgreSQLManager.drop_database()
            elif choice == "12":
                PostgreSQLManager.generate_url()
            elif choice == "13":
                break
            else:
                Logger.error("Noto'g'ri tanlov")
            
            UI.press_enter()
    
    @staticmethod
    def main():
        try:
            while True:
                UI.show_header()
                
                print(f"{Colors.GREEN}1){Colors.NC} 📀 MySQL boshqaruvi")
                print(f"{Colors.GREEN}2){Colors.NC} 🐘 PostgreSQL boshqaruvi")
                print(f"{Colors.GREEN}3){Colors.NC} 🧹 Kesh tozalash")
                print(f"{Colors.GREEN}4){Colors.NC} ℹ️ Tizim ma'lumotlari")
                print(f"{Colors.GREEN}5){Colors.NC} 🚪 Chiqish")
                
                print(f"\n{Colors.YELLOW}Tanlang [1-5]:{Colors.NC} ")
                choice = input().strip()
                
                if choice == "1":
                    MainMenu.mysql_menu()
                elif choice == "2":
                    MainMenu.postgresql_menu()
                elif choice == "3":
                    CacheManager.clean_cache()
                    UI.press_enter()
                elif choice == "4":
                    Utils.system_info()
                    UI.press_enter()
                elif choice == "5":
                    Logger.info("Dastur yakunlandi")
                    sys.exit(0)
                else:
                    Logger.error("Noto'g'ri tanlov")
                    UI.press_enter()
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Dastur to'xtatildi{Colors.NC}")
            sys.exit(0)

# ============================================================================
# SKRIPTNI ISHGA TUSHIRISH
# ============================================================================

if __name__ == "__main__":
    # Root huquqlarini tekshirish
    if os.geteuid() != 0:
        print(f"{Colors.RED}Bu skript root huquqlari bilan ishga tushirilishi kerak!{Colors.NC}")
        print(f"Foydalanish: {Colors.YELLOW}sudo python3 {sys.argv[0]}{Colors.NC}")
        sys.exit(1)
    
    MainMenu.main()


"""
============================================================================
PROFESSIONAL DATABASE MANAGEMENT SYSTEM
Version: 1.0 (Python Edition)
============================================================================
MySQL va PostgreSQL ni to'liq boshqarish uchun professional vosita
Muallif: Database Administrator
Litsenziya: MIT
============================================================================
"""
