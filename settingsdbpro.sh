#!/bin/bash

# ============================================================================
# PROFESSIONAL DATABASE MANAGEMENT SYSTEM
# Version: 3.0 (Enterprise Edition)
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
SCRIPT_VERSION="3.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/db_configs"
BACKUP_DIR="$SCRIPT_DIR/db_backups"
LOG_DIR="$SCRIPT_DIR/db_logs"
SSL_DIR="$SCRIPT_DIR/db_ssl"
TEMP_DIR="$SCRIPT_DIR/db_temp"
CONNECTION_FILE="$CONFIG_DIR/connections.db"
HISTORY_FILE="$LOG_DIR/command_history.log"

# Papkalarni yaratish
mkdir -p "$CONFIG_DIR" "$BACKUP_DIR" "$LOG_DIR" "$SSL_DIR" "$TEMP_DIR"
touch "$CONNECTION_FILE" "$HISTORY_FILE"

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
        # Default qiymatlar
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
        # Default qiymatlar
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
    
    # URL formatlari
    echo -e "\n${CYAN}${BOLD}MySQL Ulanish URL'lari:${NC}\n"
    
    # Standard URL
    echo -e "${WHITE}Standard URL:${NC}"
    echo "mysql://$user:$password@$host:$port/$database"
    
    # JDBC URL
    echo -e "\n${WHITE}JDBC URL:${NC}"
    echo "jdbc:mysql://$host:$port/$database?user=$user&password=$password"
    
    # Python SQLAlchemy URL
    echo -e "\n${WHITE}Python SQLAlchemy URL:${NC}"
    echo "mysql+pymysql://$user:$password@$host:$port/$database"
    
    # PHP PDO URL
    echo -e "\n${WHITE}PHP PDO URL:${NC}"
    echo "\$pdo = new PDO('mysql:host=$host;port=$port;dbname=$database', '$user', '$password');"
    
    # Node.js mysql2 URL
    echo -e "\n${WHITE}Node.js mysql2 URL:${NC}"
    echo "const mysql = require('mysql2');"
    echo "const connection = mysql.createConnection({"
    echo "  host: '$host',"
    echo "  port: $port,"
    echo "  user: '$user',"
    echo "  password: '$password',"
    echo "  database: '$database'"
    echo "});"
    
    # Command line
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
    
    # Standard URL
    echo -e "${WHITE}Standard URL:${NC}"
    echo "postgresql://$user:$password@$host:$port/$database"
    
    # JDBC URL
    echo -e "\n${WHITE}JDBC URL:${NC}"
    echo "jdbc:postgresql://$host:$port/$database?user=$user&password=$password"
    
    # Python SQLAlchemy URL
    echo -e "\n${WHITE}Python SQLAlchemy URL:${NC}"
    echo "postgresql+psycopg2://$user:$password@$host:$port/$database"
    echo "postgresql+asyncpg://$user:$password@$host:$port/$database"
    
    # PHP PDO URL
    echo -e "\n${WHITE}PHP PDO URL:${NC}"
    echo "\$pdo = new PDO('pgsql:host=$host;port=$port;dbname=$database', '$user', '$password');"
    
    # Node.js pg URL
    echo -e "\n${WHITE}Node.js pg URL:${NC}"
    echo "const { Client } = require('pg');"
    echo "const client = new Client({"
    echo "  host: '$host',"
    echo "  port: $port,"
    echo "  user: '$user',"
    echo "  password: '$password',"
    echo "  database: '$database'"
    echo "});"
    
    # Command line
    echo -e "\n${WHITE}Command line:${NC}"
    echo "psql -h $host -p $port -U $user -d $database"
    
    # Libpq connection string
    echo -e "\n${WHITE}Libpq Connection String:${NC}"
    echo "host=$host port=$port dbname=$database user=$user password=$password"
}

# ============================================================================
# MYSQL FUNKSIYALARI (TO'LIQ)
# ============================================================================

# MySQL mavjudligini tekshirish
check_mysql() {
    if ! command -v mysql &> /dev/null; then
        return 1
    fi
    return 0
}

# MySQL holatini ko'rish
mysql_status() {
    show_menu_header "MySQL HOLATI"
    
    if ! check_mysql; then
        log "ERROR" "MySQL o'rnatilmagan"
        return 1
    fi
    
    # Xizmat holati
    echo -e "${CYAN}${BOLD}Xizmat holati:${NC}"
    sudo systemctl status mysql --no-pager -l | grep -E "Active|Loaded"
    
    # Versiya
    echo -e "\n${CYAN}${BOLD}Versiya:${NC}"
    mysql --version
    
    # Port
    echo -e "\n${CYAN}${BOLD}Port:${NC}"
    sudo ss -tlnp | grep mysql || echo "3306"
    
    # Ulanishlar
    echo -e "\n${CYAN}${BOLD}Faol ulanishlar:${NC}"
    sudo mysql -e "SHOW STATUS LIKE 'Threads_connected';" 2>/dev/null | grep Threads_connected
    
    # Ma'lumotlar bazalari soni
    echo -e "\n${CYAN}${BOLD}Ma'lumotlar bazalari:${NC}"
    sudo mysql -e "SHOW DATABASES;" 2>/dev/null | wc -l | xargs echo "Jami:"
    
    # Processlist
    echo -e "\n${CYAN}${BOLD}Processlar:${NC}"
    sudo mysql -e "SHOW PROCESSLIST;" 2>/dev/null | head -10
    
    # Sozlamalar
    echo -e "\n${CYAN}${BOLD}Muhim sozlamalar:${NC}"
    sudo mysql -e "SHOW VARIABLES WHERE Variable_name IN ('max_connections', 'innodb_buffer_pool_size', 'wait_timeout', 'interactive_timeout');" 2>/dev/null
}

# MySQL foydalanuvchilari
mysql_list_users() {
    show_menu_header "MYSQL FOYDALANUVCHILARI"
    
    if ! check_mysql; then
        log "ERROR" "MySQL o'rnatilmagan"
        return 1
    fi
    
    echo -e "${GREEN}${BOLD}Barcha foydalanuvchilar:${NC}\n"
    sudo mysql -e "SELECT 
        User, 
        Host, 
        plugin,
        authentication_string as Password_Hash,
        account_locked,
        password_expired
    FROM mysql.user 
    ORDER BY User;" 2>/dev/null | column -t -s $'\t'
    
    echo -e "\n${GREEN}${BOLD}Grantlar bilan:${NC}\n"
    sudo mysql -e "SELECT 
        User, 
        Host, 
        Grant_priv,
        Super_priv,
        Create_user_priv
    FROM mysql.user;" 2>/dev/null | column -t -s $'\t'
}

# Yangi MySQL foydalanuvchi yaratish
mysql_create_user() {
    show_menu_header "YANGI MYSQL FOYDALANUVCHI"
    
    local username host password auth_plugin
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Xost (localhost/192.168.%/%): " host
    read -s -p "Parol: " password
    echo ""
    
    # Authentication plugin tanlash
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
    
    # Foydalanuvchi yaratish
    sudo mysql -e "CREATE USER '$username'@'$host' IDENTIFIED WITH $auth_plugin BY '$password';" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Foydalanuvchi yaratildi: $username@$host"
        
        # Maxsus sozlamalar
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

# MySQL foydalanuvchi o'chirish
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

# MySQL foydalanuvchi parolini o'zgartirish
mysql_change_password() {
    show_menu_header "MYSQL PAROL O'ZGARTIRISH"
    
    local username host old_password new_password
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Xost: " host
    read -s -p "Eski parol: " old_password
    echo ""
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

# MySQL grantlar qo'shish
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
        5) 
            read -p "Ruxsatlarni vergul bilan yozing: " privileges
            ;;
        6)
            read -p "Ruxsatlar: " base_priv
            privileges="$base_priv WITH GRANT OPTION"
            ;;
    esac
    
    sudo mysql -e "GRANT $privileges ON $database.* TO '$username'@'$host'; FLUSH PRIVILEGES;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Ruxsatlar berildi: $privileges"
        
        # Grantlarni ko'rish
        echo -e "\n${CYAN}Yangi grantlar:${NC}"
        sudo mysql -e "SHOW GRANTS FOR '$username'@'$host';" 2>/dev/null
    else
        log "ERROR" "Ruxsat berishda xatolik"
    fi
}

# MySQL grantlarni ko'rish
mysql_show_grants() {
    show_menu_header "MYSQL GRANTLAR"
    
    local username host
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Xost: " host
    
    sudo mysql -e "SHOW GRANTS FOR '$username'@'$host';" 2>/dev/null
}

# MySQL grantlarni olib tashlash
mysql_revoke_privileges() {
    show_menu_header "MYSQL RUXSATLARNI OLIB TASHLASH"
    
    local username host database
    
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

# MySQL ma'lumotlar bazalarini ko'rish
mysql_list_databases() {
    show_menu_header "MYSQL MA'LUMOTLAR BAZALARI"
    
    echo -e "${GREEN}${BOLD}Barcha ma'lumotlar bazalari:${NC}\n"
    sudo mysql -e "SELECT 
        SCHEMA_NAME as 'Database',
        DEFAULT_CHARACTER_SET_NAME as 'Charset',
        DEFAULT_COLLATION_NAME as 'Collation'
    FROM information_schema.SCHEMATA 
    ORDER BY SCHEMA_NAME;" 2>/dev/null | column -t -s $'\t'
    
    echo -e "\n${GREEN}${BOLD}Hajmlari bilan:${NC}\n"
    sudo mysql -e "SELECT 
        table_schema as 'Database',
        ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as 'Size (MB)',
        COUNT(*) as 'Tables'
    FROM information_schema.tables 
    GROUP BY table_schema
    ORDER BY 2 DESC;" 2>/dev/null | column -t -s $'\t'
}

# Yangi MySQL ma'lumotlar bazasi yaratish
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
        
        # Foydalanuvchiga ruxsat berish
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

# MySQL ma'lumotlar bazasini o'chirish
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

# MySQL sozlamalarini ko'rish
mysql_config_view() {
    show_menu_header "MYSQL SOZLAMALARI"
    
    local config_file="/etc/mysql/mysql.conf.d/mysqld.cnf"
    
    if [[ -f "$config_file" ]]; then
        echo -e "${CYAN}${BOLD}Asosiy sozlamalar:${NC}\n"
        grep -v "^#" "$config_file" | grep -v "^$" | head -50
        
        echo -e "\n${CYAN}${BOLD}Muhim o'zgaruvchilar:${NC}\n"
        sudo mysql -e "SHOW VARIABLES WHERE Variable_name IN (
            'max_connections',
            'innodb_buffer_pool_size',
            'innodb_log_file_size',
            'query_cache_size',
            'tmp_table_size',
            'max_allowed_packet',
            'wait_timeout',
            'interactive_timeout',
            'sort_buffer_size',
            'read_buffer_size',
            'read_rnd_buffer_size',
            'join_buffer_size',
            'thread_cache_size',
            'table_open_cache'
        );" 2>/dev/null | column -t -s $'\t'
    else
        log "ERROR" "Sozlamalar fayli topilmadi"
    fi
}

# MySQL sozlamalarini o'zgartirish
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
    esac
    
    if confirm_action "MySQL ni qayta ishga tushirish kerak. Hozir bajaramizmi?"; then
        sudo systemctl restart mysql
        log "SUCCESS" "MySQL qayta ishga tushirildi"
    fi
}

# MySQL ulanish URL generatsiya
mysql_generate_url() {
    show_menu_header "MYSQL ULANISH URL GENERATSIYASI"
    
    local host port user password database
    
    # Avval saqlangan sozlamalarni o'qish
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
    
    # Sozlamalarni saqlash
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

# MySQL performans statistikasi
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
    
    echo -e "\n${CYAN}${BOLD}Eng ko'p ishlatilgan so'rovlar:${NC}\n"
    sudo mysql -e "SELECT * FROM performance_schema.events_statements_summary_by_digest ORDER BY SUM_TIMER_WAIT DESC LIMIT 10\G" 2>/dev/null
}

# ============================================================================
# POSTGRESQL FUNKSIYALARI (TO'LIQ)
# ============================================================================

# PostgreSQL mavjudligini tekshirish
check_postgresql() {
    if ! command -v psql &> /dev/null; then
        return 1
    fi
    return 0
}

# PostgreSQL holatini ko'rish
postgresql_status() {
    show_menu_header "POSTGRESQL HOLATI"
    
    if ! check_postgresql; then
        log "ERROR" "PostgreSQL o'rnatilmagan"
        return 1
    fi
    
    # Xizmat holati
    echo -e "${CYAN}${BOLD}Xizmat holati:${NC}"
    sudo systemctl status postgresql --no-pager -l | grep -E "Active|Loaded"
    
    # Versiya
    echo -e "\n${CYAN}${BOLD}Versiya:${NC}"
    sudo -u postgres psql -c "SELECT version();" 2>/dev/null | grep PostgreSQL
    
    # Port
    echo -e "\n${CYAN}${BOLD}Port:${NC}"
    sudo ss -tlnp | grep postgres || echo "5432"
    
    # Ulanishlar
    echo -e "\n${CYAN}${BOLD}Faol ulanishlar:${NC}"
    sudo -u postgres psql -c "SELECT count(*) as active_connections FROM pg_stat_activity;" 2>/dev/null
    
    # Ma'lumotlar bazalari soni
    echo -e "\n${CYAN}${BOLD}Ma'lumotlar bazalari:${NC}"
    sudo -u postgres psql -c "SELECT count(*) FROM pg_database WHERE datistemplate = false;" 2>/dev/null
    
    # Processlist
    echo -e "\n${CYAN}${BOLD}Processlar:${NC}"
    sudo -u postgres psql -x -c "SELECT * FROM pg_stat_activity WHERE state = 'active' LIMIT 5;" 2>/dev/null
    
    # Sozlamalar
    echo -e "\n${CYAN}${BOLD}Muhim sozlamalar:${NC}"
    sudo -u postgres psql -c "SELECT name, setting, unit FROM pg_settings WHERE name IN ('max_connections', 'shared_buffers', 'work_mem', 'maintenance_work_mem', 'effective_cache_size', 'wal_buffers');" 2>/dev/null
}

# PostgreSQL foydalanuvchilari
postgresql_list_users() {
    show_menu_header "POSTGRESQL FOYDALANUVCHILARI"
    
    echo -e "${GREEN}${BOLD}Barcha foydalanuvchilar:${NC}\n"
    sudo -u postgres psql -c "\du" 2>/dev/null
    
    echo -e "\n${GREEN}${BOLD}Foydalanuvchi ma'lumotlari:${NC}\n"
    sudo -u postgres psql -c "SELECT 
        rolname as username,
        rolsuper as superuser,
        rolcreaterole as create_role,
        rolcreatedb as create_db,
        rolcanlogin as can_login,
        rolreplication as replication,
        rolconnlimit as connection_limit,
        rolvaliduntil as valid_until
    FROM pg_roles 
    WHERE rolname NOT LIKE 'pg_%'
    ORDER BY rolname;" 2>/dev/null | column -t -s $'\t'
}

# Yangi PostgreSQL foydalanuvchi yaratish
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
    esac
    
    # Qo'shimcha sozlamalar
    if confirm_action "Ulanish limiti belgilansinmi?"; then
        read -p "Maksimal ulanishlar soni: " conn_limit
        options="$options CONNECTION LIMIT $conn_limit"
    fi
    
    if confirm_action "Parol amal qilish muddati belgilansinmi?"; then
        read -p "Muddat (YYYY-MM-DD formatida): " valid_until
        options="$options VALID UNTIL '$valid_until'"
    fi
    
    # Foydalanuvchi yaratish
    sudo -u postgres psql -c "CREATE USER $username WITH PASSWORD '$password' $options;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Foydalanuvchi yaratildi: $username"
    else
        log "ERROR" "Foydalanuvchi yaratishda xatolik"
    fi
}

# PostgreSQL foydalanuvchi o'chirish
postgresql_delete_user() {
    show_menu_header "POSTGRESQL FOYDALANUVCHI O'CHIRISH"
    
    postgresql_list_users
    
    local username
    read -p "Foydalanuvchi nomi: " username
    
    if confirm_action "Foydalanuvchi $username ni o'chirishni tasdiqlaysizmi?"; then
        # Avval foydalanuvchiga tegishli obyektlarni o'tkazish
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

# PostgreSQL foydalanuvchi parolini o'zgartirish
postgresql_change_password() {
    show_menu_header "POSTGRESQL PAROL O'ZGARTIRISH"
    
    local username new_password
    
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

# PostgreSQL ruxsatlar berish
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
        5) 
            read -p "Ruxsatlarni vergul bilan yozing: " privileges
            ;;
        6)
            read -p "Ruxsatlar: " base_priv
            privileges="$base_priv WITH GRANT OPTION"
            ;;
    esac
    
    # Ma'lumotlar bazasiga ruxsat
    sudo -u postgres psql -c "GRANT CONNECT ON DATABASE $database TO $username;" 2>/dev/null
    sudo -u postgres psql -c "GRANT $privileges ON ALL TABLES IN SCHEMA public TO $username;" 2>/dev/null
    sudo -u postgres psql -c "GRANT $privileges ON ALL SEQUENCES IN SCHEMA public TO $username;" 2>/dev/null
    sudo -u postgres psql -c "GRANT $privileges ON ALL FUNCTIONS IN SCHEMA public TO $username;" 2>/dev/null
    
    # Default ruxsatlar
    sudo -u postgres psql -d "$database" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT $privileges ON TABLES TO $username;" 2>/dev/null
    sudo -u postgres psql -d "$database" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT $privileges ON SEQUENCES TO $username;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Ruxsatlar berildi: $username"
        
        # Grantlarni ko'rish
        echo -e "\n${CYAN}Yangi grantlar:${NC}"
        sudo -u postgres psql -c "\dp $database.*" 2>/dev/null | head -20
    else
        log "ERROR" "Ruxsat berishda xatolik"
    fi
}

# PostgreSQL grantlarni ko'rish
postgresql_show_grants() {
    show_menu_header "POSTGRESQL GRANTLAR"
    
    local username
    
    read -p "Foydalanuvchi nomi: " username
    
    sudo -u postgres psql -c "\du $username" 2>/dev/null
    sudo -u postgres psql -c "\dp" 2>/dev/null | grep "$username" || echo "Grantlar topilmadi"
}

# PostgreSQL ruxsatlarni olib tashlash
postgresql_revoke_privileges() {
    show_menu_header "POSTGRESQL RUXSATLARNI OLIB TASHLASH"
    
    local username database
    
    read -p "Foydalanuvchi nomi: " username
    read -p "Ma'lumotlar bazasi: " database
    
    echo -e "\n${CYAN}Mavjud grantlar:${NC}"
    sudo -u postgres psql -c "\dp $database.*" 2>/dev/null | grep "$username"
    
    read -p "Olib tashlanadigan ruxsatlar: " privileges
    
    sudo -u postgres psql -c "REVOKE $privileges ON ALL TABLES IN SCHEMA public FROM $username;" 2>/dev/null
    sudo -u postgres psql -c "REVOKE $privileges ON ALL SEQUENCES IN SCHEMA public FROM $username;" 2>/dev/null
    sudo -u postgres psql -c "REVOKE $privileges ON ALL FUNCTIONS IN SCHEMA public FROM $username;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Ruxsatlar olib tashlandi"
    else
        log "ERROR" "Ruxsatlarni olib tashlashda xatolik"
    fi
}

# PostgreSQL ma'lumotlar bazalarini ko'rish
postgresql_list_databases() {
    show_menu_header "POSTGRESQL MA'LUMOTLAR BAZALARI"
    
    echo -e "${GREEN}${BOLD}Barcha ma'lumotlar bazalari:${NC}\n"
    sudo -u postgres psql -c "\l+" 2>/dev/null
    
    echo -e "\n${GREEN}${BOLD}Hajmlari bilan:${NC}\n"
    sudo -u postgres psql -c "SELECT 
        datname as database,
        pg_database_size(datname) / 1024 / 1024 as size_mb,
        pg_size_pretty(pg_database_size(datname)) as size_pretty
    FROM pg_database 
    WHERE datistemplate = false
    ORDER BY size_mb DESC;" 2>/dev/null
}

# Yangi PostgreSQL ma'lumotlar bazasi yaratish
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

# PostgreSQL ma'lumotlar bazasini o'chirish
postgresql_drop_database() {
    show_menu_header "POSTGRESQL MA'LUMOTLAR BAZASINI O'CHIRISH"
    
    postgresql_list_databases
    
    local dbname
    read -p "O'chiriladigan ma'lumotlar bazasi: " dbname
    
    if confirm_action "DIQQAT! $dbname butunlay o'chiriladi. Tasdiqlaysizmi?"; then
        # Ulanishlarni uzish
        sudo -u postgres psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$dbname';" 2>/dev/null
        sudo -u postgres psql -c "DROP DATABASE $dbname;" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            log "SUCCESS" "Ma'lumotlar bazasi o'chirildi: $dbname"
        else
            log "ERROR" "O'chirishda xatolik"
        fi
    fi
}

# PostgreSQL sozlamalarini ko'rish
postgresql_config_view() {
    show_menu_header "POSTGRESQL SOZLAMALARI"
    
    PG_VERSION=$(psql --version | awk '{print $3}' | cut -d. -f1)
    local config_file="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    
    if [[ -f "$config_file" ]]; then
        echo -e "${CYAN}${BOLD}Asosiy sozlamalar:${NC}\n"
        grep -v "^#" "$config_file" | grep -v "^$" | head -50
        
        echo -e "\n${CYAN}${BOLD}Muhim o'zgaruvchilar:${NC}\n"
        sudo -u postgres psql -c "SELECT name, setting, unit FROM pg_settings WHERE name IN (
            'max_connections',
            'shared_buffers',
            'work_mem',
            'maintenance_work_mem',
            'effective_cache_size',
            'wal_buffers',
            'checkpoint_completion_target',
            'random_page_cost',
            'effective_io_concurrency'
        );" 2>/dev/null | column -t -s $'\t'
        
        echo -e "\n${CYAN}${BOLD}Client sozlamalari:${NC}\n"
        grep -A 10 "^# - Connection Settings" "$config_file" | grep -v "^#"
    else
        log "ERROR" "Sozlamalar fayli topilmadi"
    fi
}

# PostgreSQL sozlamalarini o'zgartirish
postgresql_config_edit() {
    show_menu_header "POSTGRESQL SOZLAMALARINI O'ZGARTIRISH"
    
    PG_VERSION=$(psql --version | awk '{print $3}' | cut -d. -f1)
    local config_file="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    
    echo "1) Port o'zgartirish"
    echo "2) Maksimal ulanishlar"
    echo "3) Shared buffers hajmi"
    echo "4) Work mem hajmi"
    echo "5) WAL sozlamalari"
    echo "6) Log sozlamalari"
    echo "7) Maxsus sozlama"
    echo "8) Faylni tahrirlash"
    
    read -p "Tanlov: " config_choice
    
    case $config_choice in
        1)
            read -p "Yangi port (5432): " new_port
            sudo sed -i "s/^port =.*/port = $new_port/" "$config_file"
            log "SUCCESS" "Port o'zgartirildi: $new_port"
            ;;
        2)
            read -p "Maksimal ulanishlar (100): " max_conn
            sudo sed -i "s/^max_connections =.*/max_connections = $max_conn/" "$config_file"
            log "SUCCESS" "max_connections = $max_conn"
            ;;
        3)
            read -p "Shared buffers hajmi (128MB): " shared_buffers
            sudo sed -i "s/^shared_buffers =.*/shared_buffers = $shared_buffers/" "$config_file"
            log "SUCCESS" "shared_buffers = $shared_buffers"
            ;;
        4)
            read -p "Work mem hajmi (4MB): " work_mem
            sudo sed -i "s/^work_mem =.*/work_mem = $work_mem/" "$config_file"
            log "SUCCESS" "work_mem = $work_mem"
            ;;
        5)
            read -p "WAL buffer hajmi (16MB): " wal_buffers
            read -p "Checkpoint timeout (5min): " checkpoint_timeout
            sudo sed -i "s/^wal_buffers =.*/wal_buffers = $wal_buffers/" "$config_file"
            sudo sed -i "s/^checkpoint_timeout =.*/checkpoint_timeout = $checkpoint_timeout/" "$config_file"
            log "SUCCESS" "WAL sozlamalari yangilandi"
            ;;
        6)
            echo "log_directory = 'pg_log'" >> "$config_file"
            echo "log_filename = 'postgresql-%Y-%m-%d.log'" >> "$config_file"
            echo "log_statement = 'all'" >> "$config_file"
            echo "log_duration = on" >> "$config_file"
            log "SUCCESS" "Log sozlamalari yangilandi"
            ;;
        7)
            read -p "O'zgaruvchi nomi: " var_name
            read -p "Yangi qiymat: " var_value
            echo "$var_name = $var_value" >> "$config_file"
            log "SUCCESS" "$var_name = $var_value"
            ;;
        8)
            sudo nano "$config_file"
            log "INFO" "Sozlamalar fayli tahrirlandi"
            ;;
    esac
    
    if confirm_action "PostgreSQL ni qayta ishga tushirish kerak. Hozir bajaramizmi?"; then
        sudo systemctl restart postgresql
        log "SUCCESS" "PostgreSQL qayta ishga tushirildi"
    fi
}

# PostgreSQL ulanish URL generatsiya
postgresql_generate_url() {
    show_menu_header "POSTGRESQL ULANISH URL GENERATSIYASI"
    
    local host port user password database
    
    # Avval saqlangan sozlamalarni o'qish
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
    
    # Sozlamalarni saqlash
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

# PostgreSQL performans statistikasi
postgresql_performance_stats() {
    show_menu_header "POSTGRESQL PERFORMANS STATISTIKASI"
    
    echo -e "${CYAN}${BOLD}So'rovlar statistikasi:${NC}\n"
    sudo -u postgres psql -c "SELECT 
        sum(xact_commit) as commits,
        sum(xact_rollback) as rollbacks,
        sum(blks_read) as blocks_read,
        sum(blks_hit) as blocks_hit
    FROM pg_stat_database;" 2>/dev/null
    
    echo -e "\n${CYAN}${BOLD}Indeks statistikasi:${NC}\n"
    sudo -u postgres psql -c "SELECT 
        schemaname,
        tablename,
        indexname,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch
    FROM pg_stat_user_indexes 
    ORDER BY idx_scan DESC 
    LIMIT 10;" 2>/dev/null
    
    echo -e "\n${CYAN}${BOLD}Eng ko'p ishlatilgan so'rovlar:${NC}\n"
    sudo -u postgres psql -c "SELECT 
        query,
        calls,
        total_time,
        rows
    FROM pg_stat_statements 
    ORDER BY total_time DESC 
    LIMIT 10;" 2>/dev/null
}

# ============================================================================
# UMUMIY FUNKSIYALAR
# ============================================================================

# Database benchmark
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
                
                # Test ma'lumotlar bazasi yaratish
                sudo mysql -e "CREATE DATABASE IF NOT EXISTS benchmark;" 2>/dev/null
                sudo mysql -e "USE benchmark; CREATE TABLE IF NOT EXISTS test (id INT PRIMARY KEY AUTO_INCREMENT, data VARCHAR(255));" 2>/dev/null
                
                # Write test
                echo -e "\n${CYAN}Yozish testi:${NC}"
                time (for i in {1..1000}; do
                    sudo mysql -e "INSERT INTO benchmark.test (data) VALUES ('test_data_$i');" 2>/dev/null
                done)
                
                # Read test
                echo -e "\n${CYAN}O'qish testi:${NC}"
                time (for i in {1..1000}; do
                    sudo mysql -e "SELECT * FROM benchmark.test WHERE id = $((RANDOM % 1000 + 1));" 2>/dev/null
                done)
                
                # Tozalash
                sudo mysql -e "DROP DATABASE benchmark;" 2>/dev/null
            else
                log "ERROR" "MySQL o'rnatilmagan"
            fi
            ;;
        2)
            if check_postgresql; then
                log "INFO" "PostgreSQL benchmark boshlanmoqda..."
                
                # Test ma'lumotlar bazasi yaratish
                sudo -u postgres psql -c "CREATE DATABASE benchmark;" 2>/dev/null
                sudo -u postgres psql -d benchmark -c "CREATE TABLE test (id SERIAL PRIMARY KEY, data VARCHAR(255));" 2>/dev/null
                
                # Write test
                echo -e "\n${CYAN}Yozish testi:${NC}"
                time (for i in {1..1000}; do
                    sudo -u postgres psql -d benchmark -c "INSERT INTO test (data) VALUES ('test_data_$i');" 2>/dev/null
                done)
                
                # Read test
                echo -e "\n${CYAN}O'qish testi:${NC}"
                time (for i in {1..1000}; do
                    sudo -u postgres psql -d benchmark -c "SELECT * FROM test WHERE id = $((RANDOM % 1000 + 1));" 2>/dev/null
                done)
                
                # Tozalash
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
    esac
}

# Backup/Restore menyusi
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
                    sudo mysqldump "$dbname" > "$backup_file"
                    gzip "$backup_file"
                    log "SUCCESS" "Backup yaratildi: ${backup_file}.gz"
                fi
                ;;
            2)
                if check_mysql; then
                    echo "Mavjud backup'lar:"
                    ls -lh "$BACKUP_DIR"/mysql_*.sql.gz
                    read -p "Backup fayl: " backup_file
                    read -p "Restore qilinadigan DB: " dbname
                    gunzip -c "$backup_file" | sudo mysql "$dbname"
                    log "SUCCESS" "Restore bajarildi"
                fi
                ;;
            3)
                if check_postgresql; then
                    postgresql_list_databases
                    read -p "Backup qilinadigan DB: " dbname
                    backup_file="$BACKUP_DIR/postgres_${dbname}_$(date +%Y%m%d_%H%M%S).sql"
                    sudo -u postgres pg_dump "$dbname" > "$backup_file"
                    gzip "$backup_file"
                    log "SUCCESS" "Backup yaratildi: ${backup_file}.gz"
                fi
                ;;
            4)
                if check_postgresql; then
                    echo "Mavjud backup'lar:"
                    ls -lh "$BACKUP_DIR"/postgres_*.sql.gz
                    read -p "Backup fayl: " backup_file
                    read -p "Restore qilinadigan DB: " dbname
                    gunzip -c "$backup_file" | sudo -u postgres psql "$dbname"
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
                echo "0 2 * * * root $SCRIPT_DIR/settingsdbpro.sh --auto-backup mysql" > /etc/cron.d/db_auto_backup
                echo "0 3 * * * root $SCRIPT_DIR/settingsdbpro.sh --auto-backup postgresql" >> /etc/cron.d/db_auto_backup
                log "SUCCESS" "Avtomatik backup sozlandi (soat 02:00 va 03:00)"
                ;;
            7)
                find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
                log "SUCCESS" "7 kundan eski backup'lar tozalandi"
                ;;
            8) break ;;
        esac
        press_enter
    done
}

# Connection manager
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
                # Ulanishni test qilish
                ;;
            6)
                mkdir -p "$SSL_DIR"
                echo "SSL sertifikatlar $SSL_DIR papkasida saqlanadi"
                ;;
            7) break ;;
        esac
        press_enter
    done
}

# Monitoring menyusi
monitoring_menu() {
    while true; do
        clear
        show_menu_header "MONITORING MARKAZI"
        
        echo "1) 📊 Real-time monitoring"
        echo "2) 📈 Grafiklar (soddalashtirilgan)"
        echo "3) 📉 Performans metrikalari"
        echo "4) 🔔 Ogohlantirishlar"
        echo "5) 📋 Hisobot generatsiya"
        echo "6) ◀️ Orqaga"
        
        read -p "Tanlov: " mon_choice
        
        case $mon_choice in
            1)
                watch -n 2 "echo 'MySQL:' && mysql -e 'SHOW PROCESSLIST' 2>/dev/null | head -20 && echo '\nPostgreSQL:' && psql -c 'SELECT * FROM pg_stat_activity' 2>/dev/null | head -20"
                ;;
            5)
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
                } > "$report_file"
                log "SUCCESS" "Hisobot yaratildi: $report_file"
                ;;
            6) break ;;
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
        echo -e "${GREEN}7)${NC} 🔧 Sozlamalar"
        echo -e "${GREEN}8)${NC} 📜 Loglarni ko'rish"
        echo -e "${GREEN}9)${NC} ℹ️ Tizim ma'lumotlari"
        echo -e "${GREEN}10)${NC} 🚪 Chiqish"
        
        echo -e "\n${YELLOW}Tanlang [1-10]:${NC} "
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
                    esac
                    press_enter
                done
                ;;
            3) connection_manager ;;
            4) backup_menu ;;
            5) monitoring_menu ;;
            6) run_benchmark ;;
            7)
                echo "Sozlamalar fayli: $CONFIG_DIR"
                echo "Log fayli: $LOG_DIR"
                echo "Backup papka: $BACKUP_DIR"
                ;;
            8)
                tail -50 "$LOG_DIR/db_manager.log"
                ;;
            9)
                echo -e "\n${CYAN}Tizim ma'lumotlari:${NC}"
                echo "Ubuntu: $(lsb_release -d | cut -f2)"
                echo "Kernel: $(uname -r)"
                echo "CPU: $(nproc) core"
                echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
                echo "Disk: $(df -h / | awk 'NR==2 {print $2}')"
                echo "MySQL: $(mysql --version 2>/dev/null || echo 'O\'rnatilmagan')"
                echo "PostgreSQL: $(psql --version 2>/dev/null || echo 'O\'rnatilmagan')"
                ;;
            10)
                log "INFO" "Dastur yakunlandi"
                exit 0
                ;;
        esac
        press_enter
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
                    mysql_list_databases
                    for db in $(sudo mysql -e "SHOW DATABASES;" | grep -v "Database\|information_schema\|performance_schema\|mysql\|sys"); do
                        backup_file="$BACKUP_DIR/mysql_${db}_$(date +%Y%m%d).sql"
                        sudo mysqldump "$db" | gzip > "${backup_file}.gz"
                    done
                    ;;
                postgresql)
                    for db in $(sudo -u postgres psql -c "\l" | grep -v "template\|postgres" | awk '{print $1}' | grep -v "List\|Name\|--\|("); do
                        backup_file="$BACKUP_DIR/postgres_${db}_$(date +%Y%m%d).sql"
                        sudo -u postgres pg_dump "$db" | gzip > "${backup_file}.gz"
                    done
                    ;;
            esac
            ;;
        --help)
            echo "Foydalanish: sudo $0 [OPTION]"
            echo "Options:"
            echo "  --auto-backup [mysql|postgresql]  Avtomatik backup"
            echo "  --help                             Yordam"
            ;;
        *)
            main_menu
            ;;
    esac
else
    main_menu
fi
