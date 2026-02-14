"""
Database models for Smart Parking System Web Application
Uses SQLAlchemy for ORM and SQLite for storage
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


class ReferenceImage(db.Model):
    """Model for storing reference images used in parking space setup"""
    __tablename__ = 'reference_images'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    video_source = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    
    def __repr__(self):
        return f"<ReferenceImage {self.name} ({self.width}x{self.height})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'filename': self.filename,
            'width': self.width,
            'height': self.height,
            'video_source': self.video_source,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ParkingSpaceGroup(db.Model):
    """Model for grouping parking spaces (e.g., for larger vehicles)"""
    __tablename__ = 'parking_space_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    member_spaces = db.Column(db.Text, nullable=False)  # JSON string of space IDs
    section = db.Column(db.String(100), default="General")
    is_occupied = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    
    def __repr__(self):
        return f"<ParkingSpaceGroup {self.group_id}: {self.name}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        import json
        return {
            'id': self.id,
            'group_id': self.group_id,
            'name': self.name,
            'member_spaces': json.loads(self.member_spaces) if self.member_spaces else [],
            'section': self.section,
            'is_occupied': self.is_occupied,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_db(app):
    """Initialize database with Flask app"""
    # Configure SQLAlchemy
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'parking.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize db with app
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        print(f"Database initialized at: {db_path}")
