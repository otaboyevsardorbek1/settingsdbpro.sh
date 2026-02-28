#!/bin/bash

# ============================================================================
# PROFESSIONAL DATABASE MANAGEMENT SYSTEM
# Version: 3.3 (Enterprise Edition)
# ============================================================================
# Ushbu skript MySQL va PostgreSQL ni to'liq boshqarish imkonini beradi
# Muallif: Database Administrator
# Litsenziya: MIT
# ============================================================================

# Ranglar va formatlash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m'

# Global o'zgaruvchilar
SCRIPT_NAME="Database Professional Manager"
SCRIPT_VERSION="3.3"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/db_configs"
BACKUP_DIR="$SCRIPT_DIR/db_backups"
LOG_DIR="$SCRIPT_DIR/db_logs"
SSL_DIR="$SCRIPT_DIR/db_ssl"
TEMP_DIR="$SCRIPT_DIR/db_temp"
CACHE_DIR="$SCRIPT_DIR/db_cache"
DATA_DIR="$SCRIPT_DIR/db_data"
ARCHIVE_DIR="$SCRIPT_DIR/db_archive"
CONNECTION_FILE="$CONFIG_DIR/connections.db"
HISTORY_FILE="$LOG_DIR/command_history.log"
ERROR_LOG="$LOG_DIR/error.log"
DEBUG_LOG="$LOG_DIR/debug.log"

# Papkalarni yaratish
mkdir -p "$CONFIG_DIR" "$BACKUP_DIR" "$LOG_DIR" "$SSL_DIR" "$TEMP_DIR" "$CACHE_DIR" "$DATA_DIR" "$ARCHIVE_DIR"
touch "$CONNECTION_FILE" "$HISTORY_FILE" "$ERROR_LOG" "$DEBUG_LOG"

# ============================================================================
# LOGGING FUNKSIYALARI
# ============================================================================

log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_DIR/db_manager.log"
    
    case $level in
        "ERROR")   echo -e "${RED}[XATOLIK]${NC} $message" ;;
        "SUCCESS") echo -e "${GREEN}[OK]${NC} $message" ;;
        "WARNING") echo -e "${YELLOW}[OGOHLANTIRISH]${NC} $message" ;;
        "INFO")    echo -e "${CYAN}[MA'LUMOT]${NC} $message" ;;
        "DEBUG")   echo -e "${PURPLE}[DEBUG]${NC} $message" ;;
        *)         echo -e "$message" ;;
    esac
}

log_command() {
    local cmd="$1"
    local user="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "$timestamp | $user | $cmd" >> "$HISTORY_FILE"
}

log_error() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$ERROR_LOG"
    log "ERROR" "$message"
}

log_debug() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" >> "$DEBUG_LOG"
}

# ============================================================================
# UI FUNKSIYALARI
# ============================================================================

show_header() {
    clear
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${WHITE}${BOLD}              PROFESSIONAL DATABASE MANAGEMENT                ${BLUE}║${NC}"
    echo -e "${BLUE}║${WHITE}                 Version: $SCRIPT_VERSION | Enterprise              ${BLUE}║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

show_menu_header() {
    local title="$1"
    echo -e "\n${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${WHITE}${BOLD}   $title${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

press_enter() {
    echo -e "\n${YELLOW}${BOLD}[Enter]${NC} tugmasini bosing davom etish uchun..."
    read -s
}

confirm_action() {
    local message="$1"
    echo -e -n "${YELLOW}$message (y/n): ${NC}"
    read confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        return 1
    fi
    return 0
}

# ============================================================================
# KESH TOZALASH FUNKSIYALARI (TO'LIQ)
# ============================================================================

clean_cache() {
    show_menu_header "KESH TOZALASH"
    
    echo "1) 🧹 Barcha kesh fayllarni tozalash"
    echo "2) 📁 Log fayllarni tozalash"
    echo "3) 📦 Backup fayllarni tozalash"
    echo "4) 🔧 Konfiguratsiya fayllarini tozalash"
    echo "5) 🗑️ Temp fayllarni tozalash"
    echo "6) 📊 Kesh statistikasi"
    echo "7) 🔄 Barchasini tozalash"
    echo "8) ◀️ Orqaga"
    
    read -p "Tanlov: " cache_choice
    
    case $cache_choice in
        1)
            if confirm_action "Barcha kesh fayllar o'chirilsinmi?"; then
                find "$CACHE_DIR" -type f -delete 2>/dev/null
                log "SUCCESS" "Barcha kesh fayllar tozalandi"
            fi
            ;;
        2)
            if confirm_action "Log fayllar tozalansinmi?"; then
                find "$LOG_DIR" -name "*.log" -mtime +1 -delete 2>/dev/null
                > "$LOG_DIR/db_manager.log" 2>/dev/null
                > "$ERROR_LOG" 2>/dev/null
                > "$DEBUG_LOG" 2>/dev/null
                log "SUCCESS" "Log fayllar tozalandi"
            fi
            ;;
        3)
            if confirm_action "Backup fayllar tozalansinmi?"; then
                read -p "Necha kundan eski backup'lar o'chirilsin? (7): " days
                days=${days:-7}
                find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$days -delete 2>/dev/null
                find "$BACKUP_DIR" -name "*.sql" -mtime +$days -delete 2>/dev/null
                find "$BACKUP_DIR" -name "*.tar" -mtime +$days -delete 2>/dev/null
                find "$BACKUP_DIR" -name "*.gz" -mtime +$days -delete 2>/dev/null
                log "SUCCESS" "$days kundan eski backup'lar tozalandi"
            fi
            ;;
        4)
            if confirm_action "Konfiguratsiya fayllari tozalansinmi?"; then
                find "$CONFIG_DIR" -name "*.conf" -mtime +30 -delete 2>/dev/null
                find "$CONFIG_DIR" -name "*.old" -delete 2>/dev/null
                find "$CONFIG_DIR" -name "*.bak" -delete 2>/dev/null
                log "SUCCESS" "Eski konfiguratsiya fayllari tozalandi"
            fi
            ;;
        5)
            if confirm_action "Temp fayllar tozalansinmi?"; then
                rm -rf "$TEMP_DIR"/* 2>/dev/null
                mkdir -p "$TEMP_DIR" 2>/dev/null
                log "SUCCESS" "Temp fayllar tozalandi"
            fi
            ;;
        6)
            echo -e "\n${CYAN}Kesh statistikasi:${NC}"
            echo "📁 Log fayllar: $(find "$LOG_DIR" -type f -name "*.log" 2>/dev/null | wc -l) ta, $(du -sh "$LOG_DIR" 2>/dev/null | cut -f1)"
            echo "📦 Backup fayllar: $(find "$BACKUP_DIR" -name "*.sql.gz" 2>/dev/null | wc -l) ta, $(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"
            echo "🔧 Konfiguratsiya: $(find "$CONFIG_DIR" -type f 2>/dev/null | wc -l) ta, $(du -sh "$CONFIG_DIR" 2>/dev/null | cut -f1)"
            echo "🗑️ Temp fayllar: $(find "$TEMP_DIR" -type f 2>/dev/null | wc -l) ta, $(du -sh "$TEMP_DIR" 2>/dev/null | cut -f1)"
            echo "🧹 Kesh fayllar: $(find "$CACHE_DIR" -type f 2>/dev/null | wc -l) ta, $(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1)"
            echo "📊 Data fayllar: $(find "$DATA_DIR" -type f 2>/dev/null | wc -l) ta, $(du -sh "$DATA_DIR" 2>/dev/null | cut -f1)"
            echo "📚 Archive fayllar: $(find "$ARCHIVE_DIR" -type f 2>/dev/null | wc -l) ta, $(du -sh "$ARCHIVE_DIR" 2>/dev/null | cut -f1)"
            ;;
        7)
            if confirm_action "BARCHA fayllar tozalansinmi? (ehtiyot bo'ling!)"; then
                rm -rf "$CACHE_DIR"/* 2>/dev/null
                rm -rf "$TEMP_DIR"/* 2>/dev/null
                rm -rf "$DATA_DIR"/* 2>/dev/null
                find "$LOG_DIR" -name "*.log" -delete 2>/dev/null
                > "$LOG_DIR/db_manager.log" 2>/dev/null
                > "$ERROR_LOG" 2>/dev/null
                > "$DEBUG_LOG" 2>/dev/null
                find "$BACKUP_DIR" -name "*.sql.gz" -mtime +1 -delete 2>/dev/null
                log "SUCCESS" "Barcha kesh va temp fayllar tozalandi"
            fi
            ;;
        8) return ;;
        *) log_error "Noto'g'ri tanlov: $cache_choice" ;;
    esac
    press_enter
}

# Root huquqida yaratilgan fayllarni tozalash
clean_root_files() {
    show_menu_header "ROOT FAYLLARINI TOZALASH"
    
    echo "1) 🔍 Root fayllarini qidirish"
    echo "2) 🗑️ Root fayllarini o'chirish"
    echo "3) 🔄 Root fayllarini oddiy foydalanuvchiga o'tkazish"
    echo "4) 📊 Root fayllar statistikasi"
    echo "5) ◀️ Orqaga"
    
    read -p "Tanlov: " root_choice
    
    case $root_choice in
        1)
            echo -e "\n${CYAN}Root egasidagi fayllar:${NC}"
            find "$SCRIPT_DIR" -user root -type f -not -path "*/\.*" 2>/dev/null | head -30
            echo -e "\nJami: $(find "$SCRIPT_DIR" -user root -type f 2>/dev/null | wc -l) ta"
            ;;
        2)
            if confirm_action "Root egasidagi barcha fayllar o'chirilsinmi?"; then
                find "$SCRIPT_DIR" -user root -type f -delete 2>/dev/null
                log "SUCCESS" "Root fayllari o'chirildi"
            fi
            ;;
        3)
            read -p "Foydalanuvchi nomi (joriy: $SUDO_USER): " username
            username=${username:-$SUDO_USER}
            if [ -n "$username" ]; then
                find "$SCRIPT_DIR" -user root -type f -exec chown $username:$username {} \; 2>/dev/null
                log "SUCCESS" "Root fayllari $username ga o'tkazildi"
            fi
            ;;
        4)
            echo -e "\n${CYAN}Root fayllar statistikasi:${NC}"
            echo "Jami root fayllar: $(find "$SCRIPT_DIR" -user root -type f 2>/dev/null | wc -l) ta"
            echo "Umumiy hajmi: $(find "$SCRIPT_DIR" -user root -type f -exec du -b {} \; 2>/dev/null | awk '{sum+=$1} END {print sum/1024/1024 " MB"}')"
            echo "Eng katta fayllar:"
            find "$SCRIPT_DIR" -user root -type f -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -5
            ;;
        5) return ;;
        *) log_error "Noto'g'ri tanlov: $root_choice" ;;
    esac
    press_enter
}

# Dastur papkalarini tozalash
clean_program_folders() {
    show_menu_header "DASTUR PAPKALARINI TOZALASH"
    
    echo "1) 🗑️ Bo'sh papkalarni o'chirish"
    echo "2) 📦 Eski arxivlarni tozalash"
    echo "3) 🔄 Duplikat fayllarni topish"
    echo "4) 🧹 Barcha qo'shimcha papkalarni tozalash"
    echo "5) 📊 Papkalar statistikasi"
    echo "6) ◀️ Orqaga"
    
    read -p "Tanlov: " folder_choice
    
    case $folder_choice in
        1)
            if confirm_action "Barcha bo'sh papkalar o'chirilsinmi?"; then
                find "$SCRIPT_DIR" -type d -empty -delete 2>/dev/null
                log "SUCCESS" "Bo'sh papkalar o'chirildi"
            fi
            ;;
        2)
            if confirm_action "Eski arxivlar tozalansinmi?"; then
                find "$ARCHIVE_DIR" -name "*.tar.gz" -mtime +90 -delete 2>/dev/null
                find "$ARCHIVE_DIR" -name "*.zip" -mtime +90 -delete 2>/dev/null
                log "SUCCESS" "90 kundan eski arxivlar tozalandi"
            fi
            ;;
        3)
            echo -e "\n${CYAN}Duplikat fayllar qidirilmoqda...${NC}"
            find "$SCRIPT_DIR" -type f -exec md5sum {} \; 2>/dev/null | sort | uniq -w32 -dD | head -20
            ;;
        4)
            if confirm_action "Barcha qo'shimcha papkalar tozalansinmi?"; then
                folders=("$CONFIG_DIR" "$BACKUP_DIR" "$LOG_DIR" "$SSL_DIR" "$TEMP_DIR" "$CACHE_DIR" "$DATA_DIR" "$ARCHIVE_DIR")
                for folder in "${folders[@]}"; do
                    if [ -d "$folder" ]; then
                        rm -rf "$folder"/* 2>/dev/null
                        log "INFO" "$folder tozalandi"
                    fi
                done
                log "SUCCESS" "Barcha qo'shimcha papkalar tozalandi"
            fi
            ;;
        5)
            echo -e "\n${CYAN}Papkalar statistikasi:${NC}"
            echo "📁 Jami papkalar: $(find "$SCRIPT_DIR" -type d 2>/dev/null | wc -l) ta"
            echo "📊 Papkalar hajmi: $(du -sh "$SCRIPT_DIR" 2>/dev/null | cut -f1)"
            echo ""
            echo "Asosiy papkalar:"
            du -sh "$CONFIG_DIR" 2>/dev/null || echo "$CONFIG_DIR: 0B"
            du -sh "$BACKUP_DIR" 2>/dev/null || echo "$BACKUP_DIR: 0B"
            du -sh "$LOG_DIR" 2>/dev/null || echo "$LOG_DIR: 0B"
            du -sh "$SSL_DIR" 2>/dev/null || echo "$SSL_DIR: 0B"
            du -sh "$TEMP_DIR" 2>/dev/null || echo "$TEMP_DIR: 0B"
            du -sh "$CACHE_DIR" 2>/dev/null || echo "$CACHE_DIR: 0B"
            du -sh "$DATA_DIR" 2>/dev/null || echo "$DATA_DIR: 0B"
            du -sh "$ARCHIVE_DIR" 2>/dev/null || echo "$ARCHIVE_DIR: 0B"
            ;;
        6) return ;;
        *) log_error "Noto'g'ri tanlov: $folder_choice" ;;
    esac
    press_enter
}

# ============================================================================
# MA'LUMOTLAR BAZASI ULANISH FUNKSIYALARI
# ============================================================================

# MySQL ulanish ma'lumotlarini olish
get_mysql_connection_info() {
    local instance="$1"
    local config_file="$CONFIG_DIR/mysql_${instance}.conf"
    
    if [[ -f "$config_file" ]]; then
        source "$config_file"
        echo "HOST=$MYSQL_HOST"
        echo "PORT=$MYSQL_PORT"
        echo "USER=$MYSQL_USER"
        echo "PASSWORD=$MYSQL_PASSWORD"
        echo "DATABASE=$MYSQL_DATABASE"
    else
        echo "HOST=localhost"
        echo "PORT=3306"
        echo "USER=root"
        echo "PASSWORD="
        echo "DATABASE="
    fi
}

# PostgreSQL ulanish ma'lumotlarini olish
get_postgresql_connection_info() {
    local instance="$1"
    local config_file="$CONFIG_DIR/postgres_${instance}.conf"
    
    if [[ -f "$config_file" ]]; then
        source "$config_file"
        echo "HOST=$PG_HOST"
        echo "PORT=$PG_PORT"
        echo "USER=$PG_USER"
        echo "PASSWORD=$PG_PASSWORD"
        echo "DATABASE=$PG_DATABASE"
    else
        echo "HOST=localhost"
        echo "PORT=5432"
        echo "USER=postgres"
        echo "PASSWORD="
        echo "DATABASE="
    fi
}

# MySQL ulanish URL generatsiya qilish
generate_mysql_url() {
    local host="$1"
    local port="$2"
    local user="$3"
    local password="$4"
    local database="$5"
    
    echo -e "\n${CYAN}${BOLD}MySQL Ulanish URL'lari:${NC}\n"
    echo -e "${WHITE}Standard URL:${NC}"
    echo "mysql://$user:$password@$host:$port/$database"
    echo -e "\n${WHITE}JDBC URL:${NC}"
    echo "jdbc:mysql://$host:$port/$database?user=$user&password=$password"
    echo -e "\n${WHITE}Python SQLAlchemy URL:${NC}"
    echo "mysql+pymysql://$user:$password@$host:$port/$database"
    echo -e "\n${WHITE}PHP PDO URL:${NC}"
    echo "\$pdo = new PDO('mysql:host=$host;port=$port;dbname=$database', '$user', '$password');"
    echo -e "\n${WHITE}Node.js mysql2 URL:${NC}"
    echo "const mysql = require('mysql2');"
    echo "const connection = mysql.createConnection({"
    echo "  host: '$host',"
    echo "  port: $port,"
    echo "  user: '$user',"
    echo "  password: '$password',"
    echo "  database: '$database'"
    echo "});"
    echo -e "\n${WHITE}Command line:${NC}"
    echo "mysql -h $host -P $port -u $user -p$password $database"
}

# PostgreSQL ulanish URL generatsiya qilish
generate_postgresql_url() {
    local host="$1"
    local port="$2"
    local user="$3"
    local password="$4"
    local database="$5"
    
    echo -e "\n${CYAN}${BOLD}PostgreSQL Ulanish URL'lari:${NC}\n"
    echo -e "${WHITE}Standard URL:${NC}"
    echo "postgresql://$user:$password@$host:$port/$database"
    echo -e "\n${WHITE}JDBC URL:${NC}"
    echo "jdbc:postgresql://$host:$port/$database?user=$user&password=$password"
    echo -e "\n${WHITE}Python SQLAlchemy URL:${NC}"
    echo "postgresql+psycopg2://$user:$password@$host:$port/$database"
    echo "postgresql+asyncpg://$user:$password@$host:$port/$database"
    echo -e "\n${WHITE}PHP PDO URL:${NC}"
    echo "\$pdo = new PDO('pgsql:host=$host;port=$port;dbname=$database', '$user', '$password');"
    echo -e "\n${WHITE}Node.js pg URL:${NC}"
    echo "const { Client } = require('pg');"
    echo "const client = new Client({"
    echo "  host: '$host',"
    echo "  port: $port,"
    echo "  user: '$user',"
    echo "  password: '$password',"
    echo "  database: '$database'"
    echo "});"
    echo -e "\n${WHITE}Command line:${NC}"
    echo "psql -h $host -p $port -U $user -d $database"
    echo -e "\n${WHITE}Libpq Connection String:${NC}"
    echo "host=$host port=$port dbname=$database user=$user password=$password"
}

# ============================================================================
# MYSQL FUNKSIYALARI (TO'LIQ)
# ============================================================================

check_mysql() {
    if ! command -v mysql &> /dev/null; then
        return 1
    fi
    return 0
}

mysql_status() {
    show_menu_header "MySQL HOLATI"
    
    if ! check_mysql; then
        log "ERROR" "MySQL o'rnatilmagan"
        return 1
    fi
    
    echo -e "${CYAN}${BOLD}Xizmat holati:${NC}"
    sudo systemctl status mysql --no-pager -l 2>/dev/null | grep -E "Active|Loaded" || echo "MySQL xizmati topilmadi"
    
    echo -e "\n${CYAN}${BOLD}Versiya:${NC}"
    mysql --version 2>/dev/null
    
    echo -e "\n${CYAN}${BOLD}Port:${NC}"
    sudo ss -tlnp 2>/dev/null | grep mysql || echo "3306"
    
    echo -e "\n${CYAN}${BOLD}Faol ulanishlar:${NC}"
    sudo mysql -e "SHOW STATUS LIKE 'Threads_connected';" 2>/dev/null | grep Threads_connected || echo "Ma'lumot olish imkonsiz"
    
    echo -e "\n${CYAN}${BOLD}Ma'lumotlar bazalari:${NC}"
    sudo mysql -e "SHOW DATABASES;" 2>/dev/null | wc -l | xargs echo "Jami:" || echo "Ma'lumot olish imkonsiz"
    
    echo -e "\n${CYAN}${BOLD}Processlar:${NC}"
    sudo mysql -e "SHOW PROCESSLIST;" 2>/dev/null | head -10 || echo "Ma'lumot olish imkonsiz"
}

mysql_list_users() {
    show_menu_header "MYSQL FOYDALANUVCHILARI"
    
    if ! check_mysql; then
        log "ERROR" "MySQL o'rnatilmagan"
        return 1
    fi
    
    echo -e "${GREEN}${BOLD}Barcha foydalanuvchilar:${NC}\n"
    sudo mysql -e "SELECT User, Host, plugin, authentication_string as Password_Hash, account_locked, password_expired FROM mysql.user ORDER BY User;" 2>/dev/null | column -t -s $'\t' || echo "Ma'lumot olish imkonsiz"
}

mysql_create_user() {
    show_menu_header "YANGI MYSQL FOYDALANUVCHI"
    
    local username host password auth_plugin
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Xost (localhost/192.168.%/%): " host
    read -s -p "Parol: " password
    echo ""
    
    echo -e "\nAuth plugin tanlang:"
    echo "1) mysql_native_password (default)"
    echo "2) caching_sha2_password"
    echo "3) sha256_password"
    read -p "Tanlov (1-3): " auth_choice
    
    case $auth_choice in
        1) auth_plugin="mysql_native_password" ;;
        2) auth_plugin="caching_sha2_password" ;;
        3) auth_plugin="sha256_password" ;;
        *) auth_plugin="mysql_native_password" ;;
    esac
    
    sudo mysql -e "CREATE USER '$username'@'$host' IDENTIFIED WITH $auth_plugin BY '$password';" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Foydalanuvchi yaratildi: $username@$host"
        
        echo -e "\nQo'shimcha sozlamalar:"
        echo "1) Parol muddatini belgilash"
        echo "2) Hisobni bloklash"
        echo "3) Resurs limitlari"
        echo "4) O'tkazib yuborish"
        read -p "Tanlov: " extra_choice
        
        case $extra_choice in
            1)
                read -p "Parol amal qilish muddati (kun): " days
                sudo mysql -e "ALTER USER '$username'@'$host' PASSWORD EXPIRE INTERVAL $days DAY;" 2>/dev/null
                log "INFO" "Parol muddati: $days kun"
                ;;
            2)
                sudo mysql -e "ALTER USER '$username'@'$host' ACCOUNT LOCK;" 2>/dev/null
                log "INFO" "Hisob bloklandi"
                ;;
            3)
                read -p "So'rovlar limiti/soat: " queries
                read -p "Ulanishlar limiti/soat: " connections
                read -p "Yangilanishlar limiti/soat: " updates
                sudo mysql -e "ALTER USER '$username'@'$host' WITH MAX_QUERIES_PER_HOUR $queries MAX_CONNECTIONS_PER_HOUR $connections MAX_UPDATES_PER_HOUR $updates;" 2>/dev/null
                log "INFO" "Resurs limitlari o'rnatildi"
                ;;
        esac
    else
        log "ERROR" "Foydalanuvchi yaratishda xatolik"
    fi
}

mysql_delete_user() {
    show_menu_header "MYSQL FOYDALANUVCHI O'CHIRISH"
    
    mysql_list_users
    
    local username host
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Xost: " host
    
    if confirm_action "Foydalanuvchi $username@$host ni o'chirishni tasdiqlaysizmi?"; then
        sudo mysql -e "DROP USER IF EXISTS '$username'@'$host';" 2>/dev/null
        sudo mysql -e "FLUSH PRIVILEGES;" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            log "SUCCESS" "Foydalanuvchi o'chirildi: $username@$host"
        else
            log "ERROR" "Foydalanuvchi o'chirishda xatolik"
        fi
    fi
}

mysql_change_password() {
    show_menu_header "MYSQL PAROL O'ZGARTIRISH"
    
    local username host new_password new_password2
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Xost: " host
    read -s -p "Yangi parol: " new_password
    echo ""
    read -s -p "Yangi parol (takror): " new_password2
    echo ""
    
    if [[ "$new_password" != "$new_password2" ]]; then
        log "ERROR" "Parollar mos kelmadi"
        return
    fi
    
    sudo mysql -e "ALTER USER '$username'@'$host' IDENTIFIED BY '$new_password';" 2>/dev/null
    sudo mysql -e "FLUSH PRIVILEGES;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Parol o'zgartirildi"
    else
        log "ERROR" "Parol o'zgartirishda xatolik"
    fi
}

mysql_grant_privileges() {
    show_menu_header "MYSQL RUXSATLAR BERISH"
    
    local username host database privileges
    
    mysql_list_users
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Xost: " host
    
    echo -e "\n${CYAN}Ma'lumotlar bazalari:${NC}"
    sudo mysql -e "SHOW DATABASES;" 2>/dev/null | grep -v "Database\|information_schema\|performance_schema\|mysql\|sys"
    
    read -p "Ma'lumotlar bazasi nomi (* - barchasi): " database
    [[ "$database" == "*" ]] && database="*"
    
    echo -e "\n${CYAN}Ruxsat turlari:${NC}"
    echo "1) Barcha ruxsatlar (ALL PRIVILEGES)"
    echo "2) O'qish (SELECT)"
    echo "3) O'qish/Yozish (SELECT, INSERT, UPDATE, DELETE)"
    echo "4) Ma'lumotlar strukturasi (CREATE, ALTER, DROP)"
    echo "5) Maxsus ruxsatlar"
    echo "6) Grant option bilan"
    
    read -p "Tanlov (1-6): " priv_choice
    
    case $priv_choice in
        1) privileges="ALL PRIVILEGES" ;;
        2) privileges="SELECT" ;;
        3) privileges="SELECT, INSERT, UPDATE, DELETE" ;;
        4) privileges="CREATE, ALTER, DROP, INDEX" ;;
        5) read -p "Ruxsatlarni vergul bilan yozing: " privileges ;;
        6) read -p "Ruxsatlar: " base_priv && privileges="$base_priv WITH GRANT OPTION" ;;
        *) log_error "Noto'g'ri tanlov" && return ;;
    esac
    
    sudo mysql -e "GRANT $privileges ON $database.* TO '$username'@'$host'; FLUSH PRIVILEGES;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Ruxsatlar berildi: $privileges"
        echo -e "\n${CYAN}Yangi grantlar:${NC}"
        sudo mysql -e "SHOW GRANTS FOR '$username'@'$host';" 2>/dev/null
    else
        log "ERROR" "Ruxsat berishda xatolik"
    fi
}

mysql_show_grants() {
    show_menu_header "MYSQL GRANTLAR"
    
    local username host
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Xost: " host
    
    sudo mysql -e "SHOW GRANTS FOR '$username'@'$host';" 2>/dev/null
}

mysql_revoke_privileges() {
    show_menu_header "MYSQL RUXSATLARNI OLIB TASHLASH"
    
    local username host database privileges
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Xost: " host
    read -p "Ma'lumotlar bazasi: " database
    
    echo -e "\n${CYAN}Mavjud grantlar:${NC}"
    sudo mysql -e "SHOW GRANTS FOR '$username'@'$host';" 2>/dev/null
    
    read -p "Olib tashlanadigan ruxsatlar: " privileges
    
    sudo mysql -e "REVOKE $privileges ON $database.* FROM '$username'@'$host'; FLUSH PRIVILEGES;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Ruxsatlar olib tashlandi"
    else
        log "ERROR" "Ruxsatlarni olib tashlashda xatolik"
    fi
}

mysql_list_databases() {
    show_menu_header "MYSQL MA'LUMOTLAR BAZALARI"
    
    echo -e "${GREEN}${BOLD}Barcha ma'lumotlar bazalari:${NC}\n"
    sudo mysql -e "SELECT SCHEMA_NAME as 'Database', DEFAULT_CHARACTER_SET_NAME as 'Charset', DEFAULT_COLLATION_NAME as 'Collation' FROM information_schema.SCHEMATA ORDER BY SCHEMA_NAME;" 2>/dev/null | column -t -s $'\t'
    
    echo -e "\n${GREEN}${BOLD}Hajmlari bilan:${NC}\n"
    sudo mysql -e "SELECT table_schema as 'Database', ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as 'Size (MB)', COUNT(*) as 'Tables' FROM information_schema.tables GROUP BY table_schema ORDER BY 2 DESC;" 2>/dev/null | column -t -s $'\t'
}

mysql_create_database() {
    show_menu_header "YANGI MYSQL MA'LUMOTLAR BAZASI"
    
    local dbname charset collation
    
    read -p "Ma'lumotlar bazasi nomi: " dbname
    
    echo -e "\n${CYAN}Mavjud charsetlar:${NC}"
    sudo mysql -e "SHOW CHARACTER SET;" 2>/dev/null | head -10
    
    read -p "Charset (utf8mb4): " charset
    charset=${charset:-utf8mb4}
    
    read -p "Collation (utf8mb4_unicode_ci): " collation
    collation=${collation:-utf8mb4_unicode_ci}
    
    sudo mysql -e "CREATE DATABASE IF NOT EXISTS $dbname CHARACTER SET $charset COLLATE $collation;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Ma'lumotlar bazasi yaratildi: $dbname"
        
        if confirm_action "Foydalanuvchiga ruxsat berilsinmi?"; then
            read -p "Foydalanuvchi nomi: " username
            read -p "Xost: " host
            sudo mysql -e "GRANT ALL PRIVILEGES ON $dbname.* TO '$username'@'$host'; FLUSH PRIVILEGES;" 2>/dev/null
            log "SUCCESS" "Ruxsat berildi: $username@$host"
        fi
    else
        log "ERROR" "Ma'lumotlar bazasi yaratishda xatolik"
    fi
}

mysql_drop_database() {
    show_menu_header "MYSQL MA'LUMOTLAR BAZASINI O'CHIRISH"
    
    mysql_list_databases
    
    local dbname
    read -p "O'chiriladigan ma'lumotlar bazasi: " dbname
    
    if confirm_action "DIQQAT! $dbname butunlay o'chiriladi. Tasdiqlaysizmi?"; then
        sudo mysql -e "DROP DATABASE $dbname;" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            log "SUCCESS" "Ma'lumotlar bazasi o'chirildi: $dbname"
        else
            log "ERROR" "O'chirishda xatolik"
        fi
    fi
}

mysql_config_view() {
    show_menu_header "MYSQL SOZLAMALARI"
    
    local config_file="/etc/mysql/mysql.conf.d/mysqld.cnf"
    
    if [[ -f "$config_file" ]]; then
        echo -e "${CYAN}${BOLD}Asosiy sozlamalar:${NC}\n"
        grep -v "^#" "$config_file" | grep -v "^$" | head -50
        
        echo -e "\n${CYAN}${BOLD}Muhim o'zgaruvchilar:${NC}\n"
        sudo mysql -e "SHOW VARIABLES WHERE Variable_name IN ('max_connections', 'innodb_buffer_pool_size', 'innodb_log_file_size', 'query_cache_size', 'tmp_table_size', 'max_allowed_packet', 'wait_timeout', 'interactive_timeout', 'sort_buffer_size', 'read_buffer_size', 'read_rnd_buffer_size', 'join_buffer_size', 'thread_cache_size', 'table_open_cache');" 2>/dev/null | column -t -s $'\t'
    else
        log "ERROR" "Sozlamalar fayli topilmadi"
    fi
}

mysql_config_edit() {
    show_menu_header "MYSQL SOZLAMALARINI O'ZGARTIRISH"
    
    echo "1) Port o'zgartirish"
    echo "2) Maksimal ulanishlar"
    echo "3) Buffer pool hajmi"
    echo "4) Log fayl hajmi"
    echo "5) Timeout sozlamalari"
    echo "6) Xotira sozlamalari"
    echo "7) Maxsus sozlama"
    echo "8) Faylni tahrirlash"
    
    read -p "Tanlov: " config_choice
    
    case $config_choice in
        1)
            read -p "Yangi port (3306): " new_port
            sudo mysql -e "SET GLOBAL port = $new_port;" 2>/dev/null
            log "SUCCESS" "Port o'zgartirildi: $new_port"
            ;;
        2)
            read -p "Maksimal ulanishlar (151): " max_conn
            sudo mysql -e "SET GLOBAL max_connections = $max_conn;" 2>/dev/null
            log "SUCCESS" "max_connections = $max_conn"
            ;;
        3)
            read -p "Buffer pool hajmi (128M/1G): " buffer_size
            sudo mysql -e "SET GLOBAL innodb_buffer_pool_size = '$buffer_size';" 2>/dev/null
            log "SUCCESS" "innodb_buffer_pool_size = $buffer_size"
            ;;
        4)
            read -p "Log fayl hajmi (256M): " log_size
            sudo mysql -e "SET GLOBAL innodb_log_file_size = '$log_size';" 2>/dev/null
            log "SUCCESS" "innodb_log_file_size = $log_size"
            ;;
        5)
            read -p "wait_timeout (28800): " wait_timeout
            read -p "interactive_timeout (28800): " interactive_timeout
            sudo mysql -e "SET GLOBAL wait_timeout = $wait_timeout; SET GLOBAL interactive_timeout = $interactive_timeout;" 2>/dev/null
            log "SUCCESS" "Timeout sozlamalari yangilandi"
            ;;
        6)
            read -p "sort_buffer_size (2M): " sort_buffer
            read -p "read_buffer_size (128K): " read_buffer
            read -p "join_buffer_size (128K): " join_buffer
            sudo mysql -e "SET GLOBAL sort_buffer_size = '$sort_buffer'; SET GLOBAL read_buffer_size = '$read_buffer'; SET GLOBAL join_buffer_size = '$join_buffer';" 2>/dev/null
            log "SUCCESS" "Xotira sozlamalari yangilandi"
            ;;
        7)
            read -p "O'zgaruvchi nomi: " var_name
            read -p "Yangi qiymat: " var_value
            sudo mysql -e "SET GLOBAL $var_name = '$var_value';" 2>/dev/null
            log "SUCCESS" "$var_name = $var_value"
            ;;
        8)
            sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
            log "INFO" "Sozlamalar fayli tahrirlandi"
            ;;
        *) log_error "Noto'g'ri tanlov" && return ;;
    esac
    
    if confirm_action "MySQL ni qayta ishga tushirish kerak. Hozir bajaramizmi?"; then
        sudo systemctl restart mysql 2>/dev/null
        log "SUCCESS" "MySQL qayta ishga tushirildi"
    fi
}

mysql_generate_url() {
    show_menu_header "MYSQL ULANISH URL GENERATSIYASI"
    
    local host port user password database
    
    if [[ -f "$CONFIG_DIR/mysql_current.conf" ]]; then
        source "$CONFIG_DIR/mysql_current.conf"
    else
        read -p "Host (localhost): " host
        host=${host:-localhost}
        read -p "Port (3306): " port
        port=${port:-3306}
        read -p "User: " user
        read -s -p "Password: " password
        echo ""
        read -p "Database: " database
    fi
    
    generate_mysql_url "$host" "$port" "$user" "$password" "$database"
    
    if confirm_action "Bu sozlamalarni saqlash kerakmi?"; then
        cat > "$CONFIG_DIR/mysql_current.conf" << EOF
MYSQL_HOST="$host"
MYSQL_PORT="$port"
MYSQL_USER="$user"
MYSQL_PASSWORD="$password"
MYSQL_DATABASE="$database"
EOF
        log "SUCCESS" "Sozlamalar saqlandi"
    fi
}

mysql_performance_stats() {
    show_menu_header "MYSQL PERFORMANS STATISTIKASI"
    
    echo -e "${CYAN}${BOLD}So'rovlar statistikasi:${NC}\n"
    sudo mysql -e "SHOW GLOBAL STATUS LIKE 'Questions';" 2>/dev/null
    sudo mysql -e "SHOW GLOBAL STATUS LIKE 'Slow_queries';" 2>/dev/null
    sudo mysql -e "SHOW GLOBAL STATUS LIKE 'Com_select';" 2>/dev/null
    sudo mysql -e "SHOW GLOBAL STATUS LIKE 'Com_insert';" 2>/dev/null
    sudo mysql -e "SHOW GLOBAL STATUS LIKE 'Com_update';" 2>/dev/null
    sudo mysql -e "SHOW GLOBAL STATUS LIKE 'Com_delete';" 2>/dev/null
    
    echo -e "\n${CYAN}${BOLD}Buffer pool statistikasi:${NC}\n"
    sudo mysql -e "SHOW ENGINE INNODB STATUS\G" 2>/dev/null | grep -A 10 "BUFFER POOL AND MEMORY"
}

# ============================================================================
# POSTGRESQL FUNKSIYALARI (TO'LIQ)
# ============================================================================

check_postgresql() {
    if ! command -v psql &> /dev/null; then
        return 1
    fi
    return 0
}

postgresql_status() {
    show_menu_header "POSTGRESQL HOLATI"
    
    if ! check_postgresql; then
        log "ERROR" "PostgreSQL o'rnatilmagan"
        return 1
    fi
    
    echo -e "${CYAN}${BOLD}Xizmat holati:${NC}"
    sudo systemctl status postgresql --no-pager -l 2>/dev/null | grep -E "Active|Loaded"
    
    echo -e "\n${CYAN}${BOLD}Versiya:${NC}"
    sudo -u postgres psql -c "SELECT version();" 2>/dev/null | grep PostgreSQL
    
    echo -e "\n${CYAN}${BOLD}Port:${NC}"
    sudo ss -tlnp 2>/dev/null | grep postgres || echo "5432"
    
    echo -e "\n${CYAN}${BOLD}Faol ulanishlar:${NC}"
    sudo -u postgres psql -c "SELECT count(*) as active_connections FROM pg_stat_activity;" 2>/dev/null
    
    echo -e "\n${CYAN}${BOLD}Ma'lumotlar bazalari:${NC}"
    sudo -u postgres psql -c "SELECT count(*) FROM pg_database WHERE datistemplate = false;" 2>/dev/null
    
    echo -e "\n${CYAN}${BOLD}Muhim sozlamalar:${NC}"
    sudo -u postgres psql -c "SELECT name, setting, unit FROM pg_settings WHERE name IN ('max_connections', 'shared_buffers', 'work_mem', 'maintenance_work_mem', 'effective_cache_size', 'wal_buffers');" 2>/dev/null
}

postgresql_list_users() {
    show_menu_header "POSTGRESQL FOYDALANUVCHILARI"
    
    echo -e "${GREEN}${BOLD}Barcha foydalanuvchilar:${NC}\n"
    sudo -u postgres psql -c "\du" 2>/dev/null
}

postgresql_create_user() {
    show_menu_header "YANGI POSTGRESQL FOYDALANUVCHI"
    
    local username password options=""
    
    read -p "Foydalanuvchi nomi: " username
    read -s -p "Parol: " password
    echo ""
    
    echo -e "\n${CYAN}Ruxsatlar:${NC}"
    echo "1) Oddiy foydalanuvchi"
    echo "2) Superuser"
    echo "3) Ma'lumotlar bazasi yaratish huquqi bilan"
    echo "4) Replikatsiya huquqi bilan"
    
    read -p "Tanlov (1-4): " priv_choice
    
    case $priv_choice in
        1) options="" ;;
        2) options="SUPERUSER" ;;
        3) options="CREATEDB" ;;
        4) options="REPLICATION" ;;
        *) options="" ;;
    esac
    
    if confirm_action "Ulanish limiti belgilansinmi?"; then
        read -p "Maksimal ulanishlar soni: " conn_limit
        options="$options CONNECTION LIMIT $conn_limit"
    fi
    
    if confirm_action "Parol amal qilish muddati belgilansinmi?"; then
        read -p "Muddat (YYYY-MM-DD): " valid_until
        options="$options VALID UNTIL '$valid_until'"
    fi
    
    sudo -u postgres psql -c "CREATE USER $username WITH PASSWORD '$password' $options;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Foydalanuvchi yaratildi: $username"
    else
        log "ERROR" "Foydalanuvchi yaratishda xatolik"
    fi
}

postgresql_delete_user() {
    show_menu_header "POSTGRESQL FOYDALANUVCHI O'CHIRISH"
    
    postgresql_list_users
    
    local username
    read -p "Foydalanuvchi nomi: " username
    
    if confirm_action "Foydalanuvchi $username ni o'chirishni tasdiqlaysizmi?"; then
        sudo -u postgres psql -c "REASSIGN OWNED BY $username TO postgres;" 2>/dev/null
        sudo -u postgres psql -c "DROP OWNED BY $username;" 2>/dev/null
        sudo -u postgres psql -c "DROP USER IF EXISTS $username;" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            log "SUCCESS" "Foydalanuvchi o'chirildi: $username"
        else
            log "ERROR" "Foydalanuvchi o'chirishda xatolik"
        fi
    fi
}

postgresql_change_password() {
    show_menu_header "POSTGRESQL PAROL O'ZGARTIRISH"
    
    local username new_password new_password2
    
    read -p "Foydalanuvchi nomi: " username
    read -s -p "Yangi parol: " new_password
    echo ""
    read -s -p "Yangi parol (takror): " new_password2
    echo ""
    
    if [[ "$new_password" != "$new_password2" ]]; then
        log "ERROR" "Parollar mos kelmadi"
        return
    fi
    
    sudo -u postgres psql -c "ALTER USER $username WITH PASSWORD '$new_password';" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Parol o'zgartirildi"
    else
        log "ERROR" "Parol o'zgartirishda xatolik"
    fi
}

postgresql_grant_privileges() {
    show_menu_header "POSTGRESQL RUXSATLAR BERISH"
    
    local username database privileges
    
    postgresql_list_users
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Ma'lumotlar bazasi nomi: " database
    
    echo -e "\n${CYAN}Ruxsat turlari:${NC}"
    echo "1) Barcha ruxsatlar (ALL PRIVILEGES)"
    echo "2) O'qish (SELECT)"
    echo "3) O'qish/Yozish (SELECT, INSERT, UPDATE, DELETE)"
    echo "4) Ma'lumotlar strukturasi (CREATE, ALTER, DROP)"
    echo "5) Maxsus ruxsatlar"
    echo "6) Grant option bilan"
    
    read -p "Tanlov (1-6): " priv_choice
    
    case $priv_choice in
        1) privileges="ALL PRIVILEGES" ;;
        2) privileges="SELECT" ;;
        3) privileges="SELECT, INSERT, UPDATE, DELETE" ;;
        4) privileges="CREATE, ALTER, DROP" ;;
        5) read -p "Ruxsatlarni vergul bilan yozing: " privileges ;;
        6) read -p "Ruxsatlar: " base_priv && privileges="$base_priv WITH GRANT OPTION" ;;
        *) log_error "Noto'g'ri tanlov" && return ;;
    esac
    
    sudo -u postgres psql -c "GRANT CONNECT ON DATABASE $database TO $username;" 2>/dev/null
    sudo -u postgres psql -c "GRANT $privileges ON ALL TABLES IN SCHEMA public TO $username;" 2>/dev/null
    sudo -u postgres psql -c "GRANT $privileges ON ALL SEQUENCES IN SCHEMA public TO $username;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Ruxsatlar berildi: $username"
        echo -e "\n${CYAN}Yangi grantlar:${NC}"
        sudo -u postgres psql -c "\dp $database.*" 2>/dev/null | head -20
    else
        log "ERROR" "Ruxsat berishda xatolik"
    fi
}

postgresql_show_grants() {
    show_menu_header "POSTGRESQL GRANTLAR"
    
    local username
    
    read -p "Foydalanuvchi nomi: " username
    
    sudo -u postgres psql -c "\du $username" 2>/dev/null
    sudo -u postgres psql -c "\dp" 2>/dev/null | grep "$username" || echo "Grantlar topilmadi"
}

postgresql_revoke_privileges() {
    show_menu_header "POSTGRESQL RUXSATLARNI OLIB TASHLASH"
    
    local username database privileges
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Ma'lumotlar bazasi: " database
    
    echo -e "\n${CYAN}Mavjud grantlar:${NC}"
    sudo -u postgres psql -c "\dp $database.*" 2>/dev/null | grep "$username"
    
    read -p "Olib tashlanadigan ruxsatlar: " privileges
    
    sudo -u postgres psql -c "REVOKE $privileges ON ALL TABLES IN SCHEMA public FROM $username;" 2>/dev/null
    sudo -u postgres psql -c "REVOKE $privileges ON ALL SEQUENCES IN SCHEMA public FROM $username;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Ruxsatlar olib tashlandi"
    else
        log "ERROR" "Ruxsatlarni olib tashlashda xatolik"
    fi
}

postgresql_list_databases() {
    show_menu_header "POSTGRESQL MA'LUMOTLAR BAZALARI"
    
    echo -e "${GREEN}${BOLD}Barcha ma'lumotlar bazalari:${NC}\n"
    sudo -u postgres psql -c "\l+" 2>/dev/null
}

postgresql_create_database() {
    show_menu_header "YANGI POSTGRESQL MA'LUMOTLAR BAZASI"
    
    local dbname owner encoding
    
    read -p "Ma'lumotlar bazasi nomi: " dbname
    read -p "Egasi (postgres): " owner
    owner=${owner:-postgres}
    
    echo -e "\n${CYAN}Encoding tanlang:${NC}"
    echo "1) UTF8 (default)"
    echo "2) LATIN1"
    echo "3) SQL_ASCII"
    read -p "Tanlov: " enc_choice
    
    case $enc_choice in
        1) encoding="UTF8" ;;
        2) encoding="LATIN1" ;;
        3) encoding="SQL_ASCII" ;;
        *) encoding="UTF8" ;;
    esac
    
    sudo -u postgres psql -c "CREATE DATABASE $dbname OWNER $owner ENCODING '$encoding';" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Ma'lumotlar bazasi yaratildi: $dbname"
    else
        log "ERROR" "Ma'lumotlar bazasi yaratishda xatolik"
    fi
}

postgresql_drop_database() {
    show_menu_header "POSTGRESQL MA'LUMOTLAR BAZASINI O'CHIRISH"
    
    postgresql_list_databases
    
    local dbname
    read -p "O'chiriladigan ma'lumotlar bazasi: " dbname
    
    if confirm_action "DIQQAT! $dbname butunlay o'chiriladi. Tasdiqlaysizmi?"; then
        sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$dbname';" 2>/dev/null
        sudo -u postgres psql -c "DROP DATABASE $dbname;" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            log "SUCCESS" "Ma'lumotlar bazasi o'chirildi: $dbname"
        else
            log "ERROR" "O'chirishda xatolik"
        fi
    fi
}

postgresql_config_view() {
    show_menu_header "POSTGRESQL SOZLAMALARI"
    
    local pg_version=$(psql --version 2>/dev/null | awk '{print $3}' | cut -d. -f1)
    local config_file="/etc/postgresql/$pg_version/main/postgresql.conf"
    
    if [[ -f "$config_file" ]]; then
        echo -e "${CYAN}${BOLD}Asosiy sozlamalar:${NC}\n"
        grep -v "^#" "$config_file" | grep -v "^$" | head -50
    else
        log "ERROR" "Sozlamalar fayli topilmadi"
    fi
}

postgresql_config_edit() {
    show_menu_header "POSTGRESQL SOZLAMALARINI O'ZGARTIRISH"
    
    local pg_version=$(psql --version 2>/dev/null | awk '{print $3}' | cut -d. -f1)
    local config_file="/etc/postgresql/$pg_version/main/postgresql.conf"
    
    echo "1) Port o'zgartirish"
    echo "2) Maksimal ulanishlar"
    echo "3) Shared buffers hajmi"
    echo "4) Work mem hajmi"
    echo "5) Log sozlamalari"
    echo "6) Maxsus sozlama"
    echo "7) Faylni tahrirlash"
    
    read -p "Tanlov: " config_choice
    
    case $config_choice in
        1)
            read -p "Yangi port (5432): " new_port
            sudo sed -i "s/^port =.*/port = $new_port/" "$config_file" 2>/dev/null
            log "SUCCESS" "Port o'zgartirildi: $new_port"
            ;;
        2)
            read -p "Maksimal ulanishlar (100): " max_conn
            sudo sed -i "s/^max_connections =.*/max_connections = $max_conn/" "$config_file" 2>/dev/null
            log "SUCCESS" "max_connections = $max_conn"
            ;;
        3)
            read -p "Shared buffers hajmi (128MB): " shared_buffers
            sudo sed -i "s/^shared_buffers =.*/shared_buffers = $shared_buffers/" "$config_file" 2>/dev/null
            log "SUCCESS" "shared_buffers = $shared_buffers"
            ;;
        4)
            read -p "Work mem hajmi (4MB): " work_mem
            sudo sed -i "s/^work_mem =.*/work_mem = $work_mem/" "$config_file" 2>/dev/null
            log "SUCCESS" "work_mem = $work_mem"
            ;;
        5)
            echo "log_directory = 'pg_log'" >> "$config_file" 2>/dev/null
            echo "log_filename = 'postgresql-%Y-%m-%d.log'" >> "$config_file" 2>/dev/null
            log "SUCCESS" "Log sozlamalari yangilandi"
            ;;
        6)
            read -p "O'zgaruvchi nomi: " var_name
            read -p "Yangi qiymat: " var_value
            echo "$var_name = $var_value" >> "$config_file" 2>/dev/null
            log "SUCCESS" "$var_name = $var_value"
            ;;
        7)
            sudo nano "$config_file"
            log "INFO" "Sozlamalar fayli tahrirlandi"
            ;;
        *) log_error "Noto'g'ri tanlov" && return ;;
    esac
    
    if confirm_action "PostgreSQL ni qayta ishga tushirish kerak. Hozir bajaramizmi?"; then
        sudo systemctl restart postgresql 2>/dev/null
        log "SUCCESS" "PostgreSQL qayta ishga tushirildi"
    fi
}

postgresql_generate_url() {
    show_menu_header "POSTGRESQL ULANISH URL GENERATSIYASI"
    
    local host port user password database
    
    if [[ -f "$CONFIG_DIR/postgres_current.conf" ]]; then
        source "$CONFIG_DIR/postgres_current.conf"
    else
        read -p "Host (localhost): " host
        host=${host:-localhost}
        read -p "Port (5432): " port
        port=${port:-5432}
        read -p "User: " user
        read -s -p "Password: " password
        echo ""
        read -p "Database: " database
    fi
    
    generate_postgresql_url "$host" "$port" "$user" "$password" "$database"
    
    if confirm_action "Bu sozlamalarni saqlash kerakmi?"; then
        cat > "$CONFIG_DIR/postgres_current.conf" << EOF
PG_HOST="$host"
PG_PORT="$port"
PG_USER="$user"
PG_PASSWORD="$password"
PG_DATABASE="$database"
EOF
        log "SUCCESS" "Sozlamalar saqlandi"
    fi
}

postgresql_performance_stats() {
    show_menu_header "POSTGRESQL PERFORMANS STATISTIKASI"
    
    echo -e "${CYAN}${BOLD}So'rovlar statistikasi:${NC}\n"
    sudo -u postgres psql -c "SELECT sum(xact_commit) as commits, sum(xact_rollback) as rollbacks, sum(blks_read) as blocks_read, sum(blks_hit) as blocks_hit FROM pg_stat_database;" 2>/dev/null
}

# ============================================================================
# UMUMIY FUNKSIYALAR
# ============================================================================

run_benchmark() {
    show_menu_header "DATABASE BENCHMARK"
    
    echo "1) MySQL benchmark"
    echo "2) PostgreSQL benchmark"
    echo "3) Ikkalasini solishtirish"
    
    read -p "Tanlov: " bench_choice
    
    case $bench_choice in
        1)
            if check_mysql; then
                log "INFO" "MySQL benchmark boshlanmoqda..."
                sudo mysql -e "CREATE DATABASE IF NOT EXISTS benchmark;" 2>/dev/null
                sudo mysql -e "USE benchmark; CREATE TABLE IF NOT EXISTS test (id INT PRIMARY KEY AUTO_INCREMENT, data VARCHAR(255));" 2>/dev/null
                
                echo -e "\n${CYAN}Yozish testi:${NC}"
                time (for i in {1..100}; do
                    sudo mysql -e "INSERT INTO benchmark.test (data) VALUES ('test_data_$i');" 2>/dev/null
                done)
                
                sudo mysql -e "DROP DATABASE benchmark;" 2>/dev/null
            else
                log "ERROR" "MySQL o'rnatilmagan"
            fi
            ;;
        2)
            if check_postgresql; then
                log "INFO" "PostgreSQL benchmark boshlanmoqda..."
                sudo -u postgres psql -c "CREATE DATABASE benchmark;" 2>/dev/null
                sudo -u postgres psql -d benchmark -c "CREATE TABLE test (id SERIAL PRIMARY KEY, data VARCHAR(255));" 2>/dev/null
                
                echo -e "\n${CYAN}Yozish testi:${NC}"
                time (for i in {1..100}; do
                    sudo -u postgres psql -d benchmark -c "INSERT INTO test (data) VALUES ('test_data_$i');" 2>/dev/null
                done)
                
                sudo -u postgres psql -c "DROP DATABASE benchmark;" 2>/dev/null
            else
                log "ERROR" "PostgreSQL o'rnatilmagan"
            fi
            ;;
        3)
            log "INFO" "MySQL vs PostgreSQL solishtirish"
            run_benchmark 1
            run_benchmark 2
            ;;
        *) log_error "Noto'g'ri tanlov" ;;
    esac
    press_enter
}

backup_menu() {
    while true; do
        clear
        show_menu_header "BACKUP/RESTORE MARKAZI"
        
        echo "1) 📤 MySQL backup"
        echo "2) 📥 MySQL restore"
        echo "3) 📤 PostgreSQL backup"
        echo "4) 📥 PostgreSQL restore"
        echo "5) 📋 Backup ro'yxati"
        echo "6) 🔄 Avtomatik backup sozlash"
        echo "7) 🗑️ Eski backup'larni tozalash"
        echo "8) ◀️ Orqaga"
        
        read -p "Tanlov: " backup_choice
        
        case $backup_choice in
            1)
                if check_mysql; then
                    mysql_list_databases
                    read -p "Backup qilinadigan DB: " dbname
                    backup_file="$BACKUP_DIR/mysql_${dbname}_$(date +%Y%m%d_%H%M%S).sql"
                    sudo mysqldump "$dbname" > "$backup_file" 2>/dev/null
                    gzip "$backup_file" 2>/dev/null
                    log "SUCCESS" "Backup yaratildi: ${backup_file}.gz"
                fi
                ;;
            2)
                if check_mysql; then
                    echo "Mavjud backup'lar:"
                    ls -lh "$BACKUP_DIR"/mysql_*.sql.gz 2>/dev/null
                    read -p "Backup fayl: " backup_file
                    read -p "Restore qilinadigan DB: " dbname
                    gunzip -c "$backup_file" | sudo mysql "$dbname" 2>/dev/null
                    log "SUCCESS" "Restore bajarildi"
                fi
                ;;
            3)
                if check_postgresql; then
                    postgresql_list_databases
                    read -p "Backup qilinadigan DB: " dbname
                    backup_file="$BACKUP_DIR/postgres_${dbname}_$(date +%Y%m%d_%H%M%S).sql"
                    sudo -u postgres pg_dump "$dbname" > "$backup_file" 2>/dev/null
                    gzip "$backup_file" 2>/dev/null
                    log "SUCCESS" "Backup yaratildi: ${backup_file}.gz"
                fi
                ;;
            4)
                if check_postgresql; then
                    echo "Mavjud backup'lar:"
                    ls -lh "$BACKUP_DIR"/postgres_*.sql.gz 2>/dev/null
                    read -p "Backup fayl: " backup_file
                    read -p "Restore qilinadigan DB: " dbname
                    gunzip -c "$backup_file" | sudo -u postgres psql "$dbname" 2>/dev/null
                    log "SUCCESS" "Restore bajarildi"
                fi
                ;;
            5)
                echo -e "\n${CYAN}MySQL backup'lar:${NC}"
                ls -lh "$BACKUP_DIR"/mysql_*.sql.gz 2>/dev/null || echo "Topilmadi"
                echo -e "\n${CYAN}PostgreSQL backup'lar:${NC}"
                ls -lh "$BACKUP_DIR"/postgres_*.sql.gz 2>/dev/null || echo "Topilmadi"
                ;;
            6)
                echo "0 2 * * * root $SCRIPT_DIR/settingsdbpro.sh --auto-backup mysql" > /etc/cron.d/db_auto_backup 2>/dev/null
                echo "0 3 * * * root $SCRIPT_DIR/settingsdbpro.sh --auto-backup postgresql" >> /etc/cron.d/db_auto_backup 2>/dev/null
                log "SUCCESS" "Avtomatik backup sozlandi (soat 02:00 va 03:00)"
                ;;
            7)
                find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete 2>/dev/null
                log "SUCCESS" "7 kundan eski backup'lar tozalandi"
                ;;
            8) break ;;
            *) log_error "Noto'g'ri tanlov" ;;
        esac
        press_enter
    done
}

connection_manager() {
    while true; do
        clear
        show_menu_header "ULANISH MANAGERI"
        
        echo "1) 📋 Saqlangan ulanishlar"
        echo "2) ➕ Yangi ulanish qo'shish"
        echo "3) ✏️ Ulanishni tahrirlash"
        echo "4) 🗑️ Ulanishni o'chirish"
        echo "5) 🔌 Ulanishni test qilish"
        echo "6) 🔑 SSL sozlamalari"
        echo "7) ◀️ Orqaga"
        
        read -p "Tanlov: " conn_choice
        
        case $conn_choice in
            1)
                if [[ -f "$CONNECTION_FILE" ]]; then
                    cat "$CONNECTION_FILE"
                else
                    echo "Saqlangan ulanishlar yo'q"
                fi
                ;;
            2)
                read -p "Ulanish nomi: " conn_name
                read -p "Database turi (mysql/postgresql): " db_type
                read -p "Host: " host
                read -p "Port: " port
                read -p "User: " user
                read -s -p "Password: " password
                echo ""
                read -p "Database: " database
                
                cat >> "$CONNECTION_FILE" << EOF
[$conn_name]
type=$db_type
host=$host
port=$port
user=$user
password=$password
database=$database
EOF
                log "SUCCESS" "Ulanish saqlandi"
                ;;
            5)
                read -p "Ulanish nomi: " conn_name
                echo "Test qilish funksiyasi ishlab chiqilmoqda..."
                ;;
            6)
                mkdir -p "$SSL_DIR"
                echo "SSL sertifikatlar $SSL_DIR papkasida saqlanadi"
                ;;
            7) break ;;
            *) log_error "Noto'g'ri tanlov" ;;
        esac
        press_enter
    done
}

monitoring_menu() {
    while true; do
        clear
        show_menu_header "MONITORING MARKAZI"
        
        echo "1) 📊 Real-time monitoring"
        echo "2) 📉 Performans metrikalari"
        echo "3) 📋 Hisobot generatsiya"
        echo "4) ◀️ Orqaga"
        
        read -p "Tanlov: " mon_choice
        
        case $mon_choice in
            1)
                watch -n 2 "echo 'MySQL:' && mysql -e 'SHOW PROCESSLIST' 2>/dev/null | head -20 && echo '\nPostgreSQL:' && psql -c 'SELECT * FROM pg_stat_activity' 2>/dev/null | head -20"
                ;;
            2)
                echo -e "${CYAN}MySQL:${NC}"
                mysql_performance_stats
                echo -e "\n${CYAN}PostgreSQL:${NC}"
                postgresql_performance_stats
                ;;
            3)
                report_file="$LOG_DIR/report_$(date +%Y%m%d).txt"
                {
                    echo "DATABASE HISOBOT $(date)"
                    echo "========================"
                    echo ""
                    echo "MySQL status:"
                    mysql_status
                    echo ""
                    echo "PostgreSQL status:"
                    postgresql_status
                } > "$report_file" 2>/dev/null
                log "SUCCESS" "Hisobot yaratildi: $report_file"
                ;;
            4) break ;;
            *) log_error "Noto'g'ri tanlov" ;;
        esac
        press_enter
    done
}

# ============================================================================
# ASOSIY MENYU
# ============================================================================

main_menu() {
    while true; do
        show_header
        
        echo -e "${GREEN}1)${NC} 📀 MySQL boshqaruvi"
        echo -e "${GREEN}2)${NC} 🐘 PostgreSQL boshqaruvi"
        echo -e "${GREEN}3)${NC} 🔌 Connection manager"
        echo -e "${GREEN}4)${NC} 📦 Backup/Restore"
        echo -e "${GREEN}5)${NC} 📊 Monitoring"
        echo -e "${GREEN}6)${NC} ⚡ Benchmark"
        echo -e "${GREEN}7)${NC} 🧹 Kesh tozalash"
        echo -e "${GREEN}8)${NC} 👑 Root fayllarini boshqarish"
        echo -e "${GREEN}9)${NC} 📁 Dastur papkalarini tozalash"
        echo -e "${GREEN}10)${NC} 📜 Loglarni ko'rish"
        echo -e "${GREEN}11)${NC} ℹ️ Tizim ma'lumotlari"
        echo -e "${GREEN}12)${NC} 🔧 Sozlamalar"
        echo -e "${GREEN}13)${NC} 🚪 Chiqish"
        
        echo -e "\n${YELLOW}Tanlang [1-13]:${NC} "
        read main_choice
        
        case $main_choice in
            1)
                while true; do
                    clear
                    show_menu_header "MYSQL BOSHQARUVI"
                    
                    echo "1) 📊 Holat"
                    echo "2) 👥 Foydalanuvchilar"
                    echo "3) ➕ Foydalanuvchi qo'shish"
                    echo "4) 🗑️ Foydalanuvchi o'chirish"
                    echo "5) 🔑 Parol o'zgartirish"
                    echo "6) 🔐 Ruxsatlar berish"
                    echo "7) 🔓 Ruxsatlarni ko'rish"
                    echo "8) 🔒 Ruxsatlarni olib tashlash"
                    echo "9) 🗄️ Ma'lumotlar bazalari"
                    echo "10) ➕ DB qo'shish"
                    echo "11) 🗑️ DB o'chirish"
                    echo "12) ⚙️ Sozlamalar"
                    echo "13) 🔗 URL generatsiya"
                    echo "14) 📊 Performans statistikasi"
                    echo "15) ◀️ Orqaga"
                    
                    read -p "Tanlov: " mysql_choice
                    
                    case $mysql_choice in
                        1) mysql_status ;;
                        2) mysql_list_users ;;
                        3) mysql_create_user ;;
                        4) mysql_delete_user ;;
                        5) mysql_change_password ;;
                        6) mysql_grant_privileges ;;
                        7) mysql_show_grants ;;
                        8) mysql_revoke_privileges ;;
                        9) mysql_list_databases ;;
                        10) mysql_create_database ;;
                        11) mysql_drop_database ;;
                        12)
                            echo "1) Sozlamalarni ko'rish"
                            echo "2) Sozlamalarni o'zgartirish"
                            read -p "Tanlov: " cfg_choice
                            if [ "$cfg_choice" == "1" ]; then
                                mysql_config_view
                            else
                                mysql_config_edit
                            fi
                            ;;
                        13) mysql_generate_url ;;
                        14) mysql_performance_stats ;;
                        15) break ;;
                        *) log_error "Noto'g'ri tanlov" ;;
                    esac
                    press_enter
                done
                ;;
            2)
                while true; do
                    clear
                    show_menu_header "POSTGRESQL BOSHQARUVI"
                    
                    echo "1) 📊 Holat"
                    echo "2) 👥 Foydalanuvchilar"
                    echo "3) ➕ Foydalanuvchi qo'shish"
                    echo "4) 🗑️ Foydalanuvchi o'chirish"
                    echo "5) 🔑 Parol o'zgartirish"
                    echo "6) 🔐 Ruxsatlar berish"
                    echo "7) 🔓 Ruxsatlarni ko'rish"
                    echo "8) 🔒 Ruxsatlarni olib tashlash"
                    echo "9) 🗄️ Ma'lumotlar bazalari"
                    echo "10) ➕ DB qo'shish"
                    echo "11) 🗑️ DB o'chirish"
                    echo "12) ⚙️ Sozlamalar"
                    echo "13) 🔗 URL generatsiya"
                    echo "14) 📊 Performans statistikasi"
                    echo "15) ◀️ Orqaga"
                    
                    read -p "Tanlov: " pgsql_choice
                    
                    case $pgsql_choice in
                        1) postgresql_status ;;
                        2) postgresql_list_users ;;
                        3) postgresql_create_user ;;
                        4) postgresql_delete_user ;;
                        5) postgresql_change_password ;;
                        6) postgresql_grant_privileges ;;
                        7) postgresql_show_grants ;;
                        8) postgresql_revoke_privileges ;;
                        9) postgresql_list_databases ;;
                        10) postgresql_create_database ;;
                        11) postgresql_drop_database ;;
                        12)
                            echo "1) Sozlamalarni ko'rish"
                            echo "2) Sozlamalarni o'zgartirish"
                            read -p "Tanlov: " cfg_choice
                            if [ "$cfg_choice" == "1" ]; then
                                postgresql_config_view
                            else
                                postgresql_config_edit
                            fi
                            ;;
                        13) postgresql_generate_url ;;
                        14) postgresql_performance_stats ;;
                        15) break ;;
                        *) log_error "Noto'g'ri tanlov" ;;
                    esac
                    press_enter
                done
                ;;
            3) connection_manager ;;
            4) backup_menu ;;
            5) monitoring_menu ;;
            6) run_benchmark ;;
            7) clean_cache ;;
            8) clean_root_files ;;
            9) clean_program_folders ;;
            10)
                tail -50 "$LOG_DIR/db_manager.log" 2>/dev/null
                press_enter
                ;;
            11)
                echo -e "\n${CYAN}Tizim ma'lumotlari:${NC}"
                echo "Ubuntu: $(lsb_release -d 2>/dev/null | cut -f2)"
                echo "Kernel: $(uname -r)"
                echo "CPU: $(nproc) core"
                echo "RAM: $(free -h 2>/dev/null | grep Mem | awk '{print $2}')"
                echo "Disk: $(df -h / 2>/dev/null | awk 'NR==2 {print $2}')"
                echo "MySQL: $(mysql --version 2>/dev/null || echo 'O\'rnatilmagan')"
                echo "PostgreSQL: $(psql --version 2>/dev/null || echo 'O\'rnatilmagan')"
                press_enter
                ;;
            12)
                echo "Sozlamalar fayli: $CONFIG_DIR"
                echo "Log fayli: $LOG_DIR"
                echo "Backup papka: $BACKUP_DIR"
                echo "Kesh papka: $CACHE_DIR"
                echo "Data papka: $DATA_DIR"
                echo "Archive papka: $ARCHIVE_DIR"
                press_enter
                ;;
            13)
                log "INFO" "Dastur yakunlandi"
                exit 0
                ;;
            *) log_error "Noto'g'ri tanlov: $main_choice" ;;
        esac
    done
}

# ============================================================================
# SKRIPTNI ISHGA TUSHIRISH
# ============================================================================

# Root huquqlarini tekshirish
if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}Bu skript root huquqlari bilan ishga tushirilishi kerak!${NC}"
    echo -e "Foydalanish: ${YELLOW}sudo bash $0${NC}"
    exit 1
fi

# Komanda satri argumentlarini qayta ishlash
if [[ $# -gt 0 ]]; then
    case $1 in
        --auto-backup)
            case $2 in
                mysql)
                    for db in $(sudo mysql -e "SHOW DATABASES;" 2>/dev/null | grep -v "Database\|information_schema\|performance_schema\|mysql\|sys"); do
                        backup_file="$BACKUP_DIR/mysql_${db}_$(date +%Y%m%d).sql"
                        sudo mysqldump "$db" 2>/dev/null | gzip > "${backup_file}.gz" 2>/dev/null
                    done
                    ;;
                postgresql)
                    for db in $(sudo -u postgres psql -c "\l" 2>/dev/null | grep -v "template\|postgres" | awk '{print $1}' | grep -v "List\|Name\|--\|("); do
                        backup_file="$BACKUP_DIR/postgres_${db}_$(date +%Y%m%d).sql"
                        sudo -u postgres pg_dump "$db" 2>/dev/null | gzip > "${backup_file}.gz" 2>/dev/null
                    done
                    ;;
            esac
            ;;
        --clean-cache)
            clean_cache
            ;;
        --clean-root)
            clean_root_files
            ;;
        --clean-folders)
            clean_program_folders
            ;;
        --help)
            echo "Foydalanish: sudo $0 [OPTION]"
            echo "Options:"
            echo "  --auto-backup [mysql|postgresql]  Avtomatik backup"
            echo "  --clean-cache                      Kesh tozalash"
            echo "  --clean-root                       Root fayllarini tozalash"
            echo "  --clean-folders                    Dastur papkalarini tozalash"
            echo "  --help                             Yordam"
            ;;
        *)
            main_menu
            ;;
    esac
else
    main_menu
fi