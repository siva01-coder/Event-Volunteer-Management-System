from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bson import ObjectId
from .models import EventRegistration, Task
from volunteerhub.mongo import events_collection, registrations_collection, tasks_collection


def event_list(request):
    """Show all events - filtered by role"""
    raw_events = list(events_collection.find())
    events = []
    for e in raw_events:
        e['id'] = str(e['_id'])
        events.append(e)
    return render(request, 'events/event_list.html', {'events': events})


@login_required(login_url='/accounts/login/')
def admin_dashboard(request):
    """Admin dashboard - manage events and approve volunteers"""
    if request.user.role != 'admin':
        messages.error(
            request,
            'You do not have permission to access this page.'
        )
        return redirect('events:volunteer_dashboard')

    pending_approvals = EventRegistration.objects.filter(
        status='pending'
    ).select_related('volunteer')
    approved_volunteers = EventRegistration.objects.filter(
        status='approved'
    ).select_related('volunteer')

    # Get events created by this admin from MongoDB
    raw_admin_events = list(events_collection.find({'created_by': request.user.username}))
    admin_events = []
    for e in raw_admin_events:
        e['id'] = str(e['_id'])
        admin_events.append(e)
    total_events = len(admin_events)

    # Count approved volunteers for admin's events
    admin_event_ids = [event['id'] for event in admin_events]
    total_volunteers = EventRegistration.objects.filter(
        event_id__in=admin_event_ids,
        status='approved'
    ).count()

    context = {
        'pending_approvals': pending_approvals,
        'approved_volunteers': approved_volunteers,
        'events': admin_events,
        'total_events': total_events,
        'total_volunteers': total_volunteers,
    }
    return render(request, 'admin/dashboard.html', context)


@login_required(login_url='/accounts/login/')
def volunteer_dashboard(request):
    """Volunteer dashboard - see events and registered events"""
    if request.user.role != 'volunteer':
        messages.error(
            request,
            'You do not have permission to access this page.'
        )
        return redirect('events:admin_dashboard')

    registered_events = EventRegistration.objects.filter(
        volunteer=request.user
    )
    tasks = Task.objects.filter(
        registration__volunteer=request.user
    ).select_related('registration')
    completed_tasks = tasks.filter(status='completed').count()
    total_hours = completed_tasks * 4  # Assuming 4 hours per task
    total_events_registered = registered_events.count()

    context = {
        'registered_events': registered_events,
        'tasks': tasks,
        'completed_tasks': completed_tasks,
        'total_hours': total_hours,
        'total_events_registered': total_events_registered,
    }
    return render(request, 'volunteer/dashboard.html', context)


@login_required(login_url='/accounts/login/')
def register_for_event(request, event_id):
    """Volunteer registration for an event"""
    if request.user.role != 'volunteer':
        messages.error(request, 'Only volunteers can register for events.')
        return redirect('events:event_list')

    # Get event from MongoDB
    try:
        event = events_collection.find_one({'_id': ObjectId(event_id)})
        if not event:
            messages.error(request, 'Event not found.')
            return redirect('events:event_list')
    except Exception:
        messages.error(request, 'Invalid event ID.')
        return redirect('events:event_list')

    existing_registration = EventRegistration.objects.filter(
        volunteer=request.user,
        event_id=event_id  # Store MongoDB ObjectId as string
    ).first()

    if existing_registration:
        messages.warning(
            request,
            'You are already registered for this event.'
        )
        return redirect('events:event_list')

    reg = EventRegistration.objects.create(
        volunteer=request.user,
        event_id=event_id,
        event_name=event['name'],
        status='pending'
    )
    registrations_collection.insert_one({
        'volunteer': request.user.username,
        'event_id': event_id,
        'event_name': event['name'],
        'status': 'pending',
        'registered_at': reg.registered_at.isoformat(),
    })
    messages.success(
        request,
        'You have registered for the event. Waiting for admin approval.'
    )
    return redirect('events:volunteer_dashboard')


@login_required(login_url='/accounts/login/')
def approve_registration(request, registration_id):
    """Admin approves volunteer registration"""
    if request.user.role != 'admin':
        messages.error(
            request,
            'You do not have permission to approve registrations.'
        )
        return redirect('events:volunteer_dashboard')

    registration = get_object_or_404(EventRegistration, id=registration_id)
    registration.status = 'approved'
    registration.save()
    messages.success(
        request,
        f'{registration.volunteer.username} has been approved for '
        f'{registration.event_name}'
    )
    return redirect('events:admin_dashboard')


@login_required(login_url='/accounts/login/')
def reject_registration(request, registration_id):
    """Admin rejects volunteer registration"""
    if request.user.role != 'admin':
        messages.error(
            request,
            'You do not have permission to reject registrations.'
        )
        return redirect('events:volunteer_dashboard')

    registration = get_object_or_404(EventRegistration, id=registration_id)
    registration.status = 'rejected'
    registration.save()
    messages.success(
        request,
        f'{registration.volunteer.username} has been rejected for '
        f'{registration.event_name}'
    )
    return redirect('events:admin_dashboard')


@login_required(login_url='/accounts/login/')
def update_task_status(request, task_id):
    """Volunteer updates task status"""
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)

        if (task.registration.volunteer != request.user and
                request.user.role != 'admin'):
            messages.error(
                request,
                'You do not have permission to update this task.'
            )
            return redirect('events:volunteer_dashboard')

        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
            messages.success(request, f'Task status updated to {new_status}.')
        else:
            messages.error(request, 'Invalid status.')

        if request.user.role == 'admin':
            return redirect('events:admin_dashboard')
        return redirect('events:volunteer_dashboard')

    return redirect('events:volunteer_dashboard')


@login_required(login_url='/accounts/login/')
def create_event(request):
    """Admin creates a new event"""
    if request.user.role != 'admin':
        messages.error(request, 'Only admins can create events.')
        return redirect('events:event_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        location = request.POST.get('location')
        description = request.POST.get('description')

        if name and date and location and description:
            event_data = {
                'name': name,
                'date': date,
                'location': location,
                'description': description,
                'created_by': request.user.username,
                'created_at': str(request.user.date_joined)
            }
            events_collection.insert_one(event_data)
            messages.success(request, 'Event created successfully!')
            return redirect('events:event_list')
        else:
            messages.error(request, 'All fields are required.')

    return render(request, 'admin/create_event.html')


@login_required(login_url='/accounts/login/')
def assign_task(request, registration_id):
    """Admin assigns task to approved volunteer"""
    if request.user.role != 'admin':
        messages.error(request, 'Only admins can assign tasks.')
        return redirect('events:event_list')

    registration = get_object_or_404(EventRegistration, id=registration_id)

    if registration.status != 'approved':
        messages.error(
            request,
            'Can only assign tasks to approved volunteers.'
        )
        return redirect('events:admin_dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        if title and description:
            task = Task.objects.create(
                registration=registration,
                title=title,
                description=description
            )
            tasks_collection.insert_one({
                'volunteer': registration.volunteer.username,
                'event_id': registration.event_id,
                'event_name': registration.event_name,
                'title': title,
                'description': description,
                'status': 'assigned',
                'created_at': task.created_at.isoformat(),
            })
            messages.success(
                request,
                f'Task assigned to {registration.volunteer.username}.'
            )
            return redirect('events:admin_dashboard')
        else:
            messages.error(request, 'All fields are required.')

    context = {'registration': registration}
    return render(request, 'admin/assign_task.html', context)
