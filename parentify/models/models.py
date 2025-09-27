import bcrypt
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum, func, LargeBinary
from sqlalchemy.orm import relationship
from django.contrib.auth.hashers    import *
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from parentify.models import Base, Orm
from parentify.models.models import *


class GenderEnum(PyEnum):
    MALE = "male"
    FEMALE = "female"

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(255), unique=False, nullable=False)
    last_name = Column(String(255), unique=False, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    birth_date = Column(Date, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    childs = relationship("UserChild", uselist=True)
    

    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def zodiac_sign(self) -> Optional[str]:
        if not self.birth_date:
            return None
        day = self.birth_date.day
        month = self.birth_date.month
        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "Овен"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "Телец"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "Близнецы"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "Рак"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "Лев"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "Дева"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "Весы"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "Скорпион"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "Стрелец"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "Козерог"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "Водолей"
        elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
            return "Рыбы"
        else:
            return None
        
    @staticmethod
    def create(
            orm,
            email,
            first_name,
            last_name,
            password,
            is_active=True,
            is_admin=False,
            birth_date=None,
            gender=None):
        user = User()
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = is_active
        user.is_admin = is_admin
        user.birth_date = birth_date
        user.gender = gender
        user.set_password(password)
        orm.add(user)
        orm.commit()
        return user
    def check_password(self, raw_password):
        if not self.password:
            return False
        return check_password(raw_password, self.password)

    def set_password(self, password,salt=None):
        self.password = make_password(password,salt=User.get_salt(self.email if not salt else salt))

    def get_salt(string, rounds:int = 12, prefix: bytes = b"2b") -> bytes:
        #(b'2a'  b'2b')
        if prefix not in (b"2a", b"2b"):
            raise ValueError("Supported prefixes are b'2a' or b'2b'")
        str_res = ''
        for i in range(16):
            if len(str_res)>=16:
                string = str_res[0:16]
                break
            else:
                str_res += string
        salt = bytes(string,'ascii')
        output = bcrypt._bcrypt.encode_base64(salt)
        result = (  
            b"$"
            + prefix
            + b"$"
            + str(rounds).encode("ascii")
            + b"$"
            + output
        )
        return result
    
class UserChild(Base):
    __tablename__ = 'user_child'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parrent_id = Column(Integer, ForeignKey('user.id'))
    first_name = Column(String(255), unique=False, nullable=False)
    last_name = Column(String(255), unique=False, nullable=False)
    is_active = Column(Boolean, default=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=True)
    parrent = relationship("User", back_populates="childs")

    def __str__(self):
        return self.full_name
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"
    
    @property
    def zodiac_sign(self) -> Optional[str]:
        if not self.birth_date:
            return None

        day = self.birth_date.day
        month = self.birth_date.month

        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "Овен"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "Телец"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "Близнецы"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "Рак"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "Лев"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "Дева"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "Весы"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "Скорпион"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "Стрелец"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "Козерог"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "Водолей"
        elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
            return "Рыбы"
        else:
            return None

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    articles = relationship('Article', back_populates='category')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Article(Base):
    __tablename__ = 'article'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    html = Column(Text, nullable=False)
    image = Column(LargeBinary) 
    views_count = Column(Integer, default=0)
    useful_count = Column(Integer, default=0)
    not_useful_count = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship('Category', back_populates='article')
    
    def __repr__(self):
        return f'<Article {self.title}>'
    
    def total_votes(self):
        return self.useful_count + self.not_useful_count
    
    def usefulness_percentage(self):
        if self.total_votes() == 0:
            return 0
        return (self.useful_count / self.total_votes()) * 100
    
    def increment_views(self):
        self.views_count += 1
    
    def vote_useful(self):
        self.useful_count += 1
    
    def vote_not_useful(self):
        self.not_useful_count += 1