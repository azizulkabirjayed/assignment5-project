from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.utils import timezone
from .models import All_Users, Classroom_Students, Classroom_Requests, Classrooms, Announcements, Notices, Attendance, Resources







def signup(request):
    if request.method == 'POST':
        # Get data from the form
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # Check if email or username already exists
        if All_Users.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use!')
            return redirect('signup')
        
        if All_Users.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken!')
            return redirect('signup')

        # Create a new user with role set as 'student' (password is hashed using set_password)
        user = All_Users.objects.create_user(  # Use create_user instead of create() to properly handle password hashing
            email=email,
            username=username,
            password=password,  # This will be hashed by the set_password method
            first_name=first_name,
            last_name=last_name,
            role='student',  # Default role set to 'student'
        )

        # Log the user in automatically after registration (optional)
        messages.success(request, 'Account created successfully! You can now log in.')
        return redirect('index')  # Redirect to the login page

    return render(request, 'main/signup.html')

def index(request):
    if request.user.is_authenticated:
        # Redirect to the appropriate dashboard based on user role
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'faculty':
            return redirect('faculty_dashboard')
        else:  # Default to student dashboard
            return redirect('student_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username_email')  # Field is still named username_email in the form
        password = request.POST.get('password')

        # Authenticate the user using username and password
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_active:
            # User is authenticated, log them in
            login(request, user)
            # Redirect to the appropriate dashboard based on user role
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'faculty':
                return redirect('faculty_dashboard')
            else:  # Default to student dashboard
                return redirect('student_dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
            return render(request, 'main/index.html')  # Render index.html with error message

    return render(request, 'main/index.html')  # Render the login page for GET requests



def admin_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('index')
    notices = Notices.objects.filter(admin_id=request.user)
    return render(request, 'admin/admin_dashboard.html', {'notices': notices})

def faculty_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'faculty':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('index')
    classrooms = Classrooms.objects.filter(faculty_id=request.user)
    announcements = Announcements.objects.filter(faculty_id=request.user)
    return render(request, 'faculty/faculty_dashboard.html', {'classrooms': classrooms, 'announcements': announcements})

def student_dashboard(request):
    if not request.user.is_authenticated or request.user.role != 'student':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('index')
    enrolled_classrooms = Classroom_Students.objects.filter(student_id=request.user)
    pending_requests = Classroom_Requests.objects.filter(student_id=request.user, status='pending')
    return render(request, 'student/student_dashboard.html', {'enrolled_classrooms': enrolled_classrooms, 'pending_requests': pending_requests})






@login_required
def notice_board(request, notice_id=None):
    # Handle deletion if notice_id is provided and request method is POST
    if notice_id and request.method == 'POST':
        notice = get_object_or_404(Notices, notice_id=notice_id)
        notice.delete()
        messages.success(request, 'Notice deleted successfully.')
        return redirect('notice_board')
    
    # Retrieve all notices, ordered by posted_at (newest first)
    notices = Notices.objects.all().order_by('-posted_at')
    return render(request, 'admin/notice_board.html', {'notices': notices})




@login_required
def add_notice(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        # Validate input
        if not title or not content:
            messages.error(request, 'Title and content are required.')
            return render(request, 'admin/add_notice.html')
        
        # Create new notice
        try:
            Notices.objects.create(
                admin_id=request.user,  # Assuming All_Users is linked to the authenticated user
                title=title,
                content=content
            )
            messages.success(request, 'Notice added successfully.')
            return redirect('notice_board')
        except Exception as e:
            messages.error(request, f'Error adding notice: {str(e)}')
            return render(request, 'admin/add_notice.html')
    return render(request, 'admin/add_notice.html')



@login_required
def add_faculty(request):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to add faculty.')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validate input
        if not all([first_name, last_name, username, email, password, confirm_password]):
            messages.error(request, 'All fields are required.')
            return render(request, 'admin/add_faculty.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'admin/add_faculty.html')
        
        # Check if username or email already exists
        if All_Users.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'admin/add_faculty.html')
        
        if All_Users.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'admin/add_faculty.html')
        
        # Create new faculty user
        try:
            user = All_Users.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='faculty'
            )
            messages.success(request, 'Faculty added successfully.')
            return redirect('faculty_list')
        except Exception as e:
            messages.error(request, f'Error adding faculty: {str(e)}')
            return render(request, 'admin/add_faculty.html')
    
    return render(request, 'admin/add_faculty.html')



@login_required
def faculty_list(request, user_id=None):
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view or manage faculty.')
        return redirect('admin_dashboard')
    
    # Handle deletion if user_id is provided and request method is POST
    if user_id and request.method == 'POST':
        user = get_object_or_404(All_Users, id=user_id, role='faculty')
        user.delete()
        messages.success(request, 'Faculty deleted successfully.')
        return redirect('faculty_list')
    
    # Retrieve all faculty users
    faculty = All_Users.objects.filter(role='faculty').order_by('first_name')
    return render(request, 'admin/faculty_list.html', {'faculty': faculty})


def logout_view(request):
    # Log the user out
    logout(request)
    # Render the logout.html template
    response = render(request, 'main/logout.html')
    # Delete session cookies (sessionid is the default name for session cookie)
    response.delete_cookie('sessionid')
    # Optionally, delete any other cookies you want to clear (if set by the app)
    # response.delete_cookie('your_cookie_name')
    # Return the response which will clear cookies and render logout.html
    return response


@login_required
def uni_notice_board(request):
    if request.user.role != 'faculty':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('faculty_dashboard')
    notices = Notices.objects.all().order_by('-posted_at')
    return render(request, 'faculty/uni_notice_board.html', {'notices': notices})
# done
@login_required
def create_classroom(request):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can create classrooms.')
        return redirect('faculty_dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if not name:
            messages.error(request, 'Classroom name is required.')
            return render(request, 'faculty/create_classroom.html')
        
        try:
            Classrooms.objects.create(
                faculty_id=All_Users.objects.get(id=request.user.id),
                name=name,
                description=description
            )
            messages.success(request, 'Classroom created successfully.')
            return redirect('classroom_list')
        except Exception as e:
            messages.error(request, f'Error creating classroom: {str(e)}')
            return render(request, 'faculty/create_classroom.html')
    
    return render(request, 'faculty/create_classroom.html')

@login_required
def classroom_list(request):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can view their classrooms.')
        return redirect('faculty_dashboard')
    
    if request.method == 'POST':
        classroom_id = request.POST.get('classroom_id')
        if not classroom_id or not classroom_id.isdigit():
            messages.error(request, 'Invalid classroom ID.')
            return redirect('classroom_list')
        
        classroom = get_object_or_404(Classrooms, classroom_id=classroom_id)
        if classroom.faculty_id != request.user:
            messages.error(request, 'You do not have permission to delete this classroom.')
            return redirect('classroom_list')
        
        try:
            classroom_name = classroom.name
            classroom.delete()
            messages.success(request, f'Classroom "{classroom_name}" deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting classroom: {str(e)}')
        
        return redirect('classroom_list')
    
    classrooms = Classrooms.objects.filter(faculty_id=request.user).order_by('name')
    return render(request, 'faculty/classroom_list.html', {'classrooms': classrooms})



@login_required
def add_student(request):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can manage student requests.')
        return redirect('faculty_dashboard')
    
    # Fetch all classrooms created by the logged-in faculty
    classrooms = Classrooms.objects.filter(faculty_id=request.user).order_by('name')
    # Dictionary to store pending requests for each classroom
    classroom_requests = {}
    
    for classroom in classrooms:
        pending_requests = Classroom_Requests.objects.filter(
            classroom_id=classroom, status='pending'
        ).order_by('requested_at')
        classroom_requests[classroom] = pending_requests
    
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        classroom_id = request.POST.get('classroom_id')
        action = request.POST.get('action')
        
        # Validate classroom_id and request_id
        if not classroom_id or not classroom_id.isdigit():
            messages.error(request, 'Invalid classroom ID.')
            return redirect('add_student')
        if not request_id or not request_id.isdigit():
            messages.error(request, 'Invalid request ID.')
            return redirect('add_student')
        
        # Query classroom using classroom_id
        classroom = get_object_or_404(Classrooms, classroom_id=classroom_id)
        if classroom.faculty_id != request.user:
            messages.error(request, 'You do not have permission to manage this classroom.')
            return redirect('add_student')
        
        # Query class request
        class_request = get_object_or_404(
            Classroom_Requests, request_id=request_id, classroom_id=classroom, status='pending'
        )
        
        try:
            if action == 'approve':
                # Add student to Classroom_Students
                Classroom_Students.objects.create(
                    classroom_id=classroom,
                    student_id=class_request.student_id
                )
                # Update request status
                class_request.status = 'approved'
                class_request.save()
                messages.success(request, f'Request from {class_request.student_id.username} approved.')
            elif action == 'reject':
                # Update request status to rejected
                class_request.status = 'rejected'
                class_request.save()
                messages.success(request, f'Request from {class_request.student_id.username} rejected.')
            else:
                messages.error(request, 'Invalid action.')
        except Exception as e:
            messages.error(request, f'Error processing request: {str(e)}')
        
        return redirect('add_student')
    
    return render(request, 'faculty/add_student.html', {
        'classroom_requests': classroom_requests
    })




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Classrooms

@login_required
def add_attendance(request):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can manage attendance.')
        return redirect('faculty_dashboard')
    
    # Fetch classrooms created by the logged-in faculty
    classrooms = Classrooms.objects.filter(faculty_id=request.user).order_by('name')
    
    return render(request, 'faculty/add_attendance.html', {
        'classrooms': classrooms
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Classrooms, Classroom_Students, Attendance, All_Users

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Classrooms, Classroom_Students, Attendance, All_Users

@login_required
def att_form(request, classroom_id):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can manage attendance.')
        return redirect('faculty_dashboard')
    
    # Fetch the classroom using the correct primary key field: classroom_id
    classroom = get_object_or_404(Classrooms, classroom_id=classroom_id)
    
    # Verify the classroom belongs to the logged-in faculty
    if classroom.faculty_id != request.user:
        messages.error(request, 'You do not have permission to manage this classroom.')
        return redirect('add_attendance')
    
    # Fetch students enrolled in the classroom
    students = Classroom_Students.objects.filter(classroom_id=classroom).order_by('student_id__username')
    
    # Set today's date
    today = timezone.now().date()
    
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('attendance_'):
                student_id = key.split('_')[1]
                student = get_object_or_404(All_Users, id=student_id)
                
                if value in ['present', 'absent']:
                    # Check if attendance already exists for this student on this date
                    existing_attendance = Attendance.objects.filter(
                        classroom_id=classroom,
                        student_id=student,
                        session_date=today
                    ).first()
                    
                    if existing_attendance:
                        # Update existing record
                        existing_attendance.midday_status = value
                        existing_attendance.save()
                    else:
                        # Create new record
                        Attendance.objects.create(
                            classroom_id=classroom,
                            student_id=student,
                            session_date=today,
                            midday_status=value
                        )
                    messages.success(request, f'Attendance recorded for {student.username}.')
        
        return redirect('att_form', classroom_id=classroom_id)
    
    return render(request, 'faculty/att_form.html', {
        'classroom': classroom,
        'students': students,
        'today': today
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Attendance, Classrooms

@login_required
def attendance_list(request):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can view attendance records.')
        return redirect('faculty_dashboard')
    
    # Fetch classrooms managed by the logged-in faculty
    classrooms = Classrooms.objects.filter(faculty_id=request.user)
    
    # Fetch attendance records for those classrooms
    attendance_records = Attendance.objects.filter(classroom_id__in=classrooms).order_by('-session_date')
    
    return render(request, 'faculty/attendance_list.html', {
        'attendance_records': attendance_records
    })





@login_required
def announcements_list(request):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can view announcements.')
        return redirect('faculty_dashboard')
    
    # Fetch all announcements for the logged-in faculty
    announcements = Announcements.objects.filter(faculty_id=request.user).order_by('classroom_id', '-posted_at')
    
    # Group announcements by classroom
    classroom_announcements = {}
    for announcement in announcements:
        classroom = announcement.classroom_id
        if classroom not in classroom_announcements:
            classroom_announcements[classroom] = []
        classroom_announcements[classroom].append(announcement)
    
    if request.method == 'POST':
        announcement_id = request.POST.get('announcement_id')
        announcement = get_object_or_404(Announcements, announcement_id=announcement_id, faculty_id=request.user)
        
        try:
            announcement.delete()
            messages.success(request, 'Announcement deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting announcement: {str(e)}')
        
        return redirect('announcements_list')
    
    return render(request, 'faculty/announcements_list.html', {
        'classroom_announcements': classroom_announcements
    })




@login_required
def uni_notice_board_s(request):
    notices = Notices.objects.all().order_by('-posted_at')
    return render(request, 'student/uni_notice_board_s.html', {'notices': notices})

@login_required
def classroom_list_s(request):
    student = request.user
    enrolled_classrooms = Classroom_Students.objects.filter(student_id=student).select_related('classroom_id')
    classrooms = [cs.classroom_id for cs in enrolled_classrooms]
    return render(request, 'student/classroom_list_s.html', {'classrooms': classrooms})

@login_required
def classroom_announcements_s(request):
    student = request.user
    enrolled_classrooms = Classroom_Students.objects.filter(student_id=student).values_list('classroom_id', flat=True)
    announcements = Announcements.objects.filter(classroom_id__in=enrolled_classrooms).order_by('-posted_at')
    return render(request, 'student/classroom_announcements_s.html', {'announcements': announcements})

@login_required
def classroom_resources_s(request):
    student = request.user
    enrolled_classrooms = Classroom_Students.objects.filter(student_id=student).values_list('classroom_id', flat=True)
    resources = Resources.objects.filter(classroom_id__in=enrolled_classrooms).order_by('-uploaded_at')
    return render(request, 'student/classroom_resources_s.html', {'resources': resources})



@login_required
def add_classroom_request_s(request):
    if request.method == 'POST':
        classroom_id = request.POST.get('classroom_id')
        try:
            classroom = Classrooms.objects.get(classroom_id=classroom_id)
            if Classroom_Requests.objects.filter(classroom_id=classroom, student_id=request.user).exists():
                messages.error(request, 'You already requested to join this classroom.')
            else:
                Classroom_Requests.objects.create(
                    classroom_id=classroom,
                    student_id=request.user,
                    status='pending',
                    requested_at=timezone.now()
                )
                messages.success(request, 'Classroom join request submitted successfully.')
        except Classrooms.DoesNotExist:
            messages.error(request, 'Invalid classroom ID.')
        return redirect('add_classroom_request_s')

    classrooms = Classrooms.objects.all()
    requested_classrooms = Classroom_Requests.objects.filter(student_id=request.user).values_list('classroom_id__classroom_id', flat=True)
    
    context = {
        'classrooms': classrooms,
        'requested_classrooms': requested_classrooms,
    }
    return render(request, 'student/add_classroom_request_s.html', context)




from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Classrooms, Announcements, Resources

@login_required
def add_ann_res(request):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can manage classrooms.')
        return redirect('faculty_dashboard')
    
    # Fetch all classrooms created by the logged-in faculty
    classrooms = Classrooms.objects.filter(faculty_id=request.user).order_by('name')
    
    return render(request, 'faculty/add_ann_res.html', {
        'classrooms': classrooms
    })

@login_required
def ann_form(request, classroom_id):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can create announcements.')
        return redirect('faculty_dashboard')
    
    classroom = get_object_or_404(Classrooms, classroom_id=classroom_id)
    if classroom.faculty_id != request.user:
        messages.error(request, 'You do not have permission to post in this classroom.')
        return redirect('add_ann_res')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if not title or not content:
            messages.error(request, 'Please fill in all fields.')
            return render(request, 'faculty/ann_form.html', {'classroom': classroom})
        
        try:
            Announcements.objects.create(
                classroom_id=classroom,
                faculty_id=request.user,
                title=title,
                content=content
            )
            messages.success(request, 'Announcement created successfully.')
            return redirect('add_ann_res')  # Redirect back to the classroom list
        except Exception as e:
            messages.error(request, f'Error creating announcement: {str(e)}')
    
    return render(request, 'faculty/ann_form.html', {'classroom': classroom})

@login_required
def res_form(request, classroom_id):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can upload resources.')
        return redirect('faculty_dashboard')
    
    classroom = get_object_or_404(Classrooms, classroom_id=classroom_id)
    if classroom.faculty_id != request.user:
        messages.error(request, 'You do not have permission to upload resources to this classroom.')
        return redirect('add_ann_res')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        file_url = request.POST.get('file_url')
        description = request.POST.get('description')
        
        if not title or not file_url:
            messages.error(request, 'Please fill in the required fields.')
            return render(request, 'faculty/res_form.html', {'classroom': classroom})
        
        try:
            Resources.objects.create(
                classroom_id=classroom,
                faculty_id=request.user,
                title=title,
                file_url=file_url,
                description=description
            )
            messages.success(request, 'Resource uploaded successfully.')
            return redirect('resources_list')  # Redirect back to the classroom list
        except Exception as e:
            messages.error(request, f'Error uploading resource: {str(e)}')
    
    return render(request, 'faculty/res_form.html', {'classroom': classroom})
@login_required
def resources_list(request):
    if request.user.role != 'faculty':
        messages.error(request, 'Only faculty can view resources.')
        return redirect('faculty_dashboard')
    
    # Fetch all classrooms created by the logged-in faculty
    classrooms = Classrooms.objects.filter(faculty_id=request.user).order_by('name')
    
    # Dictionary to store resources for each classroom
    classroom_resources = {}
    
    for classroom in classrooms:
        # Fetch resources for this classroom where the faculty is the logged-in user
        resources = Resources.objects.filter(
            classroom_id=classroom,
            faculty_id=request.user
        ).order_by('-uploaded_at')
        classroom_resources[classroom] = resources
    
    return render(request, 'faculty/resources_list.html', {
        'classroom_resources': classroom_resources
    })