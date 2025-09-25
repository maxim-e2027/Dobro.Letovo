from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///DobroLetovo.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

class Volunteers(Base):
    __tablename__ = 'Volunteers'
    Volunteer_ID = Column(Integer, primary_key=True)
    Volunteer_Name = Column(String(50), nullable=False)
    Volunteer_Rating = Column(Integer)
    Volunteer_Hours = Column(Integer)
    #Volunteer_Description contains not the description itself, but the path to the file containing it
    Volunteer_Description = Column(String)

    def __repr__(self):
        return f"<Volunteer(ID={self.Volunteer_ID}, name={self.Volunteer_Name}, Hours={self.Volunteer_Hours})>"


class Organisations(Base):
    __tablename__ = 'Organisations'
    Organisation_ID = Column(Integer, primary_key=True)
    Organisation_Name = Column(String(50), nullable=False)
    #Organisation_Description contains not the description itself, but the path to the file containing it
    Organisation_Description = Column(String(20))

    def __repr__(self):
        return f"<Organisation(ID={self.Organisation_ID_ID}, name={self.Organisation_Name_Name}, Description={self.Organisation_Description})>"

class Comments(Base):
    __tablename__ = 'Comments'
    Comment_ID = Column(Integer, primary_key = True)
    Volunteer_ID = Column(Integer, nullable = False)
    Organisation_ID = Column(Integer, nullable = False)
    Comment_Date = Column(String(10))
    Comment_Text = Column(String(1000))
    Comment_Direction = Column(String(2))

    def __repr__(self):
        return f"<Comment(ID={self.Comment_ID}, Volunteer={self.Volunteer_ID}, Organisation={self.Organisation_ID}, Text={self.Comment_Text})>"

class Events(Base):
    __tablename__ = 'Events'
    Event_ID = Column(Integer, primary_key=True)
    Organisation_ID = Column(Integer, nullable=False)
    Required_Volunteers = Column(Integer)
    Event_Date = Column(String(10))
    Event_Description = Column(String(20))
    Event_Name = Column(String(50))

    def __repr__(self):
        return f"<Event(ID={self.Event_ID}, Name={self.Event_Name}, Organisation={self.Organisation_ID_ID}, Required Volunteers={self.Required_Volunteers})>"

class Requests(Base):
    __tablename__ = 'Requests'
    Request_ID = Column(Integer, primary_key=True)
    Volunteer_ID = Column(Integer, nullable=False)
    Event_ID = Column(Integer, nullable=False)
    Request_Status = Column(String(10))
    Request_Content = Column(String(20))

    def __repr__(self):
        return f"<Request(ID={self.Request_ID}, Volunteer={self.Volunteer_ID}, Event={self.Event_ID}, Status={self.Request_Status})>"

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

session.commit()

volunteer = session.query(Volunteers).filter_by(Volunteer_Name="Ivan Ivanovich Ivanov").all()
print(volunteer)
