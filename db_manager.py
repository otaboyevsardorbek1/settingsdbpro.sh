# db_manager.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Numeric, BigInteger, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import datetime
import os

# Ranglar (agar settingsdbpro.py dan foydalanmasangiz)
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


# Base class
Base = declarative_base()

class UserBalance(Base):
    """
    Umumiy foydalanuvchi balans modeli
    MySQL va PostgreSQL bilan ishlaydi
    """
    __tablename__ = 'user_balances'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, unique=True)
    balans = Column(Numeric(10, 2), default=0.00, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    # Indexes
    __table_args__ = (
        Index('idx_chat_id', chat_id),
        Index('idx_balans', balans),
    )
    
    def __repr__(self):
        return f"<UserBalance(id={self.id}, chat_id={self.chat_id}, balans={self.balans})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'balans': float(self.balans),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DatabaseManager:
    """
    Umumiy database boshqaruvchi klass
    MySQL va PostgreSQL ni qo'llab-quvvatlaydi
    """
    
    def __init__(self, db_type='mysql', host='localhost', port=None, 
                 user='root', password='', database='test_db'):
        """
        db_type: 'mysql' yoki 'postgresql'
        """
        self.db_type = db_type.lower()
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        
        # Default portlar
        if port is None:
            if self.db_type == 'mysql':
                self.port = 3306
            else:
                self.port = 5432
        else:
            self.port = port
        
        # Connection string yaratish
        if self.db_type == 'mysql':
            self.connection_string = f"mysql+pymysql://{user}:{password}@{host}:{self.port}/{database}"
        else:
            self.connection_string = f"postgresql://{user}:{password}@{host}:{self.port}/{database}"
        
        self.engine = None
        self.Session = None
    
    def connect(self):
        """Database ga ulanish"""
        try:
            self.engine = create_engine(self.connection_string, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            # Jadvallarni yaratish
            Base.metadata.create_all(self.engine)
            print(f"{Colors.GREEN}✅ {self.db_type.upper()} ga muvaffaqiyatli ulandi{Colors.NC}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ {self.db_type.upper()} ulanish xatosi: {e}{Colors.NC}")
            return False
    
    def get_session(self):
        """Yangi session olish"""
        if self.Session:
            return self.Session()
        return None
    
    # ==================== CRUD OPERATSIYALAR ====================
    
    def create_user(self, chat_id, initial_balance=0.00):
        """Yangi foydalanuvchi yaratish"""
        session = self.get_session()
        if not session:
            return None
        
        try:
            # Mavjudligini tekshirish
            existing = session.query(UserBalance).filter_by(chat_id=chat_id).first()
            if existing:
                print(f"{Colors.YELLOW}⚠️ Foydalanuvchi allaqachon mavjud: {chat_id}{Colors.NC}")
                return existing
            
            user = UserBalance(chat_id=chat_id, balans=initial_balance)
            session.add(user)
            session.commit()
            print(f"{Colors.GREEN}✅ Foydalanuvchi yaratildi: ID={user.id}, chat_id={chat_id}{Colors.NC}")
            return user
        except Exception as e:
            session.rollback()
            print(f"{Colors.RED}❌ Foydalanuvchi yaratishda xatolik: {e}{Colors.NC}")
            return None
        finally:
            session.close()
    
    def get_user(self, chat_id):
        """chat_id bo'yicha foydalanuvchini olish"""
        session = self.get_session()
        if not session:
            return None
        
        try:
            user = session.query(UserBalance).filter_by(chat_id=chat_id).first()
            return user
        except Exception as e:
            print(f"{Colors.RED}❌ Foydalanuvchi olishda xatolik: {e}{Colors.NC}")
            return None
        finally:
            session.close()
    
    def get_user_by_id(self, user_id):
        """ID bo'yicha foydalanuvchini olish"""
        session = self.get_session()
        if not session:
            return None
        
        try:
            user = session.query(UserBalance).filter_by(id=user_id).first()
            return user
        except Exception as e:
            print(f"{Colors.RED}❌ Foydalanuvchi olishda xatolik: {e}{Colors.NC}")
            return None
        finally:
            session.close()
    
    def update_balance(self, chat_id, amount, operation='add'):
        """
        Balansni yangilash
        operation: 'add' (qo'shish), 'subtract' (ayirish), 'set' (o'rnatish)
        """
        session = self.get_session()
        if not session:
            return None
        
        try:
            user = session.query(UserBalance).filter_by(chat_id=chat_id).first()
            if not user:
                print(f"{Colors.YELLOW}⚠️ Foydalanuvchi topilmadi: {chat_id}{Colors.NC}")
                return None
            
            old_balance = float(user.balans)
            
            if operation == 'add':
                user.balans = float(user.balans) + amount
                print(f"{Colors.GREEN}✅ {amount:.2f} qo'shildi{Colors.NC}")
            elif operation == 'subtract':
                new_balance = float(user.balans) - amount
                if new_balance < 0:
                    print(f"{Colors.YELLOW}⚠️ Balans manfiy bo'lishi mumkin emas{Colors.NC}")
                    return None
                user.balans = new_balance
                print(f"{Colors.GREEN}✅ {amount:.2f} ayirildi{Colors.NC}")
            elif operation == 'set':
                if amount < 0:
                    print(f"{Colors.YELLOW}⚠️ Balans manfiy bo'lishi mumkin emas{Colors.NC}")
                    return None
                user.balans = amount
                print(f"{Colors.GREEN}✅ Balans o'rnatildi{Colors.NC}")
            
            user.updated_at = datetime.datetime.now()
            session.commit()
            
            print(f"{Colors.CYAN}   Eski balans: {old_balance:.2f} -> Yangi balans: {float(user.balans):.2f}{Colors.NC}")
            return user
        except Exception as e:
            session.rollback()
            print(f"{Colors.RED}❌ Balans yangilashda xatolik: {e}{Colors.NC}")
            return None
        finally:
            session.close()
    
    def delete_user(self, chat_id):
        """Foydalanuvchini o'chirish"""
        session = self.get_session()
        if not session:
            return False
        
        try:
            user = session.query(UserBalance).filter_by(chat_id=chat_id).first()
            if not user:
                print(f"{Colors.YELLOW}⚠️ Foydalanuvchi topilmadi: {chat_id}{Colors.NC}")
                return False
            
            session.delete(user)
            session.commit()
            print(f"{Colors.GREEN}✅ Foydalanuvchi o'chirildi: {chat_id}{Colors.NC}")
            return True
        except Exception as e:
            session.rollback()
            print(f"{Colors.RED}❌ Foydalanuvchi o'chirishda xatolik: {e}{Colors.NC}")
            return False
        finally:
            session.close()
    
    def list_users(self, limit=100):
        """Barcha foydalanuvchilarni ro'yxatlash"""
        session = self.get_session()
        if not session:
            return []
        
        try:
            users = session.query(UserBalance).order_by(UserBalance.id).limit(limit).all()
            return users
        except Exception as e:
            print(f"{Colors.RED}❌ Foydalanuvchilarni olishda xatolik: {e}{Colors.NC}")
            return []
        finally:
            session.close()
    
    # ==================== QO'SHIMCHA FUNKSIYALAR ====================
    
    def get_statistics(self):
        """Statistika olish"""
        session = self.get_session()
        if not session:
            return {}
        
        try:
            total_users = session.query(UserBalance).count()
            total_balance = session.query(func.sum(UserBalance.balans)).scalar() or 0
            max_balance = session.query(func.max(UserBalance.balans)).scalar() or 0
            min_balance = session.query(func.min(UserBalance.balans)).scalar() or 0
            avg_balance = session.query(func.avg(UserBalance.balans)).scalar() or 0
            
            return {
                'total_users': total_users,
                'total_balance': float(total_balance),
                'max_balance': float(max_balance),
                'min_balance': float(min_balance),
                'avg_balance': float(avg_balance)
            }
        except Exception as e:
            print(f"{Colors.RED}❌ Statistika olishda xatolik: {e}{Colors.NC}")
            return {}
        finally:
            session.close()
    
    def get_top_users(self, limit=10):
        """Eng katta balansga ega foydalanuvchilar"""
        session = self.get_session()
        if not session:
            return []
        
        try:
            users = session.query(UserBalance).order_by(UserBalance.balans.desc()).limit(limit).all()
            return users
        except Exception as e:
            print(f"{Colors.RED}❌ Top foydalanuvchilarni olishda xatolik: {e}{Colors.NC}")
            return []
        finally:
            session.close()
    
    def search_users(self, search_term):
        """Foydalanuvchilarni qidirish (chat_id bo'yicha)"""
        session = self.get_session()
        if not session:
            return []
        
        try:
            users = session.query(UserBalance).filter(
                UserBalance.chat_id.like(f'%{search_term}%')
            ).all()
            return users
        except Exception as e:
            print(f"{Colors.RED}❌ Qidiruvda xatolik: {e}{Colors.NC}")
            return []
        finally:
            session.close()
    
    def add_money(self, chat_id, amount):
        """Pul qo'shish (update_balance uchun wrapper)"""
        return self.update_balance(chat_id, amount, 'add')
    
    def subtract_money(self, chat_id, amount):
        """Pul ayirish (update_balance uchun wrapper)"""
        return self.update_balance(chat_id, amount, 'subtract')
    
    def set_money(self, chat_id, amount):
        """Balansni o'rnatish (update_balance uchun wrapper)"""
        return self.update_balance(chat_id, amount, 'set')
    
    def get_balance(self, chat_id):
        """Foydalanuvchi balansini olish"""
        user = self.get_user(chat_id)
        if user:
            return float(user.balans)
        return None
    
    def user_exists(self, chat_id):
        """Foydalanuvchi mavjudligini tekshirish"""
        user = self.get_user(chat_id)
        return user is not None
    
    def create_or_update(self, chat_id, initial_balance=0.00):
        """Foydalanuvchi yaratish yoki mavjud bo'lsa olish"""
        user = self.get_user(chat_id)
        if user:
            return user
        return self.create_user(chat_id, initial_balance)
    
    def transfer_money(self, from_chat_id, to_chat_id, amount):
        """Pul o'tkazish"""
        if amount <= 0:
            print(f"{Colors.YELLOW}⚠️ Miqdor musbat bo'lishi kerak{Colors.NC}")
            return False
        
        session = self.get_session()
        if not session:
            return False
        
        try:
            from_user = session.query(UserBalance).filter_by(chat_id=from_chat_id).first()
            to_user = session.query(UserBalance).filter_by(chat_id=to_chat_id).first()
            
            if not from_user:
                print(f"{Colors.YELLOW}⚠️ Jo'natuvchi topilmadi: {from_chat_id}{Colors.NC}")
                return False
            
            if not to_user:
                print(f"{Colors.YELLOW}⚠️ Qabul qiluvchi topilmadi: {to_chat_id}{Colors.NC}")
                return False
            
            if float(from_user.balans) < amount:
                print(f"{Colors.YELLOW}⚠️ Jo'natuvchida yetarli mablag' yo'q{Colors.NC}")
                return False
            
            from_user.balans = float(from_user.balans) - amount
            to_user.balans = float(to_user.balans) + amount
            
            from_user.updated_at = datetime.datetime.now()
            to_user.updated_at = datetime.datetime.now()
            
            session.commit()
            
            print(f"{Colors.GREEN}✅ {amount:.2f} pul o'tkazildi: {from_chat_id} -> {to_chat_id}{Colors.NC}")
            print(f"   {from_chat_id} yangi balans: {float(from_user.balans):.2f}")
            print(f"   {to_chat_id} yangi balans: {float(to_user.balans):.2f}")
            
            return True
        except Exception as e:
            session.rollback()
            print(f"{Colors.RED}❌ Pul o'tkazishda xatolik: {e}{Colors.NC}")
            return False
        finally:
            session.close()
