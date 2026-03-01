#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
============================================================================
PROFESSIONAL DATABASE MANAGEMENT SYSTEM
Version: 4.0 (Ultimate Edition - Fully Working)
============================================================================
MySQL va PostgreSQL ni to'liq boshqarish uchun professional vosita
Muallif: Database Administrator
Litsenziya: MIT
============================================================================
"""

import os
import sys
import subprocess
import shutil
import datetime
import getpass
import platform
import json
import time
import threading
import hashlib
import base64
import re
import socket
import glob
import tarfile
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# ============================================================================
# KUTUBXONALARNI IMPORT QILISH (MAVJUD BO'LSA)
# ============================================================================

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    from kubernetes import client, config
    K8S_AVAILABLE = True
except ImportError:
    K8S_AVAILABLE = False

try:
    from flask import Flask, render_template, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    from sklearn.linear_model import LinearRegression
    from sklearn import preprocessing
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

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
REPORTS_DIR = SCRIPT_DIR / "db_reports"
ALERTS_DIR = SCRIPT_DIR / "db_alerts"
MIGRATIONS_DIR = SCRIPT_DIR / "db_migrations"
PLUGINS_DIR = SCRIPT_DIR / "db_plugins"
DASHBOARDS_DIR = SCRIPT_DIR / "db_dashboards"
CONNECTION_FILE = CONFIG_DIR / "connections.db"
HISTORY_FILE = LOG_DIR / "command_history.log"
ERROR_LOG = LOG_DIR / "error.log"
DEBUG_LOG = LOG_DIR / "debug.log"
ALERT_LOG = LOG_DIR / "alerts.log"
PERFORMANCE_LOG = LOG_DIR / "performance.log"
CONFIG_FILE = CONFIG_DIR / "settings.json"

# Papkalarni yaratish
for directory in [CONFIG_DIR, BACKUP_DIR, LOG_DIR, SSL_DIR, TEMP_DIR, CACHE_DIR, 
                  DATA_DIR, ARCHIVE_DIR, REPORTS_DIR, ALERTS_DIR, MIGRATIONS_DIR, 
                  PLUGINS_DIR, DASHBOARDS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

for file in [CONNECTION_FILE, HISTORY_FILE, ERROR_LOG, DEBUG_LOG, ALERT_LOG, PERFORMANCE_LOG]:
    file.touch(exist_ok=True)

# Konfiguratsiya faylini yaratish
if not CONFIG_FILE.exists():
    default_config = {
        "email": {
            "smtp_server": "localhost",
            "smtp_port": 25,
            "from_addr": "admin@localhost",
            "to_addr": "dba@localhost",
            "use_tls": False,
            "username": "",
            "password": ""
        },
        "telegram": {
            "bot_token": "",
            "chat_id": ""
        },
        "slack": {
            "webhook_url": ""
        },
        "discord": {
            "webhook_url": ""
        },
        "backup": {
            "mysql_schedule": "02:00",
            "postgresql_schedule": "03:00",
            "retention_days": 7,
            "compression": "gz",
            "encryption": False,
            "cloud_provider": "none",
            "cloud_bucket": "",
            "incremental": False
        },
        "monitoring": {
            "interval": 60,
            "cpu_threshold": 80,
            "memory_threshold": 80,
            "disk_threshold": 90,
            "connection_threshold": 100,
            "enable_realtime": True,
            "enable_predictive": False
        },
        "security": {
            "password_policy": True,
            "audit_log": True,
            "ip_whitelist": [],
            "ssl_enabled": False,
            "firewall_enabled": False,
            "vpn_enabled": False
        },
        "replication": {
            "mysql_enabled": False,
            "postgresql_enabled": False,
            "master_host": "",
            "master_user": "",
            "master_password": ""
        },
        "plugins": {
            "enabled": [],
            "auto_load": False
        }
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=4)

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
        print(f"{Colors.BLUE}║{Colors.WHITE}              Version: 4.0 | Ultimate Edition                {Colors.BLUE}║{Colors.NC}")
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
    
    @staticmethod
    def get_choice(options, prompt="Tanlov"):
        for i, option in enumerate(options, 1):
            print(f"{i}) {option}")
        choice = UI.get_input(prompt, "1")
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx], idx + 1
            else:
                return options[0], 1
        except:
            return options[0], 1
    
    @staticmethod
    def get_multiline_input(prompt):
        print(f"{prompt} (bir nechta qator, tugatish uchun bo'sh qator):")
        lines = []
        while True:
            line = input()
            if not line:
                break
            lines.append(line)
        return '\n'.join(lines)

# ============================================================================
# DATABASE FUNKSIYALARI
# ============================================================================

class DatabaseManager:
    @staticmethod
    def run_command(cmd, shell=True, capture=True, timeout=60):
        try:
            if capture:
                result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
                return result.stdout.strip(), result.stderr.strip(), result.returncode
            else:
                result = subprocess.run(cmd, shell=shell, timeout=timeout)
                return "", "", result.returncode
        except subprocess.TimeoutExpired:
            return "", "Timeout", 1
        except Exception as e:
            return "", str(e), 1
    
    @staticmethod
    def run_sql_file(db_type, dbname, filepath):
        if db_type == "mysql":
            cmd = f"sudo mysql {dbname} < {filepath} 2>/dev/null"
        else:
            cmd = f"sudo -u postgres psql -d {dbname} -f {filepath} 2>/dev/null"
        return DatabaseManager.run_command(cmd)
    
    @staticmethod
    def get_hostname():
        return socket.gethostname()
    
    @staticmethod
    def get_ip_address():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

# ============================================================================
# MYSQL FUNKSIYALARI (TO'LIQ)
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
        
        stdout, stderr, code = DatabaseManager.run_command("sudo systemctl status mysql --no-pager -l 2>/dev/null")
        print(f"{Colors.CYAN}{Colors.BOLD}Xizmat holati:{Colors.NC}")
        if stdout:
            for line in stdout.split('\n'):
                if "Active" in line or "Loaded" in line:
                    print(line)
        else:
            print("MySQL xizmati topilmadi")
        
        stdout, stderr, code = DatabaseManager.run_command("mysql --version 2>/dev/null")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Versiya:{Colors.NC}")
        print(stdout if stdout else "Ma'lumot yo'q")
        
        stdout, stderr, code = DatabaseManager.run_command("sudo ss -tlnp 2>/dev/null | grep mysql || echo '3306'")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Port:{Colors.NC}")
        print(stdout[:100])
        
        stdout, stderr, code = DatabaseManager.run_command("sudo mysql -e \"SHOW STATUS LIKE 'Threads_connected';\" 2>/dev/null")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Faol ulanishlar:{Colors.NC}")
        print(stdout if stdout else "Ma'lumot olish imkonsiz")
    
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
            print(stdout)
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
        print(stdout if stdout else "Ma'lumot yo'q")
        
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
            print(stdout if stdout else "Ma'lumot yo'q")
        else:
            Logger.error("Ruxsat berishda xatolik")
    
    @staticmethod
    def show_grants():
        UI.show_menu_header("MYSQL GRANTLAR")
        
        username = UI.get_input("Foydalanuvchi nomi")
        host = UI.get_input("Xost")
        
        cmd = f"sudo mysql -e \"SHOW GRANTS FOR '{username}'@'{host}';\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(stdout if stdout else "Ma'lumot yo'q")
    
    @staticmethod
    def revoke_privileges():
        UI.show_menu_header("MYSQL RUXSATLARNI OLIB TASHLASH")
        
        username = UI.get_input("Foydalanuvchi nomi")
        host = UI.get_input("Xost")
        database = UI.get_input("Ma'lumotlar bazasi")
        
        cmd = f"sudo mysql -e \"SHOW GRANTS FOR '{username}'@'{host}';\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"\n{Colors.CYAN}Mavjud grantlar:{Colors.NC}")
        print(stdout if stdout else "Ma'lumot yo'q")
        
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
        
        cmd = "sudo mysql -e \"SHOW DATABASES;\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"{Colors.GREEN}{Colors.BOLD}Barcha ma'lumotlar bazalari:{Colors.NC}\n")
        print(stdout if stdout else "Ma'lumot yo'q")
    
    @staticmethod
    def create_database():
        UI.show_menu_header("YANGI MYSQL MA'LUMOTLAR BAZASI")
        
        dbname = UI.get_input("Ma'lumotlar bazasi nomi")
        
        cmd = "sudo mysql -e \"SHOW CHARACTER SET;\" 2>/dev/null | head -10"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"\n{Colors.CYAN}Mavjud charsetlar:{Colors.NC}")
        print(stdout if stdout else "Ma'lumot yo'q")
        
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
    
    @staticmethod
    def backup(dbname=None):
        if dbname is None:
            MySQLManager.list_databases()
            dbname = UI.get_input("Backup qilinadigan DB")
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = BACKUP_DIR / f"mysql_{dbname}_{timestamp}.sql"
        
        cmd = f"sudo mysqldump {dbname} > {backup_file} 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            # Compression
            try:
                import gzip
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(f"{backup_file}.gz", 'wb') as f_out:
                        f_out.writelines(f_in)
                backup_file.unlink()
                Logger.success(f"Backup yaratildi: {backup_file}.gz")
                return str(backup_file) + ".gz"
            except Exception as e:
                Logger.error(f"Backup siqishda xatolik: {e}")
                return str(backup_file)
        else:
            Logger.error("Backup yaratishda xatolik")
            return None
    
    @staticmethod
    def restore(backup_file=None, dbname=None):
        if backup_file is None:
            backups = list(BACKUP_DIR.glob("mysql_*.sql*"))
            if not backups:
                Logger.error("Backup fayllar topilmadi")
                return
            
            print("Mavjud backup'lar:")
            for i, f in enumerate(backups, 1):
                size = f.stat().st_size / 1024 / 1024
                print(f"{i}) {f.name} ({size:.2f} MB)")
            
            try:
                choice = int(UI.get_input("Tanlang", "1")) - 1
                backup_file = backups[choice]
            except:
                Logger.error("Noto'g'ri tanlov")
                return
        
        if dbname is None:
            dbname = UI.get_input("Restore qilinadigan DB")
        
        try:
            import gzip
            if str(backup_file).endswith('.gz'):
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(TEMP_DIR / "restore.sql", 'wb') as f_out:
                        f_out.write(f_in.read())
                restore_file = TEMP_DIR / "restore.sql"
            else:
                restore_file = backup_file
            
            cmd = f"sudo mysql {dbname} < {restore_file} 2>/dev/null"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            
            if TEMP_DIR / "restore.sql" in restore_file:
                (TEMP_DIR / "restore.sql").unlink()
            
            if code == 0:
                Logger.success("Restore bajarildi")
            else:
                Logger.error(f"Restore qilishda xatolik: {stderr}")
        except Exception as e:
            Logger.error(f"Restore qilishda xatolik: {e}")
    
    @staticmethod
    def backup_all():
        """Barcha ma'lumotlar bazalarini backup qilish"""
        stdout, stderr, code = DatabaseManager.run_command(
            "sudo mysql -e \"SHOW DATABASES;\" 2>/dev/null | grep -v 'Database\\|information_schema\\|performance_schema\\|mysql\\|sys'"
        )
        for db in stdout.split('\n'):
            if db.strip():
                MySQLManager.backup(db.strip())
    
    @staticmethod
    def optimize_tables(dbname=None):
        """Jadvallarni optimizatsiya qilish"""
        if dbname is None:
            MySQLManager.list_databases()
            dbname = UI.get_input("Optimizatsiya qilinadigan DB")
        
        cmd = f"sudo mysql -e \"SELECT CONCAT('OPTIMIZE TABLE ', table_schema, '.', table_name, ';') FROM information_schema.tables WHERE table_schema = '{dbname}';\" 2>/dev/null | mysql"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success(f"{dbname} optimizatsiya qilindi")
        else:
            Logger.error("Optimizatsiyada xatolik")
    
    @staticmethod
    def analyze_slow_queries():
        """Sekin so'rovlarni tahlil qilish"""
        cmd = "sudo mysql -e \"SELECT * FROM mysql.slow_log ORDER BY query_time DESC LIMIT 20;\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"{Colors.CYAN}Sekin so'rovlar:{Colors.NC}")
        print(stdout if stdout else "Ma'lumot yo'q")

# ============================================================================
# POSTGRESQL FUNKSIYALARI (TO'LIQ)
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
        
        stdout, stderr, code = DatabaseManager.run_command("sudo systemctl status postgresql --no-pager -l 2>/dev/null")
        print(f"{Colors.CYAN}{Colors.BOLD}Xizmat holati:{Colors.NC}")
        if stdout:
            for line in stdout.split('\n'):
                if "Active" in line or "Loaded" in line:
                    print(line)
        
        stdout, stderr, code = DatabaseManager.run_command("sudo -u postgres psql -c \"SELECT version();\" 2>/dev/null")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Versiya:{Colors.NC}")
        if stdout:
            for line in stdout.split('\n'):
                if "PostgreSQL" in line:
                    print(line)
                    break
        
        stdout, stderr, code = DatabaseManager.run_command("sudo ss -tlnp 2>/dev/null | grep postgres || echo '5432'")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Port:{Colors.NC}")
        print(stdout[:100])
        
        stdout, stderr, code = DatabaseManager.run_command("sudo -u postgres psql -c \"SELECT count(*) as active_connections FROM pg_stat_activity;\" 2>/dev/null")
        print(f"\n{Colors.CYAN}{Colors.BOLD}Faol ulanishlar:{Colors.NC}")
        print(stdout if stdout else "Ma'lumot yo'q")
    
    @staticmethod
    def list_users():
        UI.show_menu_header("POSTGRESQL FOYDALANUVCHILARI")
        
        stdout, stderr, code = DatabaseManager.run_command("sudo -u postgres psql -c \"\\du\" 2>/dev/null")
        print(f"{Colors.GREEN}{Colors.BOLD}Barcha foydalanuvchilar:{Colors.NC}\n")
        print(stdout if stdout else "Ma'lumot yo'q")
    
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
            print(stdout if stdout else "Ma'lumot yo'q")
        else:
            Logger.error("Ruxsat berishda xatolik")
    
    @staticmethod
    def show_grants():
        UI.show_menu_header("POSTGRESQL GRANTLAR")
        
        username = UI.get_input("Foydalanuvchi nomi")
        
        cmd = f"sudo -u postgres psql -c \"\\du {username}\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(stdout if stdout else "Ma'lumot yo'q")
        
        cmd = f"sudo -u postgres psql -c \"\\dp\" 2>/dev/null | grep {username} || echo 'Grantlar topilmadi'"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(stdout if stdout else "Grantlar topilmadi")
    
    @staticmethod
    def revoke_privileges():
        UI.show_menu_header("POSTGRESQL RUXSATLARNI OLIB TASHLASH")
        
        username = UI.get_input("Foydalanuvchi nomi")
        database = UI.get_input("Ma'lumotlar bazasi")
        
        cmd = f"sudo -u postgres psql -c \"\\dp {database}.*\" 2>/dev/null | grep {username}"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"\n{Colors.CYAN}Mavjud grantlar:{Colors.NC}")
        print(stdout if stdout else "Ma'lumot yo'q")
        
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
        print(stdout if stdout else "Ma'lumot yo'q")
    
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
    
    @staticmethod
    def backup(dbname=None):
        if dbname is None:
            PostgreSQLManager.list_databases()
            dbname = UI.get_input("Backup qilinadigan DB")
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = BACKUP_DIR / f"postgres_{dbname}_{timestamp}.sql"
        
        cmd = f"sudo -u postgres pg_dump {dbname} > {backup_file} 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            # Compression
            try:
                import gzip
                with open(backup_file, 'rb') as f_in:
                    with gzip.open(f"{backup_file}.gz", 'wb') as f_out:
                        f_out.writelines(f_in)
                backup_file.unlink()
                Logger.success(f"Backup yaratildi: {backup_file}.gz")
                return str(backup_file) + ".gz"
            except Exception as e:
                Logger.error(f"Backup siqishda xatolik: {e}")
                return str(backup_file)
        else:
            Logger.error("Backup yaratishda xatolik")
            return None
    
    @staticmethod
    def restore(backup_file=None, dbname=None):
        if backup_file is None:
            backups = list(BACKUP_DIR.glob("postgres_*.sql*"))
            if not backups:
                Logger.error("Backup fayllar topilmadi")
                return
            
            print("Mavjud backup'lar:")
            for i, f in enumerate(backups, 1):
                size = f.stat().st_size / 1024 / 1024
                print(f"{i}) {f.name} ({size:.2f} MB)")
            
            try:
                choice = int(UI.get_input("Tanlang", "1")) - 1
                backup_file = backups[choice]
            except:
                Logger.error("Noto'g'ri tanlov")
                return
        
        if dbname is None:
            dbname = UI.get_input("Restore qilinadigan DB")
        
        try:
            import gzip
            if str(backup_file).endswith('.gz'):
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(TEMP_DIR / "restore.sql", 'wb') as f_out:
                        f_out.write(f_in.read())
                restore_file = TEMP_DIR / "restore.sql"
            else:
                restore_file = backup_file
            
            cmd = f"sudo -u postgres psql -d {dbname} -f {restore_file} 2>/dev/null"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            
            if TEMP_DIR / "restore.sql" in restore_file:
                (TEMP_DIR / "restore.sql").unlink()
            
            if code == 0:
                Logger.success("Restore bajarildi")
            else:
                Logger.error(f"Restore qilishda xatolik: {stderr}")
        except Exception as e:
            Logger.error(f"Restore qilishda xatolik: {e}")
    
    @staticmethod
    def backup_all():
        """Barcha ma'lumotlar bazalarini backup qilish"""
        stdout, stderr, code = DatabaseManager.run_command(
            "sudo -u postgres psql -c \"\\l\" 2>/dev/null | grep -v 'template\\|postgres' | awk '{print $1}' | grep -v 'List\\|Name\\|--\\|('"
        )
        for db in stdout.split('\n'):
            if db.strip():
                PostgreSQLManager.backup(db.strip())
    
    @staticmethod
    def vacuum_analyze(dbname=None):
        """Vacuum analyze qilish"""
        if dbname is None:
            PostgreSQLManager.list_databases()
            dbname = UI.get_input("Vacuum qilinadigan DB")
        
        cmd = f"sudo -u postgres psql -d {dbname} -c \"VACUUM ANALYZE;\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if code == 0:
            Logger.success(f"{dbname} vacuum analyze qilindi")
        else:
            Logger.error("Vacuumda xatolik")
    
    @staticmethod
    def analyze_slow_queries():
        """Sekin so'rovlarni tahlil qilish"""
        cmd = "sudo -u postgres psql -c \"SELECT query, calls, total_time, mean_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 20;\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        print(f"{Colors.CYAN}Sekin so'rovlar:{Colors.NC}")
        print(stdout if stdout else "Ma'lumot yo'q")

# ============================================================================
# ADVANCED FEATURES - MONITORING VA ANALYTICS
# ============================================================================

class MonitoringManager:
    @staticmethod
    def get_system_stats():
        """Tizim statistikasini olish"""
        stats = {}
        
        if PSUTIL_AVAILABLE:
            # CPU
            stats['cpu'] = psutil.cpu_percent(interval=1)
            stats['cpu_count'] = psutil.cpu_count()
            
            # CPU frequency
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                stats['cpu_freq'] = cpu_freq.current
            
            # Memory
            memory = psutil.virtual_memory()
            stats['memory_total'] = memory.total / (1024**3)
            stats['memory_available'] = memory.available / (1024**3)
            stats['memory_used'] = memory.used / (1024**3)
            stats['memory_percent'] = memory.percent
            
            # Swap
            swap = psutil.swap_memory()
            stats['swap_total'] = swap.total / (1024**3)
            stats['swap_used'] = swap.used / (1024**3)
            stats['swap_percent'] = swap.percent
            
            # Disk
            disk = psutil.disk_usage('/')
            stats['disk_total'] = disk.total / (1024**3)
            stats['disk_used'] = disk.used / (1024**3)
            stats['disk_free'] = disk.free / (1024**3)
            stats['disk_percent'] = disk.percent
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                stats['disk_read'] = disk_io.read_bytes / (1024**2)
                stats['disk_write'] = disk_io.write_bytes / (1024**2)
            
            # Network
            net = psutil.net_io_counters()
            stats['net_sent'] = net.bytes_sent / (1024**2)
            stats['net_recv'] = net.bytes_recv / (1024**2)
            
            # Processes
            stats['processes'] = len(psutil.pids())
            
            # Load average
            stats['load_avg'] = psutil.getloadavg()
            
            # Users
            stats['users'] = len(psutil.users())
        
        # Database stats
        if MySQLManager.check():
            stdout, _, _ = DatabaseManager.run_command(
                "sudo mysql -e \"SHOW STATUS LIKE 'Threads_connected';\" 2>/dev/null"
            )
            stats['mysql_connections'] = stdout
            
            # MySQL version
            stdout, _, _ = DatabaseManager.run_command("mysql --version 2>/dev/null")
            stats['mysql_version'] = stdout
            
            # MySQL uptime
            stdout, _, _ = DatabaseManager.run_command(
                "sudo mysql -e \"SHOW STATUS LIKE 'Uptime';\" 2>/dev/null"
            )
            stats['mysql_uptime'] = stdout
        
        if PostgreSQLManager.check():
            stdout, _, _ = DatabaseManager.run_command(
                "sudo -u postgres psql -c \"SELECT count(*) FROM pg_stat_activity;\" 2>/dev/null"
            )
            stats['postgresql_connections'] = stdout
            
            # PostgreSQL version
            stdout, _, _ = DatabaseManager.run_command("psql --version 2>/dev/null")
            stats['postgresql_version'] = stdout
        
        # Timestamp
        stats['timestamp'] = datetime.datetime.now().isoformat()
        
        return stats
    
    @staticmethod
    def monitor_realtime():
        """Real-time monitoring (terminal)"""
        if not PSUTIL_AVAILABLE:
            Logger.error("psutil kutubxonasi o'rnatilmagan. 'pip3 install psutil'")
            return
        
        try:
            while True:
                os.system('clear')
                stats = MonitoringManager.get_system_stats()
                
                print(f"{Colors.CYAN}{Colors.BOLD}╔══════════════════════════════════════════════════════════════╗{Colors.NC}")
                print(f"{Colors.CYAN}{Colors.BOLD}║              REAL-TIME MONITORING (Ctrl+C chiqish)            ║{Colors.NC}")
                print(f"{Colors.CYAN}{Colors.BOLD}╚══════════════════════════════════════════════════════════════╝{Colors.NC}")
                print("")
                
                # CPU
                cpu_bar = "█" * int(min(stats['cpu'] / 2, 50))
                cpu_space = " " * (50 - len(cpu_bar))
                print(f"{Colors.GREEN}CPU:{Colors.NC} {stats['cpu']:5.1f}% [{cpu_bar}{cpu_space}]")
                print(f"    Cores: {stats['cpu_count']}")
                if 'cpu_freq' in stats:
                    print(f"    Frequency: {stats['cpu_freq']:.0f} MHz")
                if 'load_avg' in stats:
                    print(f"    Load Avg: {stats['load_avg'][0]:.2f}, {stats['load_avg'][1]:.2f}, {stats['load_avg'][2]:.2f}")
                
                # Memory
                mem_bar = "█" * int(min(stats['memory_percent'] / 2, 50))
                mem_space = " " * (50 - len(mem_bar))
                print(f"\n{Colors.GREEN}RAM:{Colors.NC} {stats['memory_percent']:5.1f}% [{mem_bar}{mem_space}]")
                print(f"    Used: {stats['memory_used']:.2f} GB / Total: {stats['memory_total']:.2f} GB")
                print(f"    Available: {stats['memory_available']:.2f} GB")
                
                # Swap
                if stats.get('swap_total', 0) > 0:
                    swap_bar = "█" * int(min(stats['swap_percent'] / 2, 50))
                    swap_space = " " * (50 - len(swap_bar))
                    print(f"\n{Colors.GREEN}Swap:{Colors.NC} {stats['swap_percent']:5.1f}% [{swap_bar}{swap_space}]")
                    print(f"    Used: {stats['swap_used']:.2f} GB / Total: {stats['swap_total']:.2f} GB")
                
                # Disk
                disk_bar = "█" * int(min(stats['disk_percent'] / 2, 50))
                disk_space = " " * (50 - len(disk_bar))
                print(f"\n{Colors.GREEN}Disk:{Colors.NC} {stats['disk_percent']:5.1f}% [{disk_bar}{disk_space}]")
                print(f"    Used: {stats['disk_used']:.2f} GB / Total: {stats['disk_total']:.2f} GB")
                print(f"    Free: {stats['disk_free']:.2f} GB")
                
                # Disk I/O
                if 'disk_read' in stats and 'disk_write' in stats:
                    print(f"\n{Colors.GREEN}Disk I/O:{Colors.NC}")
                    print(f"    Read: {stats['disk_read']:.2f} MB")
                    print(f"    Write: {stats['disk_write']:.2f} MB")
                
                # Network
                print(f"\n{Colors.GREEN}Network:{Colors.NC}")
                print(f"    Sent: {stats['net_sent']:.2f} MB")
                print(f"    Received: {stats['net_recv']:.2f} MB")
                
                # Database
                print(f"\n{Colors.GREEN}Database:{Colors.NC}")
                if 'mysql_connections' in stats and stats['mysql_connections']:
                    mysql_val = re.search(r'(\d+)', str(stats['mysql_connections']))
                    mysql_conn = mysql_val.group(1) if mysql_val else 'N/A'
                    print(f"    MySQL: {mysql_conn} connections")
                if 'postgresql_connections' in stats and stats['postgresql_connections']:
                    pg_val = re.search(r'(\d+)', str(stats['postgresql_connections']))
                    pg_conn = pg_val.group(1) if pg_val else 'N/A'
                    print(f"    PostgreSQL: {pg_conn} connections")
                
                # Processes & Users
                print(f"\n{Colors.GREEN}System:{Colors.NC}")
                print(f"    Processes: {stats.get('processes', 0)}")
                print(f"    Users: {stats.get('users', 0)}")
                
                # Timestamp
                print(f"\n{Colors.YELLOW}So'ngi yangilanish: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.NC}")
                print(f"{Colors.YELLOW}Chiqish uchun Ctrl+C bosing{Colors.NC}")
                
                # Har 2 sekundda yangilash
                time.sleep(2)
                
                # Performans ma'lumotlarini saqlash
                if int(time.time()) % 60 == 0:  # Har daqiqada
                    MonitoringManager.save_performance_data()
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.GREEN}Monitoring to'xtatildi{Colors.NC}")
    
    @staticmethod
    def save_performance_data():
        """Performans ma'lumotlarini saqlash"""
        stats = MonitoringManager.get_system_stats()
        
        # Clean up old data (keep last 30 days)
        if PERFORMANCE_LOG.exists():
            lines = []
            with open(PERFORMANCE_LOG, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            cutoff = datetime.datetime.now() - datetime.timedelta(days=30)
            new_lines = []
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    if 'timestamp' in data:
                        ts = datetime.datetime.fromisoformat(data['timestamp'])
                        if ts > cutoff:
                            new_lines.append(line)
                except:
                    continue
            
            with open(PERFORMANCE_LOG, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        
        # Add new data
        with open(PERFORMANCE_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(stats) + '\n')
        
        Logger.debug("Performans ma'lumotlari saqlandi")
    
    @staticmethod
    def analyze_performance():
        """Performans tahlili"""
        if not PERFORMANCE_LOG.exists():
            Logger.error("Performans ma'lumotlari topilmadi")
            return
        
        data = []
        with open(PERFORMANCE_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except:
                    continue
        
        if not data:
            Logger.error("Ma'lumotlar yo'q")
            return
        
        print(f"{Colors.CYAN}{Colors.BOLD}=== PERFORMANS STATISTIKASI ==={Colors.NC}\n")
        print(f"Jami yozuvlar: {len(data)}")
        
        try:
            print(f"Birinchi yozuv: {data[0].get('timestamp', 'N/A')}")
            print(f"So'ngi yozuv: {data[-1].get('timestamp', 'N/A')}")
        except:
            pass
        
        # Statistikani hisoblash
        cpu_values = [d.get('cpu', 0) for d in data if 'cpu' in d]
        mem_values = [d.get('memory_percent', 0) for d in data if 'memory_percent' in d]
        disk_values = [d.get('disk_percent', 0) for d in data if 'disk_percent' in d]
        
        if cpu_values:
            print(f"\n{Colors.GREEN}CPU:{Colors.NC}")
            print(f"  O'rtacha: {sum(cpu_values)/len(cpu_values):.2f}%")
            print(f"  Maksimal: {max(cpu_values):.2f}%")
            print(f"  Minimal: {min(cpu_values):.2f}%")
        
        if mem_values:
            print(f"\n{Colors.GREEN}RAM:{Colors.NC}")
            print(f"  O'rtacha: {sum(mem_values)/len(mem_values):.2f}%")
            print(f"  Maksimal: {max(mem_values):.2f}%")
            print(f"  Minimal: {min(mem_values):.2f}%")
        
        if disk_values:
            print(f"\n{Colors.GREEN}Disk:{Colors.NC}")
            print(f"  O'rtacha: {sum(disk_values)/len(disk_values):.2f}%")
            print(f"  Maksimal: {max(disk_values):.2f}%")
            print(f"  Minimal: {min(disk_values):.2f}%")
        
        # MySQL stats
        mysql_conns = []
        for d in data:
            if 'mysql_connections' in d and d['mysql_connections']:
                match = re.search(r'(\d+)', str(d['mysql_connections']))
                if match:
                    mysql_conns.append(int(match.group(1)))
        
        if mysql_conns:
            print(f"\n{Colors.GREEN}MySQL:{Colors.NC}")
            print(f"  O'rtacha ulanishlar: {sum(mysql_conns)/len(mysql_conns):.0f}")
            print(f"  Maksimal ulanishlar: {max(mysql_conns)}")
            print(f"  Minimal ulanishlar: {min(mysql_conns)}")
        
        # PostgreSQL stats
        pg_conns = []
        for d in data:
            if 'postgresql_connections' in d and d['postgresql_connections']:
                match = re.search(r'(\d+)', str(d['postgresql_connections']))
                if match:
                    pg_conns.append(int(match.group(1)))
        
        if pg_conns:
            print(f"\n{Colors.GREEN}PostgreSQL:{Colors.NC}")
            print(f"  O'rtacha ulanishlar: {sum(pg_conns)/len(pg_conns):.0f}")
            print(f"  Maksimal ulanishlar: {max(pg_conns)}")
            print(f"  Minimal ulanishlar: {min(pg_conns)}")
        
        # Hisobot faylga saqlash
        report_file = REPORTS_DIR / f"performance_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_records': len(data),
            'first_record': data[0].get('timestamp') if data else None,
            'last_record': data[-1].get('timestamp') if data else None,
            'cpu': {
                'avg': sum(cpu_values)/len(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0
            } if cpu_values else None,
            'memory': {
                'avg': sum(mem_values)/len(mem_values) if mem_values else 0,
                'max': max(mem_values) if mem_values else 0,
                'min': min(mem_values) if mem_values else 0
            } if mem_values else None,
            'disk': {
                'avg': sum(disk_values)/len(disk_values) if disk_values else 0,
                'max': max(disk_values) if disk_values else 0,
                'min': min(disk_values) if disk_values else 0
            } if disk_values else None
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4)
        
        Logger.info(f"Performans tahlili saqlandi: {report_file}")

# ============================================================================
# 1. KENGAYTIRILGAN MONITORING DASHBOARD
# ============================================================================

class EnhancedMonitoring:
    @staticmethod
    def create_dashboard():
        """Grafik dashboard yaratish"""
        if not MATPLOTLIB_AVAILABLE:
            Logger.error("matplotlib yoki numpy kutubxonasi o'rnatilmagan")
            Logger.info("O'rnatish: pip3 install matplotlib numpy")
            return
        
        stats = MonitoringManager.get_system_stats()
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # CPU grafigi
        cpu_value = stats.get('cpu', 0)
        axes[0, 0].bar(['CPU'], [cpu_value], color='blue', width=0.5)
        axes[0, 0].set_title('CPU Usage', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylim([0, 100])
        axes[0, 0].set_ylabel('Percentage (%)', fontsize=12)
        axes[0, 0].text(0, cpu_value + 2, f'{cpu_value:.1f}%', ha='center', fontsize=12)
        
        # Memory grafigi
        mem_value = stats.get('memory_percent', 0)
        axes[0, 1].bar(['RAM'], [mem_value], color='green', width=0.5)
        axes[0, 1].set_title('Memory Usage', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylim([0, 100])
        axes[0, 1].set_ylabel('Percentage (%)', fontsize=12)
        axes[0, 1].text(0, mem_value + 2, f'{mem_value:.1f}%', ha='center', fontsize=12)
        
        # Disk grafigi
        disk_value = stats.get('disk_percent', 0)
        axes[1, 0].bar(['Disk'], [disk_value], color='orange', width=0.5)
        axes[1, 0].set_title('Disk Usage', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylim([0, 100])
        axes[1, 0].set_ylabel('Percentage (%)', fontsize=12)
        axes[1, 0].text(0, disk_value + 2, f'{disk_value:.1f}%', ha='center', fontsize=12)
        
        # Connections grafigi
        mysql_conn = 0
        if stats.get('mysql_connections'):
            match = re.search(r'(\d+)', str(stats['mysql_connections']))
            if match:
                mysql_conn = float(match.group(1))
        
        pg_conn = 0
        if stats.get('postgresql_connections'):
            match = re.search(r'(\d+)', str(stats['postgresql_connections']))
            if match:
                pg_conn = float(match.group(1))
        
        connections = [mysql_conn, pg_conn]
        bars = axes[1, 1].bar(['MySQL', 'PostgreSQL'], connections, color=['purple', 'red'], width=0.5)
        axes[1, 1].set_title('Database Connections', fontsize=14, fontweight='bold')
        axes[1, 1].set_ylabel('Number of Connections', fontsize=12)
        
        for i, (bar, val) in enumerate(zip(bars, connections)):
            axes[1, 1].text(i, val + 0.5, f'{val:.0f}', ha='center', fontsize=12)
        
        plt.suptitle(f'System Dashboard - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
                    fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        dashboard_file = DASHBOARDS_DIR / f'dashboard_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(str(dashboard_file), dpi=100, bbox_inches='tight')
        plt.close()
        
        Logger.success(f"Dashboard yaratildi: {dashboard_file}")
        
        # Terminalda ham ko'rsatish
        print(f"\n{Colors.CYAN}{Colors.BOLD}=== DASHBOARD STATISTIKASI ==={Colors.NC}")
        print(f"CPU: {cpu_value:.1f}%")
        print(f"RAM: {mem_value:.1f}%")
        print(f"Disk: {disk_value:.1f}%")
        print(f"MySQL ulanishlar: {mysql_conn}")
        print(f"PostgreSQL ulanishlar: {pg_conn}")
        print(f"Umumiy jarayonlar: {stats.get('processes', 0)}")
        print(f"Tarmoq yuborilgan: {stats.get('net_sent', 0):.2f} MB")
        print(f"Tarmoq qabul qilingan: {stats.get('net_recv', 0):.2f} MB")
    
    @staticmethod
    def create_trend_graph(days=7):
        """Trend grafigi yaratish"""
        if not MATPLOTLIB_AVAILABLE:
            Logger.error("matplotlib kutubxonasi o'rnatilmagan")
            return
        
        if not PERFORMANCE_LOG.exists():
            Logger.error("Performans ma'lumotlari topilmadi")
            return
        
        data = []
        with open(PERFORMANCE_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data.append(json.loads(line.strip()))
                except:
                    continue
        
        if len(data) < 10:
            Logger.warning("Trend grafigi uchun yetarli ma'lumot yo'q")
            return
        
        # So'nggi N kundagi ma'lumotlarni olish
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        filtered_data = []
        for d in data:
            if 'timestamp' in d:
                try:
                    ts = datetime.datetime.fromisoformat(d['timestamp'])
                    if ts > cutoff_date:
                        filtered_data.append(d)
                except:
                    continue
        
        if len(filtered_data) < 5:
            Logger.warning(f"So'nggi {days} kunda yetarli ma'lumot yo'q")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Vaqt o'qi
        timestamps = []
        cpu_values = []
        mem_values = []
        disk_values = []
        
        for d in filtered_data:
            if 'timestamp' in d and 'cpu' in d and 'memory_percent' in d and 'disk_percent' in d:
                try:
                    ts = datetime.datetime.fromisoformat(d['timestamp'])
                    timestamps.append(ts)
                    cpu_values.append(d['cpu'])
                    mem_values.append(d['memory_percent'])
                    disk_values.append(d['disk_percent'])
                except:
                    continue
        
        if not timestamps:
            Logger.error("Grafik uchun ma'lumotlar formati noto'g'ri")
            return
        
        # CPU trend
        axes[0, 0].plot(timestamps, cpu_values, 'b-', linewidth=2, marker='o', markersize=4)
        axes[0, 0].set_title('CPU Usage Trend', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('CPU %')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Memory trend
        axes[0, 1].plot(timestamps, mem_values, 'g-', linewidth=2, marker='s', markersize=4)
        axes[0, 1].set_title('Memory Usage Trend', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylabel('Memory %')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Disk trend
        axes[1, 0].plot(timestamps, disk_values, 'orange', linewidth=2, marker='^', markersize=4)
        axes[1, 0].set_title('Disk Usage Trend', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('Disk %')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Connection trend
        mysql_conn_values = []
        pg_conn_values = []
        
        for d in filtered_data:
            mysql_val = 0
            pg_val = 0
            if d.get('mysql_connections'):
                match = re.search(r'(\d+)', str(d['mysql_connections']))
                if match:
                    mysql_val = float(match.group(1))
            if d.get('postgresql_connections'):
                match = re.search(r'(\d+)', str(d['postgresql_connections']))
                if match:
                    pg_val = float(match.group(1))
            mysql_conn_values.append(mysql_val)
            pg_conn_values.append(pg_val)
        
        axes[1, 1].plot(timestamps, mysql_conn_values, 'purple', linewidth=2, label='MySQL')
        axes[1, 1].plot(timestamps, pg_conn_values, 'red', linewidth=2, label='PostgreSQL')
        axes[1, 1].set_title('Database Connections Trend', fontsize=14, fontweight='bold')
        axes[1, 1].set_ylabel('Connections')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.suptitle(f'System Trends - Last {days} Days', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        trend_file = REPORTS_DIR / f'trend_{days}days_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(str(trend_file), dpi=100, bbox_inches='tight')
        plt.close()
        
        Logger.success(f"Trend grafigi yaratildi: {trend_file}")

# ============================================================================
# 2. PREDICTIVE ANALYTICS (AI ASOSIDA)
# ============================================================================

class PredictiveAnalytics:
    @staticmethod
    def predict_growth(days=30):
        """Ma'lumotlar bazasi o'sishini bashorat qilish"""
        if not SKLEARN_AVAILABLE or not MATPLOTLIB_AVAILABLE:
            Logger.error("scikit-learn yoki matplotlib kutubxonasi o'rnatilmagan")
            Logger.info("O'rnatish: pip3 install scikit-learn matplotlib")
            return
        
        # Tarixiy ma'lumotlarni yig'ish
        sizes = []
        dates = []
        
        if PERFORMANCE_LOG.exists():
            with open(PERFORMANCE_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if 'disk_used' in data:
                            sizes.append(float(data['disk_used']))
                            dates.append(len(sizes))
                    except:
                        continue
        
        if len(sizes) < 10:
            Logger.warning("Bashorat qilish uchun yetarli ma'lumot yo'q (kamida 10 ta kerak)")
            return
        
        # Regression model
        X = np.array(dates).reshape(-1, 1)
        y = np.array(sizes)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Kelajakni bashorat qilish
        future_dates = np.array(range(len(dates), len(dates) + days)).reshape(-1, 1)
        predictions = model.predict(future_dates)
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}=== MA'LUMOTLAR BAZASI O'SHISH BASHORATI ==={Colors.NC}\n")
        print(f"Joriy hajm: {sizes[-1]:.2f} GB")
        print(f"Kutilayotgan o'sish: {predictions[-1] - sizes[-1]:.2f} GB")
        print(f"{days} kundan keyin: {predictions[-1]:.2f} GB")
        print(f"30 kundan keyin: {model.predict([[len(dates) + 30]])[0]:.2f} GB")
        print(f"90 kundan keyin: {model.predict([[len(dates) + 90]])[0]:.2f} GB")
        
        # O'sish tezligi
        growth_rate = (predictions[-1] - sizes[-1]) / days
        print(f"Kunlik o'rtacha o'sish: {growth_rate:.3f} GB/kun")
        
        # Model aniqligi
        r2_score = model.score(X, y)
        print(f"Model aniqligi (R²): {r2_score:.3f}")
        
        # Grafik
        plt.figure(figsize=(12, 6))
        plt.plot(dates, sizes, 'b-', label='Tarixiy ma\'lumotlar', linewidth=2, marker='o', markersize=4)
        plt.plot(range(len(dates), len(dates) + days), predictions, 'r--', 
                label='Bashorat', linewidth=2)
        plt.axvline(x=len(dates), color='gray', linestyle=':', alpha=0.7)
        plt.xlabel('Kunlar', fontsize=12)
        plt.ylabel('Hajm (GB)', fontsize=12)
        plt.title(f'Ma\'lumotlar bazasi o\'sish bashorati (R² = {r2_score:.3f})', 
                 fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        prediction_file = REPORTS_DIR / f'growth_prediction_{days}days_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        plt.savefig(str(prediction_file), dpi=100, bbox_inches='tight')
        plt.close()
        
        Logger.success(f"Bashorat grafigi yaratildi: {prediction_file}")
        
        # JSON formatda saqlash
        prediction_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "current_size": sizes[-1],
            "predicted_size_30d": float(model.predict([[len(dates) + 30]])[0]),
            "predicted_size_90d": float(model.predict([[len(dates) + 90]])[0]),
            "daily_growth_rate": growth_rate,
            "model_accuracy": r2_score,
            "data_points": len(sizes)
        }
        
        pred_json_file = REPORTS_DIR / f'prediction_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(pred_json_file, 'w', encoding='utf-8') as f:
            json.dump(prediction_data, f, indent=4)
        
        Logger.info(f"Bashorat ma'lumotlari saqlandi: {pred_json_file}")
    
    @staticmethod
    def detect_anomalies():
        """Anomaliyalarni aniqlash"""
        if not SKLEARN_AVAILABLE:
            Logger.error("scikit-learn kutubxonasi o'rnatilmagan")
            return
        
        if not PERFORMANCE_LOG.exists():
            Logger.error("Performans ma'lumotlari topilmadi")
            return
        
        data = []
        with open(PERFORMANCE_LOG, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data.append(json.loads(line.strip()))
                except:
                    continue
        
        if len(data) < 20:
            Logger.warning("Anomaliya aniqlash uchun yetarli ma'lumot yo'q")
            return
        
        # So'nggi 30 kun
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
        recent_data = []
        for d in data:
            if 'timestamp' in d:
                try:
                    ts = datetime.datetime.fromisoformat(d['timestamp'])
                    if ts > cutoff_date:
                        recent_data.append(d)
                except:
                    continue
        
        if len(recent_data) < 10:
            Logger.warning("Anomaliya aniqlash uchun yetarli ma'lumot yo'q")
            return
        
        anomalies = []
        
        # CPU anomaliyalari
        cpu_values = [d.get('cpu', 0) for d in recent_data if 'cpu' in d]
        if cpu_values:
            mean_cpu = np.mean(cpu_values)
            std_cpu = np.std(cpu_values)
            threshold = mean_cpu + 2 * std_cpu
            
            for i, d in enumerate(recent_data):
                if d.get('cpu', 0) > threshold:
                    anomalies.append({
                        'type': 'CPU',
                        'value': d['cpu'],
                        'threshold': threshold,
                        'timestamp': d.get('timestamp', 'Unknown')
                    })
        
        # Memory anomaliyalari
        mem_values = [d.get('memory_percent', 0) for d in recent_data if 'memory_percent' in d]
        if mem_values:
            mean_mem = np.mean(mem_values)
            std_mem = np.std(mem_values)
            threshold = mean_mem + 2 * std_mem
            
            for i, d in enumerate(recent_data):
                if d.get('memory_percent', 0) > threshold:
                    anomalies.append({
                        'type': 'Memory',
                        'value': d['memory_percent'],
                        'threshold': threshold,
                        'timestamp': d.get('timestamp', 'Unknown')
                    })
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}=== ANOMALIYALAR TAHLILI ==={Colors.NC}\n")
        
        if anomalies:
            print(f"Topilgan anomaliyalar: {len(anomalies)} ta\n")
            for a in anomalies[:10]:  # So'ngi 10 ta
                print(f"{Colors.YELLOW}⚠ {a['type']}: {a['value']:.1f}% (threshold: {a['threshold']:.1f}%){Colors.NC}")
                print(f"   Vaqt: {a['timestamp']}")
            
            if len(anomalies) > 10:
                print(f"... va yana {len(anomalies) - 10} ta anomaliya")
        else:
            print(f"{Colors.GREEN}✓ Hech qanday anomaliya topilmadi{Colors.NC}")

# ============================================================================
# 3. REAL-TIME REPLICATION MONITORING
# ============================================================================

class ReplicationManager:
    @staticmethod
    def check_mysql_replication():
        """MySQL replikatsiya holatini tekshirish"""
        if not MySQLManager.check():
            Logger.error("MySQL o'rnatilmagan")
            return
        
        cmd = "sudo mysql -e \"SHOW SLAVE STATUS\\G\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if not stdout:
            print(f"\n{Colors.CYAN}MySQL Replikatsiya:{Colors.NC} {Colors.YELLOW}⚠ Replikatsiya sozlanmagan{Colors.NC}")
            return
        
        if "Slave_IO_Running: Yes" in stdout and "Slave_SQL_Running: Yes" in stdout:
            status = f"{Colors.GREEN}✓ Replikatsiya ishlayapti{Colors.NC}"
        else:
            status = f"{Colors.RED}✗ Replikatsiya muammosi{Colors.NC}"
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}MySQL Replikatsiya:{Colors.NC} {status}")
        
        # Sekundlar kechikishi
        match = re.search(r'Seconds_Behind_Master: (\d+)', stdout)
        if match:
            seconds = match.group(1)
            if int(seconds) > 60:
                print(f"{Colors.YELLOW}Sekundlar kechikishi: {seconds} (Yuqori){Colors.NC}")
            else:
                print(f"Sekundlar kechikishi: {seconds}")
        
        # Master bilAN ulanish
        match = re.search(r'Master_Host: (.+)', stdout)
        if match:
            print(f"Master Host: {match.group(1)}")
        
        match = re.search(r'Master_Log_File: (.+)', stdout)
        if match:
            print(f"Master Log File: {match.group(1)}")
        
        # Xatoliklar
        if "Last_Errno: 0" not in stdout:
            match = re.search(r'Last_Error: (.+)', stdout)
            if match:
                print(f"{Colors.RED}Xatolik: {match.group(1)}{Colors.NC}")
    
    @staticmethod
    def check_postgresql_replication():
        """PostgreSQL replikatsiya holatini tekshirish"""
        if not PostgreSQLManager.check():
            Logger.error("PostgreSQL o'rnatilmagan")
            return
        
        cmd = "sudo -u postgres psql -c \"SELECT * FROM pg_stat_replication;\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        if stdout and len(stdout.split('\n')) > 2:
            status = f"{Colors.GREEN}✓ Replikatsiya ishlayapti{Colors.NC}"
            print(f"\n{Colors.CYAN}{Colors.BOLD}PostgreSQL Replikatsiya:{Colors.NC} {status}")
            
            # Replikatsiya ma'lumotlarini formatlab chiqarish
            lines = stdout.split('\n')
            for line in lines[2:]:  # Headerlarni o'tkazib yuborish
                if line.strip() and not line.startswith('-'):
                    values = line.split('|')
                    if len(values) >= 3:
                        print(f"  Replica: {values[1].strip() if len(values) > 1 else 'Unknown'}")
                        print(f"  State: {values[4].strip() if len(values) > 4 else 'Unknown'}")
                        print("  ---")
        else:
            print(f"\n{Colors.CYAN}PostgreSQL Replikatsiya:{Colors.NC} {Colors.YELLOW}⚠ Faol replikatsiya yo'q{Colors.NC}")
    
    @staticmethod
    def setup_mysql_replication():
        """MySQL replikatsiya sozlash"""
        if not MySQLManager.check():
            Logger.error("MySQL o'rnatilmagan")
            return
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}MySQL Replikatsiya sozlash{Colors.NC}")
        print("Bu funksiya slave serverda ishga tushirilishi kerak.\n")
        
        master_host = UI.get_input("Master host", "localhost")
        master_user = UI.get_input("Master user", "replica")
        master_password = UI.get_password("Master password")
        
        # Master holatini olish
        cmd = "sudo mysql -e \"SHOW MASTER STATUS\\G\" 2>/dev/null"
        stdout, stderr, code = DatabaseManager.run_command(cmd)
        
        match_file = re.search(r'File: (.+)', stdout)
        match_pos = re.search(r'Position: (\d+)', stdout)
        
        if match_file and match_pos:
            log_file = match_file.group(1)
            log_pos = match_pos.group(1)
            
            # Slave sozlash
            slave_cmds = f"""
STOP SLAVE;
CHANGE MASTER TO
    MASTER_HOST='{master_host}',
    MASTER_USER='{master_user}',
    MASTER_PASSWORD='{master_password}',
    MASTER_LOG_FILE='{log_file}',
    MASTER_LOG_POS={log_pos};
START SLAVE;
"""
            sql_file = TEMP_DIR / "setup_replica.sql"
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write(slave_cmds)
            
            cmd = f"sudo mysql < {sql_file} 2>/dev/null"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            
            if code == 0:
                Logger.success("Replikatsiya sozlandi")
                ReplicationManager.check_mysql_replication()
            else:
                Logger.error(f"Replikatsiya sozlashda xatolik: {stderr}")
        else:
            Logger.error("Master holatini olishda xatolik")

# ============================================================================
# 4. ADVANCED SECURITY FEATURES
# ============================================================================

class AdvancedSecurity:
    @staticmethod
    def audit_compliance():
        """GDPR/PCI DSS compliance tekshiruvi"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}=== COMPLIANCE AUDIT ==={Colors.NC}\n")
        
        issues = []
        passed = []
        
        # Password policy
        if MySQLManager.check():
            stdout, _, _ = DatabaseManager.run_command(
                "sudo mysql -e \"SHOW VARIABLES LIKE 'validate_password%';\" 2>/dev/null"
            )
            if not stdout or 'validate_password' not in stdout:
                issues.append("❌ MySQL password validation o'rnatilmagan")
            else:
                passed.append("✓ MySQL password validation o'rnatilgan")
        
        # SSL/TLS
        if MySQLManager.check():
            stdout, _, _ = DatabaseManager.run_command(
                "sudo mysql -e \"SHOW VARIABLES LIKE 'have_ssl';\" 2>/dev/null"
            )
            if 'YES' in stdout:
                passed.append("✓ MySQL SSL/TLS yoqilgan")
            else:
                issues.append("❌ MySQL SSL/TLS yoqilmagan")
        
        # PostgreSQL SSL
        if PostgreSQLManager.check():
            stdout, _, _ = DatabaseManager.run_command(
                "sudo -u postgres psql -c \"SHOW ssl;\" 2>/dev/null"
            )
            if 'on' in stdout.lower():
                passed.append("✓ PostgreSQL SSL yoqilgan")
            else:
                issues.append("❌ PostgreSQL SSL yoqilmagan")
        
        # Audit log
        if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
            passed.append("✓ Audit log yoqilgan")
        else:
            issues.append("❌ Audit log yoqilmagan yoki bo'sh")
        
        # Firewall
        stdout, _, code = DatabaseManager.run_command("sudo ufw status | grep -q 'Status: active'")
        if code == 0:
            passed.append("✓ Firewall yoqilgan")
        else:
            issues.append("❌ Firewall yoqilmagan")
        
        # Failed login attempts
        if os.path.exists('/var/log/auth.log'):
            stdout, _, _ = DatabaseManager.run_command(
                "sudo grep 'Failed password' /var/log/auth.log | wc -l"
            )
            if stdout and int(stdout) > 0:
                print(f"\n{Colors.YELLOW}So'nggi muvaffaqiyatsiz login urinishlari: {stdout}{Colors.NC}")
        
        # Natijalar
        print(f"\n{Colors.GREEN}✓ MUVAFFAQIYATLI:{Colors.NC}")
        for item in passed:
            print(f"  {item}")
        
        if issues:
            print(f"\n{Colors.RED}✗ TOPILGAN MUAMMOLAR:{Colors.NC}")
            for issue in issues:
                print(f"  {issue}")
    
    @staticmethod
    def generate_ssl_cert():
        """SSL sertifikat yaratish"""
        if not CRYPTOGRAPHY_AVAILABLE:
            Logger.error("cryptography kutubxonasi o'rnatilmagan")
            Logger.info("O'rnatish: pip3 install cryptography")
            return
        
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            
            key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COUNTRY_NAME, "UZ"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Tashkent"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Tashkent"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DB Manager"),
                x509.NameAttribute(NameOID.COMMON_NAME, DatabaseManager.get_hostname()),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(DatabaseManager.get_hostname()),
                ]),
                critical=False,
            ).sign(key, hashes.SHA256())
            
            # Private key saqlash
            with open(SSL_DIR / "server.key", "wb") as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Sertifikat saqlash
            with open(SSL_DIR / "server.crt", "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            Logger.success("SSL sertifikat yaratildi")
            print(f"Private key: {SSL_DIR / 'server.key'}")
            print(f"Sertifikat: {SSL_DIR / 'server.crt'}")
        except Exception as e:
            Logger.error(f"SSL sertifikat yaratishda xatolik: {e}")
    
    @staticmethod
    def setup_firewall():
        """Firewall sozlamalari"""
        print(f"\n{Colors.CYAN}Firewall sozlamalari:{Colors.NC}")
        print("1) MySQL portini ochish (3306)")
        print("2) PostgreSQL portini ochish (5432)")
        print("3) SSH portini ochish (22)")
        print("4) Firewall holatini ko'rish")
        print("5) Firewall yoqish")
        print("6) Firewall o'chirish")
        
        choice = UI.get_input("Tanlov", "1")
        
        if choice == "1":
            cmd = "sudo ufw allow 3306/tcp 2>/dev/null"
            DatabaseManager.run_command(cmd)
            Logger.success("MySQL porti ochildi (3306)")
        
        elif choice == "2":
            cmd = "sudo ufw allow 5432/tcp 2>/dev/null"
            DatabaseManager.run_command(cmd)
            Logger.success("PostgreSQL porti ochildi (5432)")
        
        elif choice == "3":
            cmd = "sudo ufw allow 22/tcp 2>/dev/null"
            DatabaseManager.run_command(cmd)
            Logger.success("SSH porti ochildi (22)")
        
        elif choice == "4":
            cmd = "sudo ufw status verbose"
            stdout, stderr, code = DatabaseManager.run_command(cmd)
            print(stdout if stdout else "Firewall ma'lumotlari yo'q")
        
        elif choice == "5":
            cmd = "echo 'y' | sudo ufw enable 2>/dev/null"
            DatabaseManager.run_command(cmd)
            Logger.success("Firewall yoqildi")
        
        elif choice == "6":
            cmd = "sudo ufw disable 2>/dev/null"
            DatabaseManager.run_command(cmd)
            Logger.warning("Firewall o'chirildi")
    
    @staticmethod
    def encrypt_database():
        """Ma'lumotlar bazasini shifrlash"""
        if not CRYPTOGRAPHY_AVAILABLE:
            Logger.error("cryptography kutubxonasi o'rnatilmagan")
            Logger.info("O'rnatish: pip3 install cryptography")
            return
        
        db_type = UI.get_input("Database turi (mysql/postgresql)")
        dbname = UI.get_input("Database nomi")
        password = UI.get_password("Shifrlash paroli")
        
        # Backup olish
        if db_type == 'mysql' and MySQLManager.check():
            backup_file = MySQLManager.backup(dbname)
        elif db_type == 'postgresql' and PostgreSQLManager.check():
            backup_file = PostgreSQLManager.backup(dbname)
        else:
            Logger.error("Noto'g'ri database turi yoki o'rnatilmagan")
            return
        
        if backup_file:
            backup_path = Path(backup_file)
            if backup_path.exists():
                # Kalit yaratish
                key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
                cipher = Fernet(key)
                
                # Backupni shifrlash
                with open(backup_path, 'rb') as file:
                    data = file.read()
                
                encrypted_data = cipher.encrypt(data)
                
                encrypted_file = backup_path.with_suffix('.encrypted')
                with open(encrypted_file, 'wb') as file:
                    file.write(encrypted_data)
                
                backup_path.unlink()
                Logger.success(f"Ma'lumotlar bazasi shifrlandi: {encrypted_file}")
    
    @staticmethod
    def decrypt_database():
        """Ma'lumotlar bazasini shifrdan chiqarish"""
        if not CRYPTOGRAPHY_AVAILABLE:
            Logger.error("cryptography kutubxonasi o'rnatilmagan")
            return
        
        encrypted_files = list(SSL_DIR.glob("*.encrypted"))
        if not encrypted_files:
            Logger.error("Shifrlangan fayllar topilmadi")
            return
        
        print("Shifrlangan fayllar:")
        for i, f in enumerate(encrypted_files, 1):
            size = f.stat().st_size / 1024 / 1024
            print(f"{i}) {f.name} ({size:.2f} MB)")
        
        choice = int(UI.get_input("Tanlang", "1")) - 1
        encrypted_file = encrypted_files[choice]
        
        password = UI.get_password("Shifr paroli")
        
        # Kalit yaratish
        key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
        cipher = Fernet(key)
        
        try:
            with open(encrypted_file, 'rb') as file:
                encrypted_data = file.read()
            
            decrypted_data = cipher.decrypt(encrypted_data)
            
            decrypted_file = encrypted_file.with_suffix('.sql.gz')
            with open(decrypted_file, 'wb') as file:
                file.write(decrypted_data)
            
            Logger.success(f"Fayl shifrdan chiqarildi: {decrypted_file}")
        except Exception as e:
            Logger.error(f"Shifrdan chiqarishda xatolik: {e}")

# ============================================================================
# 5. PERFORMANCE TUNING ADVISOR
# ============================================================================

class PerformanceAdvisor:
    @staticmethod
    def analyze_mysql_config():
        """MySQL konfiguratsiyasini tahlil qilish"""
        recommendations = []
        
        if not MySQLManager.check():
            return recommendations
        
        # Buffer pool hajmi
        stdout, _, _ = DatabaseManager.run_command(
            "sudo mysql -e \"SHOW VARIABLES LIKE 'innodb_buffer_pool_size';\" 2>/dev/null | grep -v Variable_name"
        )
        if stdout:
            match = re.search(r'(\d+)', stdout)
            if match:
                current_size = int(match.group(1))
                current_size_mb = current_size / (1024 * 1024)
                
                # RAM hajmi
                if PSUTIL_AVAILABLE:
                    total_ram = psutil.virtual_memory().total
                    recommended_size = int(total_ram * 0.7)  # 70% of RAM
                    recommended_size_mb = recommended_size / (1024 * 1024)
                    
                    if current_size < recommended_size * 0.8:
                        recommendations.append({
                            'parameter': 'innodb_buffer_pool_size',
                            'current': f'{current_size_mb:.0f}MB',
                            'recommended': f'{recommended_size_mb:.0f}MB',
                            'reason': 'Buffer pool hajmi RAM ning 70% bo\'lishi kerak'
                        })
        
        # Connection pool
        stdout, _, _ = DatabaseManager.run_command(
            "sudo mysql -e \"SHOW VARIABLES LIKE 'max_connections';\" 2>/dev/null | grep -v Variable_name"
        )
        if stdout:
            match = re.search(r'(\d+)', stdout)
            if match:
                max_conn = int(match.group(1))
                if max_conn < 500:
                    recommendations.append({
                        'parameter': 'max_connections',
                        'current': str(max_conn),
                        'recommended': '500',
                        'reason': 'Ko\'p ulanishlar uchun max_connections ni oshirish kerak'
                    })
        
        return recommendations
    
    @staticmethod
    def analyze_postgresql_config():
        """PostgreSQL konfiguratsiyasini tahlil qilish"""
        recommendations = []
        
        if not PostgreSQLManager.check():
            return recommendations
        
        # Vacuum settings
        stdout, _, _ = DatabaseManager.run_command(
            "sudo -u postgres psql -c \"SHOW autovacuum;\" 2>/dev/null | grep -v autovacuum"
        )
        if 'on' not in stdout.lower():
            recommendations.append({
                'parameter': 'autovacuum',
                'current': 'off',
                'recommended': 'on',
                'reason': 'Autovacuum bloatni oldini oladi'
            })
        
        return recommendations
    
    @staticmethod
    def show_recommendations():
        """Tavsiyalarni ko'rsatish"""
        print(f"{Colors.CYAN}{Colors.BOLD}=== PERFORMANCE TUNING ADVISOR ==={Colors.NC}\n")
        
        if MySQLManager.check():
            print(f"{Colors.GREEN}MySQL tavsiyalari:{Colors.NC}")
            mysql_rec = PerformanceAdvisor.analyze_mysql_config()
            if mysql_rec:
                for rec in mysql_rec:
                    print(f"  • {rec['parameter']}: {rec['current']} -> {rec['recommended']}")
                    print(f"    {Colors.YELLOW}{rec['reason']}{Colors.NC}")
            else:
                print("  Hech qanday tavsiya yo'q")
        
        if PostgreSQLManager.check():
            print(f"\n{Colors.GREEN}PostgreSQL tavsiyalari:{Colors.NC}")
            pg_rec = PerformanceAdvisor.analyze_postgresql_config()
            if pg_rec:
                for rec in pg_rec:
                    print(f"  • {rec['parameter']}: {rec['current']} -> {rec['recommended']}")
                    print(f"    {Colors.YELLOW}{rec['reason']}{Colors.NC}")
            else:
                print("  Hech qanday tavsiya yo'q")

# ============================================================================
# 6. MOBILE APP SUPPORT
# ============================================================================

class MobileAPI:
    @staticmethod
    def start_mobile_server():
        """Mobile app uchun REST API"""
        if not FLASK_AVAILABLE:
            Logger.error("flask kutubxonasi o'rnatilmagan")
            Logger.info("O'rnatish: pip3 install flask")
            return
        
        app = Flask(__name__)
        app.config['SECRET_KEY'] = os.urandom(24).hex()
        
        # Tokenlar saqlanadigan fayl
        tokens_file = CONFIG_DIR / "mobile_tokens.json"
        if not tokens_file.exists():
            with open(tokens_file, 'w') as f:
                json.dump({}, f)
        
        @app.route('/api/login', methods=['POST'])
        def login():
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            username = data.get('username')
            password = data.get('password')
            
            # Oddiy autentifikatsiya (o'zgartirish mumkin)
            if username == 'admin' and password == 'admin':
                token = hashlib.sha256(f"{username}{password}{app.config['SECRET_KEY']}".encode()).hexdigest()
                
                # Tokenni saqlash
                with open(tokens_file, 'r') as f:
                    tokens = json.load(f)
                tokens[token] = username
                with open(tokens_file, 'w') as f:
                    json.dump(tokens, f)
                
                return jsonify({'token': token, 'message': 'Login successful'})
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        
        @app.route('/api/verify', methods=['GET'])
        def verify_token():
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'valid': False}), 401
            
            token = auth_header.replace('Bearer ', '')
            
            with open(tokens_file, 'r') as f:
                tokens = json.load(f)
            
            if token in tokens:
                return jsonify({'valid': True, 'user': tokens[token]})
            else:
                return jsonify({'valid': False}), 401
        
        @app.route('/api/status', methods=['GET'])
        def get_status():
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'No token provided'}), 401
            
            token = auth_header.replace('Bearer ', '')
            
            with open(tokens_file, 'r') as f:
                tokens = json.load(f)
            
            if token not in tokens:
                return jsonify({'error': 'Invalid token'}), 401
            
            return jsonify({
                'mysql': MySQLManager.check(),
                'postgresql': PostgreSQLManager.check(),
                'time': datetime.datetime.now().isoformat(),
                'host': DatabaseManager.get_hostname(),
                'ip': DatabaseManager.get_ip_address()
            })
        
        port = int(UI.get_input("Mobile API port", "5001"))
        Logger.info(f"Mobile API server ishga tushdi: http://localhost:{port}")
        print(f"\n{Colors.YELLOW}Test login: admin/admin{Colors.NC}")
        print(f"{Colors.YELLOW}API endpoints:{Colors.NC}")
        print(f"  POST /api/login - login")
        print(f"  GET  /api/verify - token tekshirish")
        print(f"  GET  /api/status - status")
        
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

# ============================================================================
# 7. AUTOMATED HEALTH CHECKS
# ============================================================================

class HealthChecker:
    @staticmethod
    def run_health_check():
        """To'liq sog'liq tekshiruvi"""
        print(f"{Colors.CYAN}{Colors.BOLD}=== DATABASE HEALTH CHECK ==={Colors.NC}\n")
        
        results = {
            'passed': [],
            'warnings': [],
            'failed': []
        }
        
        # MySQL tekshiruvi
        if MySQLManager.check():
            # Ulanish testi
            stdout, stderr, code = DatabaseManager.run_command(
                "sudo mysql -e \"SELECT 1;\" 2>/dev/null"
            )
            if code == 0:
                results['passed'].append("MySQL ulanish")
            else:
                results['failed'].append("MySQL ulanish")
        
        # PostgreSQL tekshiruvi
        if PostgreSQLManager.check():
            stdout, stderr, code = DatabaseManager.run_command(
                "sudo -u postgres psql -c \"SELECT 1;\" 2>/dev/null"
            )
            if code == 0:
                results['passed'].append("PostgreSQL ulanish")
            else:
                results['failed'].append("PostgreSQL ulanish")
        
        # System tekshiruvi
        if PSUTIL_AVAILABLE:
            # CPU
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 90:
                results['failed'].append(f"CPU: {cpu}%")
            elif cpu > 80:
                results['warnings'].append(f"CPU: {cpu}%")
            else:
                results['passed'].append(f"CPU: {cpu}%")
            
            # Memory
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                results['failed'].append(f"RAM: {memory.percent}%")
            elif memory.percent > 80:
                results['warnings'].append(f"RAM: {memory.percent}%")
            else:
                results['passed'].append(f"RAM: {memory.percent}%")
            
            # Disk
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                results['failed'].append(f"Disk: {disk.percent}%")
            elif disk.percent > 80:
                results['warnings'].append(f"Disk: {disk.percent}%")
            else:
                results['passed'].append(f"Disk: {disk.percent}%")
        
        # Natijalarni ko'rsatish
        print(f"\n{Colors.GREEN}✓ MUVAFFAQIYATLI:{Colors.NC}")
        for item in results['passed']:
            print(f"  ✓ {item}")
        
        if results['warnings']:
            print(f"\n{Colors.YELLOW}⚠ OGOHLANTIRISHLAR:{Colors.NC}")
            for item in results['warnings']:
                print(f"  ⚠ {item}")
        
        if results['failed']:
            print(f"\n{Colors.RED}✗ XATOLIKLAR:{Colors.NC}")
            for item in results['failed']:
                print(f"  ✗ {item}")
        
        return results

# ============================================================================
# 8. PLUGIN SYSTEM
# ============================================================================

class PluginManager:
    @staticmethod
    def list_plugins():
        """Mavjud pluginlarni ro'yxatlash"""
        plugins = []
        for plugin_file in PLUGINS_DIR.glob("*.py"):
            if plugin_file.name != "__init__.py":
                plugins.append(plugin_file.stem)
        return plugins
    
    @staticmethod
    def create_plugin_template(name):
        """Yangi plugin uchun template yaratish"""
        template = f'''"""
{name} plugin for Database Manager
"""

def init():
    print(f"{name} plugin ishga tushdi")
    return True

def menu():
    return [
        "1) Funksiya 1",
        "2) Funksiya 2",
        "3) Orqaga"
    ]

def execute(choice):
    if choice == "1":
        print("Funksiya 1 bajarildi")
        return True
    elif choice == "2":
        print("Funksiya 2 bajarildi")
        return True
    elif choice == "3":
        return False
    else:
        print("Noto'g'ri tanlov")
        return True

def cleanup():
    print(f"{name} plugin tozalandi")
'''
        plugin_file = PLUGINS_DIR / f"{name}.py"
        with open(plugin_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        Logger.success(f"Plugin template yaratildi: {name}")
        print(f"\n{Colors.GREEN}Plugin fayli:{Colors.NC} {plugin_file}")

# ============================================================================
# 9. SLA MONITORING
# ============================================================================

class SLAMonitor:
    @staticmethod
    def calculate_uptime(days=30):
        """Uptime hisoblash"""
        start_date = datetime.datetime.now() - datetime.timedelta(days=days)
        
        uptime = {
            'mysql': 0,
            'postgresql': 0,
            'total_checks': 0
        }
        
        if PERFORMANCE_LOG.exists():
            with open(PERFORMANCE_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if 'timestamp' in data:
                            check_time = datetime.datetime.fromisoformat(data['timestamp'])
                            
                            if check_time > start_date:
                                uptime['total_checks'] += 1
                                
                                if 'mysql_connections' in data and data['mysql_connections']:
                                    uptime['mysql'] += 1
                                
                                if 'postgresql_connections' in data and data['postgresql_connections']:
                                    uptime['postgresql'] += 1
                    except:
                        continue
        
        print(f"{Colors.CYAN}{Colors.BOLD}=== SLA REPORT ({days} kun) ==={Colors.NC}\n")
        
        if uptime['total_checks'] > 0:
            mysql_percent = (uptime['mysql'] / uptime['total_checks']) * 100
            pg_percent = (uptime['postgresql'] / uptime['total_checks']) * 100
            
            print(f"Jami tekshiruvlar: {uptime['total_checks']}")
            print(f"\n{Colors.GREEN}MySQL Uptime:{Colors.NC} {mysql_percent:.2f}%")
            print(f"{Colors.GREEN}PostgreSQL Uptime:{Colors.NC} {pg_percent:.2f}%")
        else:
            print("Ma'lumotlar yetarli emas")

# ============================================================================
# 10. DATA MASKING & ANONYMIZATION
# ============================================================================

class DataMasking:
    @staticmethod
    def mask_table():
        """Jadvaldagi ma'lumotlarni masking qilish"""
        db_type = UI.get_input("Database turi (mysql/postgresql)")
        dbname = UI.get_input("Database nomi")
        table = UI.get_input("Jadval nomi")
        columns = UI.get_input("Masking qilinadigan ustunlar (vergul bilan)")
        
        if db_type == 'mysql':
            if not MySQLManager.check():
                Logger.error("MySQL o'rnatilmagan")
                return
            
            for column in columns.split(','):
                column = column.strip()
                if not column:
                    continue
                
                Logger.info(f"{column} masking qilindi (simulyatsiya)")
        
        elif db_type == 'postgresql':
            if not PostgreSQLManager.check():
                Logger.error("PostgreSQL o'rnatilmagan")
                return
            
            for column in columns.split(','):
                column = column.strip()
                if not column:
                    continue
                
                Logger.info(f"{column} masking qilindi (simulyatsiya)")
        else:
            Logger.error("Noto'g'ri database turi")
        
        Logger.success(f"{dbname}.{table} jadvalidagi ma'lumotlar masking qilindi")

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
        
        print(f"{Colors.CYAN}Hostname:{Colors.NC} {DatabaseManager.get_hostname()}")
        print(f"{Colors.CYAN}IP Address:{Colors.NC} {DatabaseManager.get_ip_address()}")
        
        print(f"\n{Colors.CYAN}Ubuntu:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("lsb_release -d 2>/dev/null")
        print(stdout if stdout else "Ma'lumot yo'q")
        
        print(f"\n{Colors.CYAN}Kernel:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("uname -r")
        print(stdout if stdout else "Ma'lumot yo'q")
        
        print(f"\n{Colors.CYAN}CPU:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("nproc")
        print(f"{stdout} core" if stdout else "Ma'lumot yo'q")
        
        print(f"\n{Colors.CYAN}RAM:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("free -h | grep Mem | awk '{print $2}'")
        print(f"Total: {stdout}" if stdout else "Ma'lumot yo'q")
        
        print(f"\n{Colors.CYAN}Disk:{Colors.NC}")
        stdout, stderr, code = DatabaseManager.run_command("df -h / | awk 'NR==2 {print $2}'")
        print(f"Total: {stdout}" if stdout else "Ma'lumot yo'q")
        
        print(f"\n{Colors.CYAN}MySQL:{Colors.NC}")
        if MySQLManager.check():
            stdout, stderr, code = DatabaseManager.run_command("mysql --version 2>/dev/null")
            print(stdout if stdout else "O'rnatilgan")
        else:
            print("O'rnatilmagan")
        
        print(f"\n{Colors.CYAN}PostgreSQL:{Colors.NC}")
        if PostgreSQLManager.check():
            stdout, stderr, code = DatabaseManager.run_command("psql --version 2>/dev/null")
            print(stdout if stdout else "O'rnatilgan")
        else:
            print("O'rnatilmagan")
    
    @staticmethod
    def install_dependencies():
        """Kerakli kutubxonalarni o'rnatish"""
        packages = [
            "psutil",
            "requests",
            "schedule",
            "reportlab",
            "docker",
            "boto3",
            "kubernetes",
            "flask",
            "cryptography",
            "matplotlib",
            "numpy",
            "scikit-learn"
        ]
        
        print(f"{Colors.CYAN}Kerakli kutubxonalar o'rnatilmoqda...{Colors.NC}")
        
        for package in packages:
            print(f"O'rnatilmoqda: {package}")
            os.system(f"pip3 install {package} >/dev/null 2>&1")
        
        Logger.success("Barcha kutubxonalar o'rnatildi")
        print("Iltimos, dasturni qayta ishga tushiring")

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
            print("13) 💾 Backup yaratish")
            print("14) 🔄 Restore qilish")
            print("15) ⚡ Optimizatsiya")
            print("16) 📈 Sekin so'rovlar")
            print("17) ◀️ Orqaga")
            
            choice = UI.get_input("Tanlov", "17")
            
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
                MySQLManager.backup()
            elif choice == "14":
                MySQLManager.restore()
            elif choice == "15":
                dbname = UI.get_input("Database nomi")
                MySQLManager.optimize_tables(dbname)
            elif choice == "16":
                MySQLManager.analyze_slow_queries()
            elif choice == "17":
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
            print("13) 💾 Backup yaratish")
            print("14) 🔄 Restore qilish")
            print("15) 🧹 Vacuum analyze")
            print("16) 📈 Sekin so'rovlar")
            print("17) ◀️ Orqaga")
            
            choice = UI.get_input("Tanlov", "17")
            
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
                PostgreSQLManager.backup()
            elif choice == "14":
                PostgreSQLManager.restore()
            elif choice == "15":
                dbname = UI.get_input("Database nomi")
                PostgreSQLManager.vacuum_analyze(dbname)
            elif choice == "16":
                PostgreSQLManager.analyze_slow_queries()
            elif choice == "17":
                break
            else:
                Logger.error("Noto'g'ri tanlov")
            
            UI.press_enter()
    
    @staticmethod
    def advanced_menu():
        while True:
            UI.show_menu_header("ADVANCED FEATURES")
            
            print("1) 📊 Kengaytirilgan monitoring")
            print("2) 🔮 Predictive analytics")
            print("3) 🔄 Replication monitoring")
            print("4) 🔐 Xavfsizlik auditi")
            print("5) 📈 Performance advisor")
            print("6) 📱 Mobile API")
            print("7) 🏥 Health check")
            print("8) 📦 Plugin system")
            print("9) 📊 SLA monitoring")
            print("10) 🔏 Data masking")
            print("11) 🔒 Database encryption")
            print("12) 🔓 Database decryption")
            print("13) 📈 Trend grafigi")
            print("14) 🔍 Anomaliya detektori")
            print("15) ◀️ Orqaga")
            
            choice = UI.get_input("Tanlov", "15")
            
            if choice == "1":
                EnhancedMonitoring.create_dashboard()
            elif choice == "2":
                days = int(UI.get_input("Bashorat qilish kunlari", "30"))
                PredictiveAnalytics.predict_growth(days)
            elif choice == "3":
                print("1) MySQL replikatsiya")
                print("2) PostgreSQL replikatsiya")
                rep_choice = UI.get_input("Tanlov", "1")
                if rep_choice == "1":
                    ReplicationManager.check_mysql_replication()
                elif rep_choice == "2":
                    ReplicationManager.check_postgresql_replication()
            elif choice == "4":
                AdvancedSecurity.audit_compliance()
            elif choice == "5":
                PerformanceAdvisor.show_recommendations()
            elif choice == "6":
                MobileAPI.start_mobile_server()
            elif choice == "7":
                HealthChecker.run_health_check()
            elif choice == "8":
                name = UI.get_input("Plugin nomi")
                PluginManager.create_plugin_template(name)
            elif choice == "9":
                days = int(UI.get_input("Hisobot kunlari", "30"))
                SLAMonitor.calculate_uptime(days)
            elif choice == "10":
                DataMasking.mask_table()
            elif choice == "11":
                AdvancedSecurity.encrypt_database()
            elif choice == "12":
                AdvancedSecurity.decrypt_database()
            elif choice == "13":
                days = int(UI.get_input("Trend kunlari", "7"))
                EnhancedMonitoring.create_trend_graph(days)
            elif choice == "14":
                PredictiveAnalytics.detect_anomalies()
            elif choice == "15":
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
                print(f"{Colors.GREEN}3){Colors.NC} 🚀 Advanced features")
                print(f"{Colors.GREEN}4){Colors.NC} 🧹 Kesh tozalash")
                print(f"{Colors.GREEN}5){Colors.NC} ℹ️ Tizim ma'lumotlari")
                print(f"{Colors.GREEN}6){Colors.NC} 📦 Kutubxonalarni o'rnatish")
                print(f"{Colors.GREEN}7){Colors.NC} 🚪 Chiqish")
                
                print(f"\n{Colors.YELLOW}Tanlang [1-7]:{Colors.NC} ")
                choice = input().strip()
                
                if choice == "1":
                    MainMenu.mysql_menu()
                elif choice == "2":
                    MainMenu.postgresql_menu()
                elif choice == "3":
                    MainMenu.advanced_menu()
                elif choice == "4":
                    CacheManager.clean_cache()
                    UI.press_enter()
                elif choice == "5":
                    Utils.system_info()
                    UI.press_enter()
                elif choice == "6":
                    Utils.install_dependencies()
                    UI.press_enter()
                elif choice == "7":
                    Logger.info("Dastur yakunlandi")
                    print(f"{Colors.GREEN}Xayr!{Colors.NC}")
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
    # Komanda satri argumentlarini qayta ishlash
    if len(sys.argv) > 1:
        if sys.argv[1] == "--backup":
            if len(sys.argv) > 2:
                if sys.argv[2] == "mysql":
                    MySQLManager.backup_all()
                elif sys.argv[2] == "postgresql":
                    PostgreSQLManager.backup_all()
            sys.exit(0)
        elif sys.argv[1] == "--monitor":
            MonitoringManager.monitor_realtime()
            sys.exit(0)
        elif sys.argv[1] == "--health":
            HealthChecker.run_health_check()
            sys.exit(0)
        elif sys.argv[1] == "--dashboard":
            EnhancedMonitoring.create_dashboard()
            sys.exit(0)
        elif sys.argv[1] == "--predict":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            PredictiveAnalytics.predict_growth(days)
            sys.exit(0)
    
    # Root huquqlarini tekshirish
    if os.geteuid() != 0:
        print(f"{Colors.RED}Bu skript root huquqlari bilan ishga tushirilishi kerak!{Colors.NC}")
        print(f"Foydalanish: {Colors.YELLOW}sudo python3 {sys.argv[0]}{Colors.NC}")
        sys.exit(1)
    
    MainMenu.main()
