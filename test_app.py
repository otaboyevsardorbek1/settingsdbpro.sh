"""
Database model test qilish uchun skript
"""

import sys
from db_manager import DatabaseManager, Colors

def print_user(user):
    """Foydalanuvchi ma'lumotlarini chiqarish"""
    if user:
        print(f"  ID: {user.id}")
        print(f"  Chat ID: {user.chat_id}")
        print(f"  Balans: {float(user.balans):.2f}")
        print(f"  Yaratilgan: {user.created_at}")
        print(f"  Yangilangan: {user.updated_at}")
    else:
        print("  Foydalanuvchi topilmadi")

def main():
    """Asosiy test funksiyasi"""
    
    # MySQL bilan test
    print(f"{Colors.BLUE}{Colors.BOLD}=== MySQL DATABASE TEST ==={Colors.NC}")
    mysql_db = DatabaseManager(
        db_type='mysql',
        host='localhost',
        user='root',
        password='',  # MySQL parolingizni yozing
        database='test_db'
    )
    
    if mysql_db.connect():
        # Test user yaratish
        print(f"\n{Colors.CYAN}1. Test user yaratish:{Colors.NC}")
        user1 = mysql_db.create_user(123456789, 100.50)
        print_user(user1)
        
        # User olish
        print(f"\n{Colors.CYAN}2. User olish:{Colors.NC}")
        user = mysql_db.get_user(123456789)
        print_user(user)
        
        # Balans qo'shish
        print(f"\n{Colors.CYAN}3. Balans qo'shish (+50):{Colors.NC}")
        mysql_db.add_money(123456789, 50)
        
        # Balans ayirish
        print(f"\n{Colors.CYAN}4. Balans ayirish (-30):{Colors.NC}")
        mysql_db.subtract_money(123456789, 30)
        
        # Balans o'rnatish
        print(f"\n{Colors.CYAN}5. Balans o'rnatish (200):{Colors.NC}")
        mysql_db.set_money(123456789, 200)
        
        # Statistika
        print(f"\n{Colors.CYAN}6. Statistika:{Colors.NC}")
        stats = mysql_db.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Top users
        print(f"\n{Colors.CYAN}7. Top foydalanuvchilar:{Colors.NC}")
        top_users = mysql_db.get_top_users()
        for user in top_users:
            print(f"  {user.chat_id}: {float(user.balans):.2f}")
        
        # User o'chirish
        print(f"\n{Colors.CYAN}8. User o'chirish:{Colors.NC}")
        mysql_db.delete_user(123456789)
        
        # User mavjudligini tekshirish
        print(f"\n{Colors.CYAN}9. User mavjudligini tekshirish:{Colors.NC}")
        exists = mysql_db.user_exists(123456789)
        print(f"  Mavjud: {exists}")
    
    # PostgreSQL bilan test
    print(f"\n{Colors.BLUE}{Colors.BOLD}=== POSTGRESQL DATABASE TEST ==={Colors.NC}")
    pg_db = DatabaseManager(
        db_type='postgresql',
        host='localhost',
        user='postgres',
        password='postgres',  # PostgreSQL parolingizni yozing
        database='test_db'
    )
    
    if pg_db.connect():
        # Bir nechta user yaratish
        print(f"\n{Colors.CYAN}1. Bir nechta user yaratish:{Colors.NC}")
        pg_db.create_user(111111, 1000)
        pg_db.create_user(222222, 2000)
        pg_db.create_user(333333, 3000)
        
        # Barcha userlarni ko'rish
        print(f"\n{Colors.CYAN}2. Barcha userlar:{Colors.NC}")
        users = pg_db.list_users()
        for user in users:
            print(f"  {user.chat_id}: {float(user.balans):.2f}")
        
        # Pul o'tkazish
        print(f"\n{Colors.CYAN}3. Pul o'tkazish (111111 -> 222222, 500):{Colors.NC}")
        pg_db.transfer_money(111111, 222222, 500)
        
        # Top users
        print(f"\n{Colors.CYAN}4. Top foydalanuvchilar:{Colors.NC}")
        top_users = pg_db.get_top_users()
        for user in top_users:
            print(f"  {user.chat_id}: {float(user.balans):.2f}")
        
        # Statistika
        print(f"\n{Colors.CYAN}5. Statistika:{Colors.NC}")
        stats = pg_db.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Search
        print(f"\n{Colors.CYAN}6. Qidiruv (222):{Colors.NC}")
        found = pg_db.search_users('222')
        for user in found:
            print(f"  Topildi: {user.chat_id}")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}=== TEST YAKUNLANDI ==={Colors.NC}")

if __name__ == "__main__":
    main()
