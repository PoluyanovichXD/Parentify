import bcrypt
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Enum, LargeBinary, Text, Float, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.orm.session         import object_session
from django.contrib.auth.hashers import make_password, check_password
from datetime import datetime
from django.utils import timezone
from enum import Enum as PyEnum
from typing import Optional
from parentify.models import Base, Orm
from parentify.models.event_types import EventTypes


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    avatar = Column(LargeBinary, nullable=True) 
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    birth_date = Column(Date, nullable=True)
    gender = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    children = relationship("UserChild", back_populates="user", cascade="all, delete-orphan")
    site_events = relationship("SiteEvent", back_populates="user", cascade="all, delete-orphan")
    forum_topics = relationship('ForumTopic', back_populates='user')
    forum_comments = relationship('ForumComment', back_populates='user')
    forum_liked_comments = relationship('ForumLikedComment', back_populates='user')
    notifications = relationship('Notification', back_populates='user')
    notification_reads = relationship('NotificationRead', back_populates='user')
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="user", cascade="all, delete-orphan")


    def __str__(self):
        return self.full_name
    
    def to_dict(self):
        return {
            "id":self.id,
            "email":self.email,
            "first_name":self.first_name,
            "last_name":self.last_name,
            "password":self.password,
            "is_active":self.is_active,
            "is_admin":self.is_admin,
            "birth_date":self.birth_date,
            "gender":self.gender,
            "avatar":self.avatar_url,
            "created_at":self.created_at,
            "updated_at":self.updated_at
        }

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def weeks_in_system(self):
        if not self.created_at:
            return 0
        
        now = timezone.now()
        
        if timezone.is_naive(self.created_at):
            created_at = timezone.make_aware(self.created_at)
        else:
            created_at = self.created_at
        
        if now < created_at:
            return 0
        
        delta = now - created_at
        days = delta.days
        
        weeks = days // 7
        return max(weeks, 0)
    
    @property
    def birth_year(self):
        current_year = datetime.now().year
        return current_year - self.birth_date.year
    @property
    def avatar_url(self):
        if self.avatar:
            return f'/users/{self.id}/avatar.png'
        return None
    
    @property
    def gender_name(self):
        if self.gender == 'MALE':
            return 'Мальчик'
        elif self.gender == 'FEMALE':
            return 'Девочка'
        else:
            return 'Другое'
    
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
    def create(orm, email, first_name, last_name, password, is_active=True, 
               is_admin=False, birth_date=None, gender=None, avatar=None):
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_admin=is_admin,
            birth_date=birth_date,
            gender=gender,
            avatar=avatar
        )
        user.set_password(password)
        orm.add(user)
        orm.commit()
        return user
    @staticmethod
    def create_password(password, salt):
        return make_password(password, salt=User.get_salt(salt))
    
    def check_password(self, raw_password):
        if not self.password:
            return False
        return check_password(raw_password, self.password)

    def set_password(self, password, salt=None):
        self.password = make_password(password, salt=User.get_salt(self.email if not salt else salt))
    

    @staticmethod
    def get_salt(string, rounds: int = 12, prefix: bytes = b"2b") -> bytes:
        if prefix not in (b"2a", b"2b"):
            raise ValueError("Supported prefixes are b'2a' or b'2b'")
        
        # Создаем соль фиксированной длины
        str_res = ''
        for i in range(16):
            if len(str_res) >= 16:
                salt_str = str_res[0:16]
                break
            else:
                str_res += string
        else:
            salt_str = str_res.ljust(16, '0')  # Дополняем до 16 символов
        
        salt = salt_str.encode('ascii')
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
    
    def has_favorite_goods(self, orm, goods_id):
        """Проверить, есть ли товар в избранном у пользователя"""
        if not self.id or not goods_id:
            return False
        
        favorite = orm.query(UserFavorite).filter(
            UserFavorite.user_id == self.id,
            UserFavorite.goods_id == goods_id
        ).first()
        
        return favorite is not None
    
    def add_to_favorites(self, orm, goods_id):
        """
        Добавить товар в избранное пользователя
        Возвращает созданный объект UserFavorite или существующий
        """
        if not self.id or not goods_id:
            raise ValueError("User ID and Goods ID are required")
        
        # Проверяем, не добавлен ли уже товар в избранное
        existing_favorite = orm.query(UserFavorite).filter(
            UserFavorite.user_id == self.id,
            UserFavorite.goods_id == goods_id
        ).first()
        
        if existing_favorite:
            return existing_favorite  # Уже в избранном
        
        # Проверяем существование товара
        goods = orm.query(Goods).get(goods_id)
        if not goods:
            raise ValueError(f"Goods with ID {goods_id} not found")
        
        # Создаем новую запись
        favorite = UserFavorite(
            user_id=self.id,
            goods_id=goods_id
        )
        orm.add(favorite)
        orm.commit()
        
        return favorite

    def remove_from_favorites(self, orm, goods_id):
        """
        Удалить товар из избранного пользователя
        Возвращает True если удалено, False если не было в избранном
        """
        if not self.id or not goods_id:
            return False
        
        favorite = orm.query(UserFavorite).filter(
            UserFavorite.user_id == self.id,
            UserFavorite.goods_id == goods_id
        ).first()
        
        if favorite:
            orm.delete(favorite)
            orm.commit()
            return True
        
        return False

    def has_favorite_goods(self, orm, goods_id):
        """
        Проверить, есть ли товар в избранном у пользователя
        """
        if not self.id or not goods_id:
            return False
        
        favorite = orm.query(UserFavorite).filter(
            UserFavorite.user_id == self.id,
            UserFavorite.goods_id == goods_id
        ).first()
        
        return favorite is not None

    def get_favorites(self, orm, limit=None, offset=None):
        """
        Получить избранные товары пользователя
        """
        query = orm.query(UserFavorite).filter(
            UserFavorite.user_id == self.id
        ).order_by(UserFavorite.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
            
        return query.all()

    def get_favorites_count(self, orm):
        """
        Получить количество избранных товаров пользователя
        """
        return orm.query(UserFavorite).filter(
            UserFavorite.user_id == self.id
        ).count()

    def clear_favorites(self, orm):
        """
        Очистить все избранные товары пользователя
        """
        favorites = orm.query(UserFavorite).filter(
            UserFavorite.user_id == self.id
        ).all()
        
        for favorite in favorites:
            orm.delete(favorite)
        
        orm.commit()
        return len(favorites)


class UserChild(Base):
    __tablename__ = 'user_child'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="children")
    treckers = relationship("Trecker", back_populates="children")

    def __str__(self):
        return self.full_name
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_active": self.is_active,
            "birth_date": self.birth_date,
            "gender": self.gender,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def gender_name(self):
        if self.gender == 'MALE':
            return 'Мальчик'
        elif self.gender == 'FEMALE':
            return 'Девочка'
        else:
            return 'Другое'
    
    @property
    def birth_year(self):
        current_year = datetime.now().year
        return current_year - self.birth_date.year
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
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    articles = relationship('Article', back_populates='category')
    
    def __repr__(self):
        return f'<ArticleCategory {self.name}>'
    
    def __str__(self):
        return self.name


class Article(Base):
    __tablename__ = 'article'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    html = Column(Text, nullable=False)
    image = Column(LargeBinary) 
    views_count = Column(Integer, default=0)
    useful_count = Column(Integer, default=0)
    not_useful_count = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey('article_category.id'), nullable=False)
    
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
            'image_url': self.image_url,
            'views_count': self.views_count,
            'useful_count': self.useful_count,
            'not_useful_count': self.not_useful_count,
            'category_id': self.category_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @property
    def image_url(self):
        return f'/article/preview/image_{self.id}.png'
    
    def total_votes(self):
        return self.useful_count + self.not_useful_count
    
    def usefulness_percentage(self):
        total = self.total_votes()
        if total == 0:
            return 0
        return (self.useful_count / total) * 100
    
    def increment_views(self):
        self.views_count += 1
    
    def vote_useful(self):
        self.useful_count += 1
    
    def vote_not_useful(self):
        self.not_useful_count += 1


class ForumTopic(Base):
    __tablename__ = 'forum_topic'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey('forum_topic_category.id'), nullable=False)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    is_closed = Column(Boolean, default=False)
    category = Column(String(50), default='general')
    tags = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', back_populates='forum_topics')
    comments = relationship("ForumComment", back_populates="topic", cascade="all, delete-orphan")
    category = relationship('ForumTopicCategory', back_populates='forums')
    
    def __repr__(self):
        return f"<ForumTopic(id={self.id}, title='{self.title}')>"

    def to_dict(self):
        return {
            'id': self.id,
            "category_id": self.category_id,
            'title': self.title,
            'content': self.content,
            'user_id': self.user_id,
            'is_closed': self.is_closed,
            'category': self.category,
            'tags': self.tags.split(',') if self.tags else [],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ForumTopicCategory(Base):
    __tablename__ = 'forum_topic_category'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    forums = relationship('ForumTopic', back_populates='category')
    
    def __repr__(self):
        return f'<ForumTopicCategory {self.name}>'
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at
        }


class ForumComment(Base):
    __tablename__ = 'forum_comment'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    topic_id = Column(Integer, ForeignKey('forum_topic.id'), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey('forum_comment.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', back_populates='forum_comments')
    topic = relationship("ForumTopic", back_populates="comments")
    parent = relationship("ForumComment", remote_side=[id], back_populates="replies")
    replies = relationship("ForumComment", back_populates="parent", cascade="all, delete-orphan")
    likes = relationship("ForumLikedComment", back_populates="comment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ForumComment(id={self.id}, topic_id={self.topic_id})>"
    
    @property
    def like_count(self):
        return len(self.likes) if self.likes else 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'user_id': self.user_id,
            'topic_id': self.topic_id,
            'parent_comment_id': self.parent_comment_id,
            'like_count': self.like_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'replies_count': len(self.replies) if self.replies else 0
        }


class ForumLikedComment(Base):
    __tablename__ = 'forum_liked_comment'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    comment_id = Column(Integer, ForeignKey('forum_comment.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    comment = relationship("ForumComment", back_populates="likes")
    user = relationship('User', back_populates='forum_liked_comments')
    
    def __repr__(self):
        return f"<ForumLikedComment(user_id={self.user_id}, comment_id={self.comment_id})>"


class Notification(Base):
    """Модель уведомлений для пользователей"""
    __tablename__ = 'notification'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(50), nullable=False, default='info')
    title = Column(String(200), nullable=False)
    html = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    user = relationship("User", back_populates="notifications")
    read_records = relationship("NotificationRead", back_populates="notification", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type}', user_id={self.user_id})>"


class NotificationRead(Base):
    """Модель прочитанных уведомлений"""
    __tablename__ = 'notification_read'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    notification_id = Column(Integer, ForeignKey('notification.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    notification = relationship("Notification", back_populates="read_records")
    user = relationship("User", back_populates="notification_reads")
    
    def __repr__(self):
        return f"<NotificationRead(user_id={self.user_id}, notification_id={self.notification_id})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'notification_id': self.notification_id,
            'user_id': self.user_id,
            'read_at': self.created_at.isoformat() if self.created_at else None
        }
    

class Place(Base):
    __tablename__ = "place"

    id = Column(Integer, primary_key=True, autoincrement=True)

    category_id = Column(Integer, ForeignKey('place_category.id'), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    image = Column(LargeBinary, nullable=True)

    rating = Column(Float, nullable=True)

    tags = Column(ARRAY(String), nullable=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    address = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)

    schedule = Column(String(255), nullable=True)

    category = relationship('PlaceCategory', back_populates='places')

    def __repr__(self):
        return f"<Place(id={self.id}, title='{self.title}')>"
    
    @property
    def image_url(self):
        return f'/map/{self.id}/image.png'
    
    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "title": self.title,
            "description": self.description,
            "image": self.image_url,
            "rating": self.rating,
            "tags": self.tags,
            "tags_str": ','.join(self.tags),
            "address": self.address,
            "phone": self.phone,
            "website": self.website,
            "schedule": self.schedule,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "coords": f"{self.latitude},{self.longitude}"
        }
    
class PlaceCategory(Base):
    __tablename__ = 'place_category'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    places = relationship('Place', back_populates='category')
    
    def __repr__(self):
        return f'<PlaceCategory {self.name}>'
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at
        }

class GoodsCategory(Base):
    __tablename__ = 'goods_category'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    goods = relationship("Goods", back_populates="category")
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Goods(Base):
    __tablename__ = 'goods'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    image = Column(LargeBinary, nullable=True)  # для хранения изображения
    category_id = Column(Integer, ForeignKey('goods_category.id'), nullable=False)
    description = Column(Text, nullable=True)
    best_place_to_buy = Column(String(500), nullable=True)  # лучшее место покупки
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("GoodsCategory", back_populates="goods")
    favorites = relationship("UserFavorite", back_populates="goods", cascade="all, delete-orphan")

    
    def __str__(self):
        return self.title
    
    def image_url(self):
        return f'/goods/preview/image_{self.id}.png'

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category_id': self.category_id,
            'description': self.description,
            'best_place_to_buy': self.best_place_to_buy,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'category': self.category.to_dict() if self.category else None
        }
    
    def is_favorite(self, user_id):
        """Проверяет, находится ли товар в избранном у пользователя"""
        if not user_id:
            return False
        orm = object_session(self)
        favorite = orm.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.goods_id == self.id
        ).first()
        
        return favorite is not None
    
class UserFavorite(Base):
    __tablename__ = 'user_favorite'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    goods_id = Column(Integer, ForeignKey('goods.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    goods = relationship("Goods", back_populates="favorites")
    
    def __str__(self):
        return f"Favorite: User {self.user_id} - Goods {self.goods_id}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "goods_id": self.goods_id,
            "created_at": self.created_at,
            "goods": self.goods.to_dict() if self.goods else None,
            "user": {
                "id": self.user.id,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name
            } if self.user else None
        }
    
    @staticmethod
    def add_to_favorites(orm, user_id, goods_id):
        """Добавить товар в избранное"""
        # Проверяем, не добавлен ли уже товар в избранное
        existing_favorite = orm.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.goods_id == goods_id
        ).first()
        
        if existing_favorite:
            return existing_favorite  # Уже в избранном
        
        favorite = UserFavorite(
            user_id=user_id,
            goods_id=goods_id
        )
        orm.add(favorite)
        orm.commit()
        return favorite
    
    @staticmethod
    def remove_from_favorites(orm, user_id, goods_id):
        """Удалить товар из избранного"""
        favorite = orm.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.goods_id == goods_id
        ).first()
        
        if favorite:
            orm.delete(favorite)
            orm.commit()
            return True
        return False
    
    @staticmethod
    def is_favorite(orm, user_id, goods_id):
        """Проверить, находится ли товар в избранном у пользователя"""
        favorite = orm.query(UserFavorite).filter(
            UserFavorite.user_id == user_id,
            UserFavorite.goods_id == goods_id
        ).first()
        return favorite is not None
    
    @staticmethod
    def get_user_favorites(orm, user_id, limit=None, offset=None):
        """Получить избранные товары пользователя"""
        query = orm.query(UserFavorite).filter(
            UserFavorite.user_id == user_id
        ).order_by(UserFavorite.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
            
        return query.all()
    
    @staticmethod
    def get_favorite_count(orm, user_id):
        """Получить количество избранных товаров пользователя"""
        return orm.query(UserFavorite).filter(
            UserFavorite.user_id == user_id
        ).count()

class ChildDevelopmentWeek(Base):
    __tablename__ = 'child_development_week'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    week_number = Column(Integer, nullable=False, unique=True)  # номер недели
    title = Column(String(255), nullable=False)  # заголовок
    description = Column(Text, nullable=True)  # текст
    parent_tips = Column(ARRAY(Text), nullable=True)  # советы родителям
    key_skills = Column(ARRAY(Text), nullable=True)  # ключевые навыки
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __str__(self):
        return f"Week {self.week_number}: {self.title}"
    
    @property
    def s_time(self):
        return self.created_at.strftime('%d.%m.%Y %H:%M') if self.created_at else ''

    def to_dict(self):
        return {
            "id": self.id,
            "week_number": self.week_number,
            "title": self.title,
            "description": self.description,
            "parent_tips": self.parent_tips or [],
            "key_skills": self.key_skills or [],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }










class SiteEvent(Base):
    __tablename__ = "site_event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)
    type = Column(String(255))
    user_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    
    user = relationship("User", back_populates="site_events")
    Types = EventTypes

    def __str__(self):
        return self.text

    @property
    def s_time(self):
        return self.created_at.strftime('%d.%m.%Y %H:%M') if self.created_at else ''
    
    @staticmethod
    def create(orm, type_event, user_event_id=None):
        evnt = SiteEvent(**{
            "type": type_event.name if getattr(type_event,'name') else (type_event.get('name') if type_event and type_event.get('name') else type_event),
            "text": type_event.value if getattr(type_event,'value') else (type_event.get('value') if type_event and type_event.get('value') else type_event),
            "user_id": user_event_id.id if isinstance(user_event_id, User) else user_event_id
        })
        orm.add(evnt)
        orm.commit()
        return evnt

    
class Trecker(Base):
    __tablename__ = 'trecker'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_trecker = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    value = Column(Float, nullable=False)
    comment = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey('trecker_category.id'), nullable=False)
    children_id = Column(Integer, ForeignKey('user_child.id'), nullable=False)
    category = relationship("TreckerCategory", back_populates="treckers")
    children = relationship("UserChild", back_populates="treckers")

    def to_dict(self):
        return {
            "id": self.id,
            "date_trecker": self.date_trecker,
            "created_at": self.created_at,
            "value": self.value,
            "comment": self.comment,
            "category_id": self.category_id,
            "children_id": self.children_id
        }
    
class TreckerCategory(Base):
    __tablename__ = 'trecker_category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    unit = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    treckers = relationship("Trecker", back_populates="category")
    
    
    def __str__(self):
        return self.name
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'unit': self.unit,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
class Reminder(Base):
    __tablename__ = 'reminder'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(Text, nullable=False)
    scheduled_datetime = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='reminders')
    
    @property
    def time_until_now(self):
        """
        Возвращает разницу времени до запланированной даты.
        Возвращает объект с днями, часами и минутами.
        """
        from datetime import datetime
        
        now = datetime.now()
        scheduled = self.scheduled_datetime
        
        if scheduled < now:
            # Если время уже прошло
            delta = now - scheduled
            return {
                'days': delta.days,
                'hours': delta.seconds // 3600,
                'minutes': (delta.seconds % 3600) // 60,
                'seconds': delta.seconds % 60,
                'total_seconds': delta.total_seconds(),
                'is_past': True
            }
        else:
            # Если время еще не наступило
            delta = scheduled - now
            return {
                'days': delta.days,
                'hours': delta.seconds // 3600,
                'minutes': (delta.seconds % 3600) // 60,
                'seconds': delta.seconds % 60,
                'total_seconds': delta.total_seconds(),
                'is_past': False
            }
    
    @property
    def time_until_now_display(self):
        """
        Возвращает отформатированную строку времени.
        """
        time_data = self.time_until_now
        
        if time_data['is_past']:
            # Время уже прошло
            if time_data['days'] > 0:
                return f"{time_data['days']} дн., {time_data['hours']} ч. назад"
            elif time_data['hours'] > 0:
                return f"{time_data['hours']} ч., {time_data['minutes']} мин. назад"
            elif time_data['minutes'] > 0:
                return f"{time_data['minutes']} мин. назад"
            else:
                return "только что"
        else:
            # Время еще не наступило
            if time_data['days'] > 0:
                return f"{time_data['days']} дн., {time_data['hours']} ч."
            elif time_data['hours'] > 0:
                return f"{time_data['hours']} ч., {time_data['minutes']} мин."
            elif time_data['minutes'] > 0:
                return f"{time_data['minutes']} мин."
            else:
                return "менее минуты"
    
    @property
    def time_status_color(self):
        """
        Возвращает цвет статуса в зависимости от времени.
        """
        time_data = self.time_until_now
        
        if time_data['is_past']:
            return "green"  # Уже отправлено (прошло)
        else:
            # Время еще не наступило
            total_seconds = time_data['total_seconds']
            if total_seconds < 3600:  # Менее часа
                return "red"
            elif total_seconds < 86400:  # Менее суток
                return "yellow"
            else:  # Более суток
                return "green"
    
    @property
    def time_status_class(self):
        """
        Возвращает CSS класс для цвета статуса.
        """
        color = self.time_status_color
        if color == "red":
            return "text-red-600"
        elif color == "yellow":
            return "text-yellow-600"
        else:
            return "text-green-600"
    
    @property
    def is_overdue(self):
        """
        Проверяет, просрочено ли напоминание.
        """
        time_data = self.time_until_now
        return time_data['is_past'] and not self.is_sent
    
    @property
    def time_until_now_simple(self):
        """
        Возвращает простое представление времени.
        Для использования в шаблонах.
        """
        time_data = self.time_until_now
        
        if time_data['is_past']:
            if time_data['days'] > 0:
                return f"{time_data['days']} дн. назад"
            elif time_data['hours'] > 0:
                return f"{time_data['hours']} ч. назад"
            elif time_data['minutes'] > 0:
                return f"{time_data['minutes']} мин. назад"
            else:
                return "только что"
        else:
            if time_data['days'] > 0:
                return f"через {time_data['days']} дн."
            elif time_data['hours'] > 0:
                return f"через {time_data['hours']} ч."
            elif time_data['minutes'] > 0:
                return f"через {time_data['minutes']} мин."
            else:
                return "скоро"
    
    def __repr__(self):
        return f"<Reminder(id={self.id}, message='{self.message[:20]}...', scheduled={self.scheduled_datetime})>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "scheduled_datetime": self.scheduled_datetime,
            "is_sent": self.is_sent,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "time_until_now": self.time_until_now,
            "time_until_now_display": self.time_until_now_display,
            "time_status_color": self.time_status_color,
            "is_overdue": self.is_overdue,
            "time_until_now_simple": self.time_until_now_simple,
        }