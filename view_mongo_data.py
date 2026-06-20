#!/usr/bin/env python
"""
Script to view MongoDB data for VolunteerHub
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'volunteerhub.settings')
django.setup()

from volunteerhub.mongo import (
    events_collection,
    users_collection,
    registrations_collection,
    tasks_collection,
)

def view_mongodb_data():
    """Display all data in MongoDB collections"""

    print("📊 VolunteerHub MongoDB Data Viewer")
    print("=" * 50)

    # Events
    print("\n🎯 EVENTS COLLECTION:")
    events = list(events_collection.find())
    if events:
        for i, event in enumerate(events, 1):
            print(f"{i}. {event['name']}")
            print(f"   📅 Date: {event['date']}")
            print(f"   📍 Location: {event['location']}")
            print(f"   📝 Description: {event['description'][:100]}...")
            print(f"   👤 Created by: {event['created_by']}")
            print()
    else:
        print("   No events found")

    # Users
    print("\n👥 USERS COLLECTION:")
    users = list(users_collection.find())
    if users:
        for i, user in enumerate(users, 1):
            print(f"{i}. {user['username']} ({user['role']})")
            print(f"   📧 Email: {user['email']}")
            print(f"   📅 Joined: {user['date_joined']}")
            print()
    else:
        print("   No users found")

    # Registrations
    print("\n📝 REGISTRATIONS COLLECTION:")
    registrations = list(registrations_collection.find())
    if registrations:
        for i, reg in enumerate(registrations, 1):
            print(f"{i}. Volunteer: {reg.get('volunteer_username', 'Unknown')}")
            print(f"   🎯 Event: {reg.get('event_name', 'Unknown')}")
            print(f"   📊 Status: {reg.get('status', 'Unknown')}")
            print()
    else:
        print("   No registrations found")

    # Tasks
    print("\n✅ TASKS COLLECTION:")
    tasks = list(tasks_collection.find())
    if tasks:
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task['title']}")
            print(f"   📝 Description: {task.get('description', 'No description')}")
            print(f"   👤 Assigned to: {task.get('volunteer_username', 'Unknown')}")
            print(f"   📊 Status: {task.get('status', 'pending')}")
            print()
    else:
        print("   No tasks found")

    print("\n" + "=" * 50)
    print("💡 Tip: Visit http://localhost:8000 to see this data in your web app!")

if __name__ == "__main__":
    view_mongodb_data()