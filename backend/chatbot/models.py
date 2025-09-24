from sqlalchemy import Column, Integer, String, ForeignKey, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from passlib.hash import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    conversations = relationship("Conversation", back_populates="user")

    def verify_password(self, password: str) -> bool:
        return bcrypt.verify(password, self.password_hash)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="Nueva conversación")
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False)   # "user" o "assistant"
    content = Column(Text, nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))

    conversation = relationship("Conversation", back_populates="messages")

# Configuración de DB
engine = create_engine("sqlite:///chatbot.db")
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
