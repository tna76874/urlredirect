#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
database modules
"""
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String, Boolean, Integer, DateTime, ForeignKey, func, and_, MetaData, inspect, text, desc
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, sessionmaker, Session, aliased, declarative_base, joinedload
from sqlalchemy.exc import IntegrityError
import uuid
import pytz
from datetime import datetime, timedelta, timezone
import os

Base = declarative_base()

class Redirect(Base):
    __tablename__ = 'redirects'

    rid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, nullable=False)
    redirect = Column(String, nullable=False)

    # Relationship to events
    events = relationship("Event", back_populates="redirect")


class Alias(Base):
    __tablename__ = 'aliases'

    aid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, nullable=False)
    rid = Column(String, ForeignKey('redirects.rid'), nullable=False)
    
class Event(Base):
    __tablename__ = 'events'

    eid = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rid = Column(String, ForeignKey('redirects.rid'), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    source = Column(String, nullable=False)

    # Relationship to redirects
    redirect = relationship("Redirect", back_populates="events")
    


    
class DatabaseManager:
    """
    Class for managing the database operations.
    """
    def __init__(self, data='data/data.db'):
        """
        Initialize the DatabaseManager with a given data file.

        :param data: The name of the database file.
        """
        db_url = f'sqlite:///{data}'
        self.engine = create_engine(db_url, echo=False)
        self.session = Session(bind=self.engine)
        self.ensure_all_tables()

    def _add_event(self, key=None, source=None):
        """
        Add a new event associated with a redirect or alias.
    
        :param key: The key of the redirect or alias.
        :param source: The source of the event.
        :return: The created event object.
        """
        # Check if both key and source are None
        if key is None or source is None:
            raise ValueError("Both 'key' and 'source' must be provided.")
        
        with self.get_session() as session:
            # Try to find the redirect by key
            redirect = session.query(Redirect).filter_by(key=key).first()
            
            if redirect:
                rid = redirect.rid
            else:
                # If not found in Redirect, check in Alias
                alias = session.query(Alias).filter_by(key=key).first()
                if alias:
                    redirect = session.query(Redirect).filter_by(rid=alias.rid).first()
                    if redirect:
                        rid = redirect.rid
                    else:
                        return
                else:
                    return
    
            # Create a new event
            new_event = Event(rid=rid, source=source)
            session.add(new_event)
            
            # Commit the changes to the database
            session.commit()


    def _ensure_redirect(self, **data):
        """
        Add or update a redirect. If the key is an alias, remove the alias first.
    
        :param data: A dictionary containing 'key' and 'redirect'.
        """
        key = data.get('key')
        redirect_url = data.get('redirect')
    
        if not key or not redirect_url:
            raise ValueError("Both 'key' and 'redirect' must be provided.")
    
        with self.get_session() as session:
            # Check if the key is an alias
            alias = session.query(Alias).filter_by(key=key).first()
            if alias:
                # If it is an alias, remove it
                self._remove_alias(key)
    
            # Check if the redirect already exists
            existing_redirect = session.query(Redirect).filter_by(key=key).first()
    
            if existing_redirect:
                # If it exists, check if the redirect URL is different
                if existing_redirect.redirect != redirect_url:
                    # Update the existing redirect
                    existing_redirect.redirect = redirect_url
                    session.commit()
            else:
                # Create a new redirect
                new_redirect = Redirect(key=key, redirect=redirect_url)
                session.add(new_redirect)
                session.commit()

    def _add_alias(self, alias=None, key=None):
        """
        Add an alias for a given key.
    
        :param alias: The alias key to be added.
        :param key: The key for which the alias is being created.
        """
        if not alias or not key:
            raise ValueError("Both 'alias' and 'key' must be provided.")
    
        with self.get_session() as session:
            # Check if the key exists in redirects
            redirect = session.query(Redirect).filter_by(key=key).first()
            if not redirect:
                raise ValueError(f"The key '{key}' does not exist in redirects.")
                
            # Check if the alias already exists
            alias_exist_as_redirect = session.query(Redirect).filter_by(key=alias).first()
            if alias_exist_as_redirect:
                raise ValueError(f"The alias '{alias}' already exists as redirect.")
    
            # Create a new alias
            new_alias = Alias(key=alias, rid=redirect.rid)
            session.add(new_alias)
            session.commit()
                    
    def _remove_alias(self, key):
        """
        Remove an alias by key.
    
        :param key: The key of the alias to remove.
        """
        with self.get_session() as session:
            existing_alias = session.query(Alias).filter_by(key=key).first()
            if existing_alias:
                session.delete(existing_alias)
                session.commit()
                
    def _delete_redirect(self, key):
        """
        Delete a redirect or alias based on the provided key.
    
        :param key: The key of the redirect or alias to delete.
        """
        with self.get_session() as session:
            # Check if the key is an alias
            alias = session.query(Alias).filter_by(key=key).first()
            if alias:
                # If it is an alias, remove it
                self._remove_alias(key)

            # Check if the key is a redirect
            redirect_to_delete = session.query(Redirect).filter_by(key=key).first()
            if redirect_to_delete:
                # Delete all associated aliases
                session.query(Alias).filter_by(rid=redirect_to_delete.rid).delete()
                # Delete the redirect
                session.delete(redirect_to_delete)
                session.commit()

    def _rename_key(self, old=None, new=None):
        """
        Rename the key of an existing redirect.

        :param old: The old key of the redirect.
        :param new: The new key to be set.
        """
        if not old or not new:
            raise ValueError("Both 'old' and 'new' keys must be provided.")

        with self.get_session() as session:
            # Check if the redirect with the old key exists
            existing_redirect = session.query(Redirect).filter_by(key=old).first()

            if existing_redirect:
                if session.query(Redirect).filter_by(key=new).first():
                    return

                existing_redirect.key = new
                session.commit()
                
    def _get_redirect(self, key):
        """
        Get the redirect for a given key. If the key is an alias, retrieve the redirect for the associated key.
    
        :param key: The key of the redirect to retrieve.
        :return: The redirect URL if found, otherwise None.
        """
        if not key:
            raise ValueError("The 'key' must be provided.")
    
        with self.get_session() as session:
            # Check if the key is an alias
            alias = session.query(Alias).filter_by(key=key).first()
            if alias:
                # If it is an alias, get the redirect associated with the rid
                redirect = session.query(Redirect).filter_by(rid=alias.rid).first()
            else:
                # Otherwise, get the redirect directly by key
                redirect = session.query(Redirect).filter_by(key=key).first()
    
            if redirect:
                redirect_url = redirect.redirect
                # Ensure the URL starts with https
                if redirect_url.startswith("http://"):
                    redirect_url = redirect_url.replace("http://", "https://")
                if not redirect_url.startswith("https://"):
                    redirect_url = "https://" + redirect_url
                return redirect_url
            else:
                return None

    def _get_all_redirects(self):
        """
        Get all redirects and aliases in a unified list.

        :return: A list of dictionaries containing 'key' and 'redirect'.
        """
        with self.get_session() as session:
            result = []

            # Get all redirects
            redirects = session.query(Redirect).all()
            for redirect in redirects:
                result.append({
                    'key': redirect.key,
                    'redirect': redirect.redirect
                })

            # Get all aliases and their corresponding redirect URLs
            aliases = session.query(Alias).all()
            for alias in aliases:
                redirect = session.query(Redirect).filter_by(rid=alias.rid).first()
                if redirect:
                    result.append({
                        'key': alias.key,
                        'redirect': redirect.redirect
                    })

            return result

    def _delete_all(self):
        """
        Delete all entries in Redirect and Alias tables.
    
        :return: None
        """
        with self.get_session() as session:
            # Delete all entries in Redirect
            session.query(Redirect).delete()
            
            # Delete all entries in Alias
            session.query(Alias).delete()
            
            # Commit the changes to the database
            session.commit()

    def _allow_request(self, source):
        """
        Check if the request from the given source is allowed based on the rate limit.
    
        :param source: The source (IP address) of the request.
        :return: True if the request is allowed, False otherwise.
        """
        try:
            with self.get_session() as session:
                # Define the time window (last 2 minutes)
                time_window = datetime.utcnow() - timedelta(minutes=2)
    
                # Count the number of events for the given source within the time window
                request_count = session.query(Event).filter(
                    Event.source == source,
                    Event.date >= time_window
                ).count()
    
                # Check if the request count exceeds the limit
                if request_count >= 30:
                    return False  # Too many requests
                else:
                    return True  # Request is allowed
        except:
            return False  

    @contextmanager
    def get_session(self):
        Session = sessionmaker(bind=self.engine)
        session = Session()
        try:
            yield session
        except Exception as e:
            print(f"An error occurred: {e}")
            session.rollback()
        finally:
            session.close()

    def ensure_all_tables(self):
        # Create a MetaData object
        metadata = MetaData()
    
        # Bind the MetaData object with the existing database engine
        metadata.reflect(bind=self.engine)
    
        # Iterate over all tables in the Base.metadata
        for table_name, table in Base.metadata.tables.items():
            # Get the existing table from the reflected metadata
            existing_table = metadata.tables.get(table_name)
    
            # Check if the table does not exist in the database
            if existing_table is None:
                # If the table does not exist, create it
                table.create(bind=self.engine)
    
                # Print a message indicating that the table has been created
                print(f"Table '{table_name}' created.")
            else:
                # If the table already exists, check for missing columns
                for column in table.columns:
                    # Check if the column does not exist in the existing table
                    if column.name not in existing_table.columns:
                        # If the column does not exist, add it to the existing table
                        new_column = Column(
                            column.name,
                            column.type,
                            primary_key=column.primary_key,
                            nullable=column.nullable,
                            default=column.default,
                            unique=column.unique
                        )
                        with self.engine.connect() as con:
                            column_info = f"{new_column.name} {new_column.type.compile(self.engine.dialect)}"
                            add_query = f"ALTER TABLE {table_name} ADD COLUMN {column_info}"
                            # print(add_query)
                            con.execute(text(add_query))
    
                        # Print a message indicating that the column has been created
                        print(f"Column '{column.name}' added to table '{table_name}'.")
            
if __name__ == '__main__':
    self = DatabaseManager()