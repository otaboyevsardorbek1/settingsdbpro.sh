# postgresql_model.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Numeric, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import datetime

# PostgreSQL uchun base class
Base = declarative_base()

class UserBalance(Base):
    """
    Foydalanuvchi balans modeli - PostgreSQL versiyasi
    """
    __tablename__ = 'user_balances'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, unique=True)  # Telegram ID lar katta bo'lishi mumkin
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


# PostgreSQL Database boshqaruvchi klass
class PostgreSQLDatabase:
    def __init__(self, host='localhost', port=5432, user='postgres', password='', database='test_db'):
        self.connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.engine = None
        self.Session = None
        
    def connect(self):
        """PostgreSQL ga ulanish"""
        try:
            self.engine = create_engine(self.connection_string, echo=True)
            self.Session = sessionmaker(bind=self.engine)
            # Jadvallarni yaratish
            Base.metadata.create_all(self.engine)
            print(f"{Colors.GREEN}✅ PostgreSQL ga muvaffaqiyatli ulandi{Colors.NC}")
            return True
        except Exception as e:
            print(f"{Colors.RED}❌ PostgreSQL ulanish xatosi: {e}{Colors.NC}")
            return False
    
    def get_session(self):
        """Yangi session olish"""
        if self.Session:
            return self.Session()
        return None
    
    # CRUD operatsiyalari
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
            print(f"{Colors.GREEN}✅ Foydalanuvchi yaratildi: {user}{Colors.NC}")
            return user
        except Exception as e:
            session.rollback()
            print(f"{Colors.RED}❌ Foydalanuvchi yaratishda xatolik: {e}{Colors.NC}")
            return None
        finally:
            session.close()
    
    def get_user(self, chat_id):
        """Foydalanuvchini olish"""
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
            elif operation == 'subtract':
                new_balance = float(user.balans) - amount
                if new_balance < 0:
                    print(f"{Colors.YELLOW}⚠️ Balans manfiy bo'lishi mumkin emas{Colors.NC}")
                    return None
                user.balans = new_balance
            elif operation == 'set':
                if amount < 0:
                    print(f"{Colors.YELLOW}⚠️ Balans manfiy bo'lishi mumkin emas{Colors.NC}")
                    return None
                user.balans = amount
            
            user.updated_at = datetime.datetime.now()
            session.commit()
            
            print(f"{Colors.GREEN}✅ Balans yangilandi: {old_balance:.2f} -> {float(user.balans):.2f}{Colors.NC}")
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
