#!/usr/bin/env python3
"""
Integration tests for web application features
Tests reference management and setup functionality
"""

import os
import sys
import json
import tempfile
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_app import app
from models.database import db, ReferenceImage, ParkingSpaceGroup


def test_database_models():
    """Test database models initialization"""
    with app.app_context():
        db.create_all()
        
        # Test ReferenceImage model
        ref = ReferenceImage(
            name="Test Image",
            filename="test.jpg",
            width=800,
            height=600,
            video_source="test.mp4"
        )
        db.session.add(ref)
        db.session.commit()
        
        # Query and verify
        saved_ref = ReferenceImage.query.filter_by(name="Test Image").first()
        assert saved_ref is not None
        assert saved_ref.width == 800
        assert saved_ref.height == 600
        
        # Test ParkingSpaceGroup model
        group = ParkingSpaceGroup(
            group_id="TEST_001",
            name="Test Group",
            member_spaces=json.dumps(["S1", "S2"])
        )
        db.session.add(group)
        db.session.commit()
        
        # Query and verify
        saved_group = ParkingSpaceGroup.query.filter_by(group_id="TEST_001").first()
        assert saved_group is not None
        assert saved_group.name == "Test Group"
        
        print("✅ Database models test passed")


def test_api_endpoints():
    """Test API endpoints"""
    client = app.test_client()
    
    # Test references page
    response = client.get('/references')
    assert response.status_code == 200
    print("✅ References page test passed")
    
    # Test setup page
    response = client.get('/setup')
    assert response.status_code == 200
    print("✅ Setup page test passed")
    
    # Test setup load (should work even with no data)
    response = client.get('/api/setup/load')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    print("✅ Setup load test passed")
    
    # Test setup save
    test_spaces = [
        {"x": 10, "y": 10, "width": 100, "height": 50, "id": "TEST1"}
    ]
    response = client.post('/api/setup/save', data={
        'spaces': json.dumps(test_spaces),
        'reference_id': '1'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    print("✅ Setup save test passed")


def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        'models/database.py',
        'templates/references.html',
        'templates/setup.html',
        'WEB_FEATURES.md',
        'web_app.py'
    ]
    
    for file in required_files:
        assert os.path.exists(file), f"Missing file: {file}"
    
    print("✅ File structure test passed")


def test_media_directories():
    """Test that media directories exist"""
    required_dirs = [
        'media/references',
        'config'
    ]
    
    for dir in required_dirs:
        assert os.path.exists(dir), f"Missing directory: {dir}"
    
    print("✅ Media directories test passed")


if __name__ == '__main__':
    print("=" * 50)
    print("Running Integration Tests")
    print("=" * 50)
    
    try:
        test_file_structure()
        test_media_directories()
        test_database_models()
        test_api_endpoints()
        
        print("=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
        sys.exit(0)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
