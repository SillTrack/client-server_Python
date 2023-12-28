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


class Client(Base):
    __tablename__ = "Client"

    client_id = Column(Integer, primary_key=True, autoincrement=True, )
    # после окончания дебага - поставить в login - unique = true
    login = Column(String)
    info = Column(Text)

    def __init__(self, login: str, info: str):
        self.login = login
        self.info = info

    def __repr__(self):
        return (self.client_id)

    def __call__(self,):
        return 0


class Client_history(Base):
    __tablename__ = "Client_history"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("Client.client_id"))
    ip_address = Column(String)
    time = Column(DateTime)

    # def __init__(self, ip_address, time, client):
    #     self.clinet_id = client
    #     self.ip_address = ip_address
    #     self.time = time


class Contact_list(Base):
    __tablename__ = "Contact_list"

    list_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("Client.client_id"))
    contact_id_list = Column(Text, nullable=False)

    def __init__(self, owner_id, contact_id_list):
        self.owner_id = owner_id
        self.contact_id_list = contact_id_list


class Server_DataBase():

    def __init__(self, engine, base) -> None:
        self.engine = engine
        self.base = base
        self.create_db()

    def create_db(self):
        if os.path.isfile("server_tables.db"):
            return "Database already exists"
        else:
            with Session(bind=self.engine) as session:
                self.base.metadata.create_all(self.engine)
            return "Database created"

# добавить в качестве аргумента ip, но как его получать на сервер пока не понятно
    def add_user(self, user_name: str, information: str):
        with Session(self.engine) as session:
            user_exists = session.query(Client).where(
                Client.login == user_name).first() is not None

            if user_exists:
                print(f'{user_name} уже есть')
            else:
                print(f'создаю пользователя {user_name}')
                client = Client(login=user_name, info=information)
                session.add(client)
                session.commit()

                client = session.query(Client).where(
                    Client.login == user_name).first()

                client_history = Client_history(
                    time=datetime.now(), ip_address='', client_id=client.client_id)

                session.add(client_history)
                session.commit()

# delete_contact and add_contact are working!!!!!!
# DO NOT CHANGE                             !!!!!!
    def add_contact(self, list_owner_name: str, contact_name: str):
        with Session(self.engine) as session:
            owner = session.query(Client).where(
                Client.login == list_owner_name).first()

            if owner is not None:
                print(f'{list_owner_name} - такой пользователь существует')
            else:
                print(f'{list_owner_name} - такого пользователя нет')
            # сообщение что такого клиента нет

            contact = session.query(Client).where(
                Client.login == contact_name).first()

            if contact is not None:
                print(f'{contact_name} - такой пользователь существует')
            else:
                print(f'{contact_name} - такого пользователя нет')
            # сообщение что такого клиента нет

        # проверить что есть запись с контактами
        record_exists = session.query(Contact_list).where(
            Contact_list.owner_id == owner.client_id).one_or_none()
        # если есть запись - проверить нет ли такого контакта уже в списке
        if record_exists:
            record = session.query(Contact_list).filter(
                Contact_list.owner_id == owner.client_id).first()

            if str(contact.client_id) in record.contact_id_list:
                print('у вас уже есть такой контакт')
            else:
                # изменить на вытягивание из таблицы записи
                # добавление к списку контактов нового id
                # сохранение измененного списка контактов
                record.contact_id_list += f", {contact.client_id}"
                session.add(record)
                session.commit()
        # если нет - создать запись и добавить первый контак в контакт лист
        else:
            record = Contact_list(owner_id=owner.client_id, contact_id_list="")
            record.contact_id_list = str(contact.client_id)
            session.add(record)
            session.commit()

    def delete_contact(self, list_owner: str, contact_name: str):
        with Session(self.engine) as session:
            owner = session.query(Client).where(
                Client.login == list_owner).first()

            if owner is not None:
                print(f'{list_owner} - такой пользователь существует')
            else:
                return 0
            # сообщение что такого клиента нет

            contact = session.query(Client).where(
                Client.login == contact_name).first()

            if contact is not None:
                print(f'{contact_name} - такой пользователь существует')
            else:
                return 0
            # сообщение что такого клиента нет

            # TODO изменить поведение функции с учетом что список контактов - через запятую в 1 поле
            # пример:
            # owner_id: 1, 2,3,4,5,18.
            # разбить контакты по разделителю ", " в список
            # удалить нужный контакт
            # собрать в строку обратно с разделителем ", "
            record = session.query(Contact_list).where(
                Contact_list.owner_id == owner.client_id).first()
            contact_list = record.contact_id_list.split(', ')
            # сделать проверку на наличие в таблице, если есть - удалить
            # иначе - сообщение что нет
        if str(contact_2.client_id) in contact_list:
            contact_list.remove(str(contact_2.client_id))
            if len(contact_list) == 0:
                session.delete(record)
                session.commit()
            else:
                record.contact_id_list = ', '.join(contact_list)
                session.add(record)
                session.commit()
        else:
            print('такого контакта нет в ващем списке')

        session.close()

# работает
    def show_contacts(self, list_owner: str) -> list:
        with Session(self.engine) as session:
            login_list = []
            record = session.query(Contact_list).where(
                Contact_list.owner_id == owner.client_id).first()
            contact_list = record.contact_id_list.split(', ')
            for contact_id in contact_list:
                login_list.append(session.query(Client).where(
                    Client.client_id == contact_id).first().login)
            session.close()
        return login_list
        # проверить есть ли запись о контактах у пользователя,если
        # есть - вернуть список контактов, иначе написать об этом
        # список контактов как выборка склеив имена по id из таблицы

    def show_clients(self) -> str:
        login_list = []
        with Session(self.engine) as session:
            login_list = [login[0]
                          for login in session.query(Client.login).all()]
            session.close()
        login_str = ", ".join(login_list)
        return login_str


if __name__ == "__main__":

    db_engine = create_engine("sqlite:///server_tables.db", echo=True)
    db_prototype = Server_DataBase(engine=db_engine, base=Base)
    with Session(db_engine) as session:

        # test 1
        admin_exists = session.query(Client).filter_by(
            login='admin').first() is not None

        # user_exists = session.query(Client).filter(
        #     Client.login.like('admin')).first() is not None

        if not admin_exists:
            print(f'создаю пользователя admin')
            client = Client(login='admin', info='info')
            session.add(client)
            session.commit()

        user1_exists = session.query(Client).filter_by(
            login='user1').first() is not None

        if not user1_exists:
            print(f'создаю пользователя user1')
            client = Client(login='user1', info='info')
            session.add(client)
            session.commit()

        user2_exists = session.query(Client).filter_by(
            login='user2').first() is not None

        if not user2_exists:
            print(f'создаю пользователя user2')
            client = Client(login='user2', info='info2')
            session.add(client)
            session.commit()

        owner = session.query(Client).where(
            Client.login == 'admin').first()

        contact = session.query(Client).where(
            Client.login == 'user1').first()

        contact_2 = session.query(Client).where(
            Client.login == 'user2').first()

        db_prototype.show_clients()

        # # проверить что есть запись с контактами
        # record_exists = session.query(Contact_list).where(
        #     Contact_list.owner_id == owner.client_id).one_or_none()
        # # если есть запись - проверить нет ли такого контакта уже в списке
        # if record_exists:
        #     record = session.query(Contact_list).filter(
        #         Contact_list.owner_id == owner.client_id).first()

        #     if str(contact_2.client_id) in record.contact_id_list:
        #         print('у вас уже есть такой контакт')
        #     else:
        #         # изменить на вытягивание из таблицы записи
        #         # добавление к списку контактов нового id
        #         # сохранение измененного списка контактов
        #         record.contact_id_list += f", {contact_2.client_id}"
        #         session.add(record)
        #         session.commit()
        # # если нет - создать запись и добавить первый контак в контакт лист
        # else:
        #     record = Contact_list(owner_id=owner.client_id, contact_id_list="")
        #     record.contact_id_list = str(contact.client_id)
        #     session.add(record)
        #     session.commit()


# test 2
        # owner = session.query(Client).where(
        #     Client.login == 'admin').first()

        # contacts = session.query(Client.login, Contact_list.list_id).join(
        #     Client, Contact_list.contact_id == Client.client_id).all()

        # for contact in contacts:
        #     print(contact._data)


# test 3

    # contact_to_delete = session.query(Contact_list).where(
    #     Contact_list.owner_id == client.client_id, Contact_list.contact_id == contact.client_id).one_or_none()

    # if contact_to_delete:
    #     session.delete(contact_to_delete)
    #     session.commit()
    # else:
    #     print('такого контакта нет в ващем списке')

    #     client = session.query(Client).where(
    #         Client.login == 'admin').first()

    #     client_history = Client_history(
    #         time=datetime.now(), ip_address='', client_id=client.client_id)

    #     session.add(client_history)
    #     session.commit()

    #     contact_list = Contact_list(owner_id=client.client_id, contacts=client.contact_id)
    #     session.add(contact_list)
    #     session.commit()
