from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import declarative_base, sessionmaker
import bcrypt

DATABASE_URL = "sqlite:///DobroLetovo.db"
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()

class Volunteer(Base):
    __tablename__ = 'Volunteers'
    Volunteer_ID = Column(Integer, primary_key=True)
    Volunteer_Name = Column(String(50), nullable=False)
    Volunteer_Rating = Column(Integer)
    Volunteer_Hours = Column(Integer)
    #Volunteer_Description contains not the description itself, but the path to the file containing it
    Volunteer_Description = Column(String)

    def __repr__(self):
        return f"<Volunteer(ID={self.Volunteer_ID}, name={self.Volunteer_Name}, Hours={self.Volunteer_Hours})>"


class Organisation(Base):
    __tablename__ = 'Organisations'
    Organisation_ID = Column(Integer, primary_key=True)
    Organisation_Name = Column(String(50), nullable=False)
    #Organisation_Description contains not the description itself, but the path to the file containing it
    Organisation_Description = Column(String(20))

    def __repr__(self):
        return f"<Organisation(ID={self.Organisation_ID_ID}, name={self.Organisation_Name_Name}, Description={self.Organisation_Description})>"
class Volunteer_Autentification(Base):
    __tablename__ = 'Volunteer_Autentification'
    Volunteer_ID = Column(Integer, primary_key=True)
    Volunteer_Username = Column(String(128), nullable=False)
    Volunteer_Password_Hash = Column(String(128), nullable=False)
    # Organisation_Description contains not the description itself, but the path to the file containing it
    Organisation_Description = Column(String(20))

    def __repr__(self):
        return f"<Volunteer(ID={self.Organisation_ID_ID})>"

    def set_password(self, password: str):
        self.Volunteer_Password_Hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.Volunteer_Password_Hash.encode('utf-8'))

class Organzation_Autentification(Base):
    extend_existing = True
    __tablename__ = 'Organization_Autentification'
    Organization_ID = Column(Integer, primary_key=True)
    Organization_Username = Column(String(128), nullable=False)
    Organization_Password_Hash = Column(String(128), nullable=False)
    # Organisation_Description contains not the description itself, but the path to the file containing it
    Organisation_Description = Column(String(20))

    def __repr__(self):
        return f"<Organisation(ID={self.Organisation_ID})"

    def set_password(self, password: str):
        self.Organization_Password_Hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.Organization_Password_Hash.encode('utf-8'))


class Comment(Base):
    __tablename__ = 'Comments'
    Comment_ID = Column(Integer, primary_key = True)
    Volunteer_ID = Column(Integer, nullable = False)
    Organisation_ID = Column(Integer, nullable = False)
    Comment_Date = Column(String(10))
    Comment_Text = Column(String(1000))
    Comment_Direction = Column(String(2))

    def __repr__(self):
        return f"<Comment(ID={self.Comment_ID}, Volunteer={self.Volunteer_ID}, Organisation={self.Organisation_ID}, Text={self.Comment_Text})>"

class Event(Base):
    __tablename__ = 'Events'
    Event_ID = Column(Integer, primary_key=True)
    Organisation_ID = Column(Integer, nullable=False)
    Required_Volunteers = Column(Integer)
    Event_Date = Column(String(10))
    Event_Description = Column(String(20))
    Event_Name = Column(String(50))

    def __repr__(self):
        return f"<Event(ID={self.Event_ID}, Name={self.Event_Name}, Organisation={self.Organisation_ID_ID}, Required Volunteers={self.Required_Volunteers})>"

class Request(Base):
    __tablename__ = 'Requests'
    Request_ID = Column(Integer, primary_key=True)
    Volunteer_ID = Column(Integer, nullable=False)
    Event_ID = Column(Integer, nullable=False)
    Request_Status = Column(String(10))
    Request_Content = Column(String(20))

    def __repr__(self):
        return f"<Request(ID={self.Request_ID}, Volunteer={self.Volunteer_ID}, Event={self.Event_ID}, Status={self.Request_Status})>"

def register_volunteer(username: str, password: str, name: str, description: str):
    if session.query(Volunteer_Autentification).filter_by(Volunteer_Username=username).first():
        print("Username already exists.")
        return "Username already exists"

    # Get max ID
    last_id = session.query(func.max(Volunteer.Volunteer_ID)).scalar()
    new_id = (last_id or 0) + 1  # If no volunteers yet, start from 1

    # Create authentification entry
    user_auth = Volunteer_Autentification(Volunteer_ID=new_id, Volunteer_Username=username)
    user_auth.set_password(password)
    session.add(user_auth)

    # Create Volunteer profile
    user_profile = Volunteer(
        Volunteer_ID=new_id,
        Volunteer_Name=name,
        Volunteer_Description=description,
        Volunteer_Rating=100,
        Volunteer_Hours=0
    )
    session.add(user_profile)

    session.commit()
    print(f"User '{username}' registered successfully.")

def register_organization(username: str, password: str, name: str, description: str):
    if session.query(Organzation_Autentification).filter_by(username=username).first():
        print("Username already exists.")
        return "Username already exists"

    #Get max ID
    last_id = session.query(func.max(Organisation.Organization_ID)).scalar()
    new_id = (last_id or 0) + 1  # If no volunteers yet, start from 1

    #Create authentification entry
    user_auth = Organzation_Autentification(Organization_ID = new_id, username=username)
    user_auth.set_password(password)
    session.add(user_auth)

    #Create Volunteerprofile
    user_profile = Volunteer(
        Organization_ID = new_id,
        Organization_Name = name,
        Organization_Description = description
    )
    session.add(user_profile)

    session.commit()
    print(f"User '{username}' registered successfully.")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

new_volunteer = Volunteer(
    Volunteer_ID=4,
    Volunteer_Name="Petr",
    Volunteer_Rating=90,
    Volunteer_Hours=404,
    Volunteer_Description="path/to/description.txt"
)
#session.add(new_volunteer)
session.commit()

volunteer = session.query(Volunteer).filter_by(Volunteer_Hours = 404).all()
print(volunteer)

