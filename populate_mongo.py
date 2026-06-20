#!/usr/bin/env python
"""
Script to populate MongoDB with sample event data for VolunteerHub
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volunteerhub.settings')
django.setup()

from volunteerhub.mongo import events_collection, users_collection, registrations_collection, tasks_collection
from datetime import datetime

def populate_sample_data():
    """Insert sample data into MongoDB collections"""

    # Clear existing data
    events_collection.delete_many({})
    users_collection.delete_many({})
    registrations_collection.delete_many({})
    tasks_collection.delete_many({})

    # Sample Events
    sample_events = [
        {
            "name": "Community Park Cleanup",
            "date": "2026-04-15",
            "location": "Central Park, New York",
            "description": "Join us for a community cleanup event at Central Park. We'll be collecting litter, planting trees, and making our park beautiful again. Gloves and trash bags will be provided.",
            "created_by": "admin",
            "created_at": "2026-03-20T10:00:00Z"
        },
        {
            "name": "Food Bank Distribution",
            "date": "2026-04-20",
            "location": "Community Center, Brooklyn",
            "description": "Help distribute food packages to families in need. We need volunteers to sort donations, pack boxes, and assist with distribution.",
            "created_by": "admin",
            "created_at": "2026-03-20T11:00:00Z"
        },
        {
            "name": "Senior Center Visit",
            "date": "2026-04-25",
            "location": "Sunset Senior Living, Queens",
            "description": "Spend time with elderly residents at the senior center. Activities include reading, playing games, and providing companionship.",
            "created_by": "admin",
            "created_at": "2026-03-20T12:00:00Z"
        },
        {
            "name": "Animal Shelter Help",
            "date": "2026-05-01",
            "location": "Happy Tails Animal Shelter",
            "description": "Help care for animals at the local shelter. Tasks include walking dogs, cleaning kennels, and socializing with cats.",
            "created_by": "admin",
            "created_at": "2026-03-20T13:00:00Z"
        },
        {
            "name": "Beach Cleanup Drive",
            "date": "2026-05-10",
            "location": "Coney Island Beach",
            "description": "Large-scale beach cleanup event. We'll remove trash from the shoreline and educate visitors about marine conservation.",
            "created_by": "admin",
            "created_at": "2026-03-20T14:00:00Z"
        }
    ]

    # Sample Users
    sample_users = [
        {
            "username": "john_volunteer",
            "email": "john@example.com",
            "role": "volunteer",
            "first_name": "John",
            "last_name": "Smith",
            "date_joined": "2026-03-15T09:00:00Z"
        },
        {
            "username": "sarah_helper",
            "email": "sarah@example.com",
            "role": "volunteer",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "date_joined": "2026-03-16T10:00:00Z"
        },
        {
            "username": "mike_admin",
            "email": "mike@example.com",
            "role": "admin",
            "first_name": "Mike",
            "last_name": "Davis",
            "date_joined": "2026-03-10T08:00:00Z"
        }
    ]

    # Insert sample data
    events_result = events_collection.insert_many(sample_events)
    users_result = users_collection.insert_many(sample_users)

    print(f"✅ Inserted {len(events_result.inserted_ids)} events into MongoDB")
    print(f"✅ Inserted {len(users_result.inserted_ids)} users into MongoDB")
    print("\n📋 Sample Events Added:")
    for event in sample_events:
        print(f"  • {event['name']} - {event['date']} at {event['location']}")

    print("\n👥 Sample Users Added:")
    for user in sample_users:
        print(f"  • {user['username']} ({user['role']}) - {user['email']}")

if __name__ == "__main__":
    print("🌱 Populating MongoDB with sample data for VolunteerHub...")
    populate_sample_data()
    print("\n🎉 MongoDB populated successfully!")
    print("💡 You can now view your data in MongoDB Compass or MongoDB shell")