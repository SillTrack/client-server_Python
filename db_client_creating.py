import os
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, String, DateTime, JSON
from sqlalchemy import select, exists

from datetime import datetime

Base = declarative_base()


class ContactList(Base):
    __tablename__ = "Contact_list"

    contact_id = Column(Integer, primary_key=True, autoincrement=True)
    contact_name = Column(Text, nullable=False)

    def __init__(self, contact_name):
        self.contact_name = contact_name


class MessageHistory(Base):
    __tablename__ = "Message_history"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    receiver = Column(Text, nullable=False)
    time_send = Column(DateTime, nullable=False)
    message_text = Column(Text, nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'message_id': self.message_id,
            'reciever': self.receiver,
            'time_send': self.timestamp.strftime("%d-%m-%Y %H:%M:%S"),
            'message_text': message.text
        }

    def __init__(self, receiver, message_text):
        now = datetime.now()
        self.time_send = now
        self.receiver = receiver
        self.message_text = message_text


class ClientDataBase():

    def __init__(self, engine, base) -> None:
        self.engine = engine
        self.base = base
        self.create_db()

    def create_db(self):
        if os.path.isfile("client_tables.db"):
            return "Client Database already exists"
        else:
            with Session(bind=self.engine) as session:
                self.base.metadata.create_all(self.engine)
            return "Client Database created"


if __name__ == "__main__":

    db_engine = create_engine("sqlite:///client_tables.db", echo=True)
    db_prototype = ClientDataBase(engine=db_engine, base=Base)
    print(db_prototype.create_db())
    with Session(db_engine) as session:
        contact = ContactList(contact_name="admin")
        message = MessageHistory(receiver="admin", message_text="hello world!")
        session.add(contact)
        session.add(message)
        session.commit()
        session.close()
