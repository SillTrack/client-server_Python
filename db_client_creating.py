import os
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import MetaData
from sqlalchemy.orm import mapper
from sqlalchemy.orm import declarative_base, subqueryload
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, Text, String, DateTime, JSON
from sqlalchemy import select, exists

Base = declarative_base()


class ContactList(Base):
    __tablename__ = "Contact_list"

    list_id = Column(Integer, primary_key=True, autoincrement=True)
    contact_id_list = Column(Text, nullable=False)

    def __init__(self, contact_id_list):
        self.contact_id_list = contact_id_list


class MessageHistory(Base):
    __tablename__ = "Message_history"

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    receiver = Column(Text, nullable=False)
    time_send = Column(DateTime, nullable=False)
    message_text = Column(Text, nullable=False)

    def __init__(self):
        pass


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
    with Session(db_engine) as session:
        session.commit()
        session.close()
