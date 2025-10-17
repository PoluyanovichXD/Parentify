import bcrypt
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum, func, LargeBinary, Text
from sqlalchemy.orm import relationship
from django.contrib.auth.hashers import *  # Ошибка: лишние пробелы
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
    url_key_name = 'id'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(255), unique=False, nullable=False)
    last_name = Column(String(255), unique=False, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    birth_date = Column(Date, nullable=True)
    gender = Column(Enum(GenderEnum), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    childs = relationship("UserChild", uselist=True, back_populates="parent")
    site_events = relationship("SiteEvent", back_populates="user", cascade="all, delete-orphan")
    

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

    def set_password(self, password, salt=None):
        self.password = make_password(password, salt=User.get_salt(self.email if not salt else salt))

    @staticmethod  # Ошибка: добавлен декоратор staticmethod
    def get_salt(string, rounds: int = 12, prefix: bytes = b"2b") -> bytes:
        if prefix not in (b"2a", b"2b"):
            raise ValueError("Supported prefixes are b'2a' or b'2b'")
        str_res = ''
        for i in range(16):
            if len(str_res) >= 16:
                string = str_res[0:16]
                break
            else:
                str_res += string
        salt = bytes(string, 'ascii')
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
    url_key_name = 'id'

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey('user.id'))  # Ошибка: исправлено parrent_id -> parent_id
    first_name = Column(String(255), unique=False, nullable=False)
    last_name = Column(String(255), unique=False, nullable=False)
    is_active = Column(Boolean, default=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parent = relationship("User", back_populates="childs")  # Ошибка: исправлено parrent -> parent

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


class ArticleCategory(Base):
    __tablename__ = 'article_category'
    url_key_name = 'id'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Ошибка: добавлен autoincrement
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    articles = relationship('Article', back_populates='category')
    
    def __repr__(self):
        return f'<ArticleCategory {self.name}>'
    
    def __str__(self):
        return self.name


class Article(Base):
    __tablename__ = 'article'
    url_key_name = 'id'
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # Ошибка: добавлен autoincrement
    title = Column(String(200), nullable=False)
    html = Column(Text, nullable=False)
    image = Column(LargeBinary) 
    views_count = Column(Integer, default=0)
    useful_count = Column(Integer, default=0)
    not_useful_count = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey('article_category.id'), nullable=False)  # Ошибка: исправлено 'category.id' -> 'article_category.id'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship('ArticleCategory', back_populates='articles')
    
    def __repr__(self):
        return f'<Article {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'html': self.html,
            'image': self.image_url,
            'views_count': self.views_count,
            'useful_count': self.useful_count,
            'not_useful_count': self.not_useful_count,
            'category_id': self.category_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
    @property
    def image_url(self):
        return f'/article/preview/image_{self.id}.png'  # Ошибка: убрана лишняя запятая
    
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


class ForumTopic(Base):
    __tablename__ = 'forum_topic'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False) 
    author_name = Column(String(100), nullable=False)  # Ошибка: добавлено отсутствующее поле
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    category = Column(String(50), default='general')
    tags = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    comments = relationship("ForumComment", back_populates="topic", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ForumTopic(id={self.id}, title='{self.title}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'author_name': self.author_name,  # Ошибка: добавлено отсутствующее поле
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'is_pinned': self.is_pinned,
            'is_closed': self.is_closed,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ForumComment(Base):
    __tablename__ = 'forum_comment'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False)
    author_name = Column(String(100), nullable=False)
    topic_id = Column(Integer, ForeignKey('forum_topic.id'), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('forum_comment.id'))
    like_count = Column(Integer, default=0)  # Ошибка: добавлено отсутствующее поле
    is_edited = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    topic = relationship("ForumTopic", back_populates="comments")
    parent = relationship("ForumComment", remote_side=[id], back_populates="replies")
    replies = relationship("ForumComment", back_populates="parent", cascade="all, delete-orphan")
    likes = relationship("ForumLikedComment", back_populates="comment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ForumComment(id={self.id}, topic_id={self.topic_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'author_id': self.author_id,
            'author_name': self.author_name,
            'topic_id': self.topic_id,
            'parent_comment_id': self.parent_comment_id,
            'like_count': self.like_count,
            'is_edited': self.is_edited,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'replies_count': len(self.replies) if self.replies else 0
        }


class ForumLikedComment(Base):
    __tablename__ = 'forum_liked_comment'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    comment_id = Column(Integer, ForeignKey('forum_comment.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    comment = relationship("ForumComment", back_populates="likes")
    
    def __repr__(self):
        return f"<ForumLikedComment(user_id={self.user_id}, comment_id={self.comment_id})>"


class Notification(Base):
    """Модель уведомлений для пользователей"""
    __tablename__ = 'notification'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False, default='info')  # Ошибка: дублирование поля type
    title = Column(String(200), nullable=False)
    html = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)  # Ошибка: исправлено 'users.id' -> 'user.id'
    
    user = relationship("User", foreign_keys=[user_id])
    read_records = relationship("NotificationRead", back_populates="notification", cascade="all, delete-orphan")  # Ошибка: добавлена связь
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', user_id={self.user_id})>"


class NotificationRead(Base):
    """Модель прочитанных уведомлений"""
    __tablename__ = 'notification_read'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    notification_id = Column(Integer, ForeignKey('notification.id'), nullable=False, index=True)  # Ошибка: исправлено 'notifications.id' -> 'notification.id'
    user_id = Column(Integer, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    notification = relationship("Notification", back_populates="read_records")
    
    def __repr__(self):
        return f"<NotificationRead(user_id={self.user_id}, notification_id={self.notification_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'read_at': self.created_at.isoformat()
        }


class SiteEvent(Base):
    __tablename__ = "site_event"
    url_key_name = "id"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Ошибка: добавлен autoincrement
    created_at = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)  # Ошибка: исправлено text вместо event
    type = Column(String(255))

    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    user = relationship("User", back_populates="site_events")  # Ошибка: исправлено "WorkerBase" -> "User"

    def __init__(self, text, type, user=None, created_at=None):  # Ошибка: исправлено event -> text
        self.text = text
        self.type = type
        if user:
            self.user = user
        if created_at:
            self.created_at = created_at

    def __str__(self):
        return self.text  # Ошибка: исправлено self.event -> self.text

    @property
    def s_time(self):
        return self.created_at.strftime('%d.%m.%Y %H:%M') if self.created_at else ''  # Ошибка: исправлено self.time -> self.created_at


    