from functools import wraps
from datetime import date, datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Book, Member, Issue

# =========================
# INSTITUTE ADMIN SECURITY
# =========================

INSTITUTE_ADMIN_CODE = 'LIBRARY@2026'
# =========================
# ADMIN ACCESS PROTECTION
# =========================

def admin_required(view_function):

    @wraps(view_function)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect('admin_login')

        if not request.user.is_staff:

            messages.error(
                request,
                'You do not have admin access.'
            )

            return redirect('member_dashboard')

        return view_function(
            request,
            *args,
            **kwargs
        )

    return wrapper


# =========================
# HOME / ADMIN DASHBOARD
# =========================

@admin_required
def home(request):

    total_books = Book.objects.count()

    available_books = Book.objects.aggregate(
        total=Sum('available_quantity')
    )['total'] or 0

    total_members = Member.objects.count()

    issued_books = Issue.objects.filter(
        status='Issued'
    ).count()

    returned_books = Issue.objects.filter(
        status='Returned'
    ).count()

    total_fines = Issue.objects.aggregate(
        total=Sum('fine')
    )['total'] or 0

    return render(
        request,
        'home/home.html',
        {
            'total_books': total_books,
            'available_books': available_books,
            'total_members': total_members,
            'issued_books': issued_books,
            'returned_books': returned_books,
            'total_fines': total_fines,
        }
    )


# =========================
# LOGIN PAGE
# =========================

def login_page(request):

    return render(
        request,
        'home/login.html'
    )


# =========================
# BOOKS
# =========================

@admin_required
def books(request):

    all_books = Book.objects.all()

    return render(
        request,
        'home/books.html',
        {
            'books': all_books
        }
    )


# =========================
# BOOK DETAIL
# =========================

@admin_required
def book_detail(request, book_id):

    book = get_object_or_404(
        Book,
        id=book_id
    )

    return render(
        request,
        'home/book_detail.html',
        {
            'book': book
        }
    )


# =========================
# ADD BOOK
# =========================

@admin_required
def add_book(request):

    if request.method == 'POST':

        title = request.POST.get(
            'title',
            ''
        ).strip()

        author = request.POST.get(
            'author',
            ''
        ).strip()

        category = request.POST.get(
            'category',
            ''
        ).strip()

        isbn = request.POST.get(
            'isbn',
            ''
        ).strip()

        quantity_text = request.POST.get(
            'quantity',
            ''
        ).strip()

        published_date = request.POST.get(
            'published_date',
            ''
        ).strip()

        # Check required fields
        if not title or not author or not category or not isbn:

            messages.error(
                request,
                'Please fill in all required fields.'
            )

            return render(
                request,
                'home/book_form.html'
            )

        # Check quantity
        try:

            quantity = int(quantity_text)

        except ValueError:

            messages.error(
                request,
                'Quantity must be a valid number.'
            )

            return render(
                request,
                'home/book_form.html'
            )

        if quantity < 1:

            messages.error(
                request,
                'Quantity must be at least 1.'
            )

            return render(
                request,
                'home/book_form.html'
            )

        # Check duplicate ISBN
        if Book.objects.filter(
            isbn=isbn
        ).exists():

            messages.error(
                request,
                'A book with this ISBN already exists.'
            )

            return render(
                request,
                'home/book_form.html'
            )

        # Create book
        Book.objects.create(
            title=title,
            author=author,
            category=category,
            isbn=isbn,
            quantity=quantity,
            available_quantity=quantity,
            published_date=published_date
            if published_date else None
        )

        messages.success(
            request,
            'Book added successfully.'
        )

        return redirect('books')

    return render(
        request,
        'home/book_form.html'
    )


# =========================
# EDIT BOOK
# =========================

@admin_required
def edit_book(request, book_id):

    book = get_object_or_404(
        Book,
        id=book_id
    )

    if request.method == 'POST':

        title = request.POST.get(
            'title',
            ''
        ).strip()

        author = request.POST.get(
            'author',
            ''
        ).strip()

        category = request.POST.get(
            'category',
            ''
        ).strip()

        isbn = request.POST.get(
            'isbn',
            ''
        ).strip()

        quantity_text = request.POST.get(
            'quantity',
            ''
        ).strip()

        published_date = request.POST.get(
            'published_date',
            ''
        ).strip()

        # Check required fields
        if not title or not author or not category or not isbn:

            messages.error(
                request,
                'Please fill in all required fields.'
            )

            return render(
                request,
                'home/edit_book.html',
                {
                    'book': book
                }
            )

        # Check quantity
        try:

            new_quantity = int(quantity_text)

        except ValueError:

            messages.error(
                request,
                'Quantity must be a valid number.'
            )

            return render(
                request,
                'home/edit_book.html',
                {
                    'book': book
                }
            )

        if new_quantity < 1:

            messages.error(
                request,
                'Quantity must be at least 1.'
            )

            return render(
                request,
                'home/edit_book.html',
                {
                    'book': book
                }
            )

        # Check duplicate ISBN
        if Book.objects.filter(
            isbn=isbn
        ).exclude(
            id=book.id
        ).exists():

            messages.error(
                request,
                'Another book already uses this ISBN.'
            )

            return render(
                request,
                'home/edit_book.html',
                {
                    'book': book
                }
            )

        # Calculate currently issued copies
        issued_quantity = (
            book.quantity - book.available_quantity
        )

        # Quantity cannot be less than issued copies
        if new_quantity < issued_quantity:

            messages.error(
                request,
                f'Quantity cannot be less than {issued_quantity} '
                f'because {issued_quantity} copy/copies are currently issued.'
            )

            return render(
                request,
                'home/edit_book.html',
                {
                    'book': book
                }
            )

        # Update book details
        book.title = title
        book.author = author
        book.category = category
        book.isbn = isbn
        book.quantity = new_quantity

        # Recalculate available quantity
        book.available_quantity = (
            new_quantity - issued_quantity
        )

        # Update published date
        if published_date:

            book.published_date = published_date

        else:

            book.published_date = None

        book.save()

        messages.success(
            request,
            'Book updated successfully.'
        )

        return redirect('books')

    return render(
        request,
        'home/edit_book.html',
        {
            'book': book
        }
    )


# =========================
# DELETE BOOK
# =========================

@admin_required
def delete_book(request, book_id):

    book = get_object_or_404(
        Book,
        id=book_id
    )

    # Check whether any copies are currently issued
    active_issues = Issue.objects.filter(
        book=book,
        status='Issued'
    ).count()

    if active_issues > 0:

        messages.error(
            request,
            f'Cannot delete "{book.title}". '
            f'{active_issues} copy/copies are currently issued.'
        )

        return redirect('books')

    # Delete only after confirmation
    if request.method == 'POST':

        book.delete()

        messages.success(
            request,
            f'"{book.title}" was deleted successfully.'
        )

        return redirect('books')

    return render(
        request,
        'home/delete_book.html',
        {
            'book': book
        }
    )


# =========================
# MEMBERS
# =========================

@admin_required
def members(request):

    all_members = Member.objects.all()

    return render(
        request,
        'home/members.html',
        {
            'members': all_members
        }
    )


# =========================
# ADD MEMBER
# =========================

@admin_required
def add_member(request):

    if request.method == 'POST':

        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        membership_id = request.POST['membership_id']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check passwords
        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return render(
                request,
                'home/member_form.html'
            )

        # Check username
        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists.'
            )

            return render(
                request,
                'home/member_form.html'
            )

        # Check email
        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                'Email already registered.'
            )

            return render(
                request,
                'home/member_form.html'
            )

        # Check membership ID
        if Member.objects.filter(
            membership_id=membership_id
        ).exists():

            messages.error(
                request,
                'Membership ID already exists.'
            )

            return render(
                request,
                'home/member_form.html'
            )

        # Create Django login account
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create Member and connect it to User
        Member.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            membership_id=membership_id
        )

        messages.success(
            request,
            'Member and login account created successfully.'
        )

        return redirect('members')

    return render(
        request,
        'home/member_form.html'
    )


# =========================
# EDIT MEMBER
# =========================

@admin_required
def edit_member(request, member_id):

    member = get_object_or_404(
        Member,
        id=member_id
    )

    if request.method == 'POST':

        name = request.POST.get(
            'name',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        phone = request.POST.get(
            'phone',
            ''
        ).strip()

        membership_id = request.POST.get(
            'membership_id',
            ''
        ).strip()

        # Check required fields
        if not name or not email or not phone or not membership_id:

            messages.error(
                request,
                'Please fill in all member details.'
            )

            return render(
                request,
                'home/edit_member.html',
                {
                    'member': member
                }
            )

        # Check duplicate email
        if Member.objects.filter(
            email=email
        ).exclude(
            id=member.id
        ).exists():

            messages.error(
                request,
                'Another member already uses this email address.'
            )

            return render(
                request,
                'home/edit_member.html',
                {
                    'member': member
                }
            )

        # Check duplicate membership ID
        if Member.objects.filter(
            membership_id=membership_id
        ).exclude(
            id=member.id
        ).exists():

            messages.error(
                request,
                'Another member already uses this Membership ID.'
            )

            return render(
                request,
                'home/edit_member.html',
                {
                    'member': member
                }
            )

        # Update member
        member.name = name
        member.email = email
        member.phone = phone
        member.membership_id = membership_id

        member.save()

        # Update linked User email
        if member.user:

            member.user.email = email

            member.user.save()

        messages.success(
            request,
            'Member updated successfully.'
        )

        return redirect('members')

    return render(
        request,
        'home/edit_member.html',
        {
            'member': member
        }
    )


# =========================
# DELETE MEMBER
# =========================

@admin_required
def delete_member(request, member_id):

    member = get_object_or_404(
        Member,
        id=member_id
    )

    # Check if member has any currently issued books
    active_issues = Issue.objects.filter(
        member=member,
        status='Issued'
    ).count()

    if active_issues > 0:

        messages.error(
            request,
            f'{member.name} cannot be deleted because they have '
            f'{active_issues} book(s) currently issued.'
        )

        return redirect('members')

    # Delete member only after confirmation
    if request.method == 'POST':

        # Delete linked User account also
        if member.user:
            member.user.delete()

        member.delete()

        messages.success(
            request,
            f'Member "{member.name}" deleted successfully.'
        )

        return redirect('members')

    return render(
        request,
        'home/delete_member.html',
        {
            'member': member
        }
    )


# =========================
# ADMIN MANAGEMENT
# =========================

@admin_required
def admins(request):

    all_admins = User.objects.filter(
        is_staff=True
    )

    return render(
        request,
        'home/admins.html',
        {
            'admins': all_admins
        }
    )


# =========================
# ADMIN REGISTRATION
# =========================

# =========================
# ADMIN REGISTRATION
# =========================

def add_admin(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        confirm_password = request.POST.get(
            'confirm_password',
            ''
        )

        admin_code = request.POST.get(
            'admin_code',
            ''
        ).strip()

        # Check required fields
        if not username or not email or not password or not confirm_password or not admin_code:

            messages.error(
                request,
                'Please fill in all fields.'
            )

            return render(
                request,
                'home/admin_form.html'
            )

        # Check institute admin code
        if admin_code != INSTITUTE_ADMIN_CODE:

            messages.error(
                request,
                'Invalid Institute Admin Code.'
            )

            return render(
                request,
                'home/admin_form.html'
            )

        # Check passwords
        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return render(
                request,
                'home/admin_form.html'
            )

        # Check username
        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists.'
            )

            return render(
                request,
                'home/admin_form.html'
            )

        # Check email
        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                'Email already registered.'
            )

            return render(
                request,
                'home/admin_form.html'
            )

        # Create admin account
        admin_user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Give admin access
        admin_user.is_staff = True

        admin_user.save()

        messages.success(
            request,
            'Admin account created successfully. Please login.'
        )

        return redirect('admin_login')

    return render(
        request,
        'home/admin_form.html'
    )


# =========================
# ISSUE BOOK
# =========================

@admin_required
def issue_book(request):

    books = Book.objects.filter(
        available_quantity__gt=0
    )

    members = Member.objects.all()

    if request.method == 'POST':

        book_id = request.POST.get('book')
        member_id = request.POST.get('member')
        due_date = request.POST.get('due_date')

        # Check all fields
        if not book_id or not member_id or not due_date:

            messages.error(
                request,
                'Please fill in all fields.'
            )

            return render(
                request,
                'home/issue_book.html',
                {
                    'books': books,
                    'members': members
                }
            )

        # Get selected book
        book = get_object_or_404(
            Book,
            id=book_id
        )

        # Get selected member
        member = get_object_or_404(
            Member,
            id=member_id
        )

        # Check book availability
        if book.available_quantity <= 0:

            messages.error(
                request,
                'This book is currently unavailable.'
            )

            return redirect('issue_book')

        # Check due date
        try:

            due_date_obj = datetime.strptime(
                due_date,
                '%Y-%m-%d'
            ).date()

        except ValueError:

            messages.error(
                request,
                'Please enter a valid due date.'
            )

            return redirect('issue_book')

        # Due date cannot be in the past
        if due_date_obj < date.today():

            messages.error(
                request,
                'Due date cannot be in the past.'
            )

            return redirect('issue_book')

        # Check if same member already has this book
        already_issued = Issue.objects.filter(
            book=book,
            member=member,
            status='Issued'
        ).exists()

        if already_issued:

            messages.error(
                request,
                'This member already has this book issued.'
            )

            return redirect('issue_book')

        # Create issue record
        Issue.objects.create(
            book=book,
            member=member,
            due_date=due_date_obj
        )

        # Reduce available quantity
        book.available_quantity -= 1

        book.save()

        messages.success(
            request,
            f'"{book.title}" issued successfully.'
        )

        return redirect('issued_books')

    return render(
        request,
        'home/issue_book.html',
        {
            'books': books,
            'members': members
        }
    )


# =========================
# ISSUED BOOKS
# =========================

@admin_required
def issued_books(request):

    issues = Issue.objects.all().order_by(
        '-issue_date'
    )

    return render(
        request,
        'home/issued_books.html',
        {
            'issues': issues
        }
    )


# =========================
# RETURN BOOK
# =========================

@admin_required
def return_book(request, issue_id):

    issue = get_object_or_404(
        Issue,
        id=issue_id
    )

    # Prevent returning an already returned book
    if issue.status == 'Returned':

        messages.warning(
            request,
            'This book has already been returned.'
        )

        return redirect('issued_books')

    if request.method == 'POST':

        # Set today's date
        issue.return_date = date.today()

        # Calculate fine
        if issue.return_date > issue.due_date:

            late_days = (
                issue.return_date - issue.due_date
            ).days

            # ₹10 fine per late day
            issue.fine = late_days * 10

        else:

            issue.fine = 0

        # Change status
        issue.status = 'Returned'

        issue.save()

        # Increase available quantity
        book = issue.book

        book.available_quantity += 1

        # Available quantity cannot exceed total quantity
        if book.available_quantity > book.quantity:

            book.available_quantity = book.quantity

        book.save()

        messages.success(
            request,
            f'"{book.title}" has been returned successfully.'
        )

        return redirect('issued_books')

    return render(
        request,
        'home/return_book.html',
        {
            'issue': issue
        }
    )


# =========================
# ADMIN LOGIN
# =========================

def admin_login(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if user.is_staff:

                login(request, user)

                return redirect('home')

            else:

                messages.error(
                    request,
                    'You do not have admin access.'
                )

        else:

            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(
        request,
        'home/admin_login.html'
    )


# =========================
# MEMBER LOGIN
# =========================

def member_login(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            if hasattr(user, 'member'):

                login(request, user)

                return redirect('member_dashboard')

            else:

                messages.error(
                    request,
                    'This account is not registered as a member.'
                )

        else:

            messages.error(
                request,
                'Invalid username or password.'
            )

    return render(
        request,
        'home/member_login.html'
    )


# =========================
# MEMBER REGISTRATION
# =========================

def member_register(request):

    if request.method == 'POST':

        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        membership_id = request.POST['membership_id']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check passwords
        if password != confirm_password:

            messages.error(
                request,
                'Passwords do not match.'
            )

            return render(
                request,
                'home/member_register.html'
            )

        # Check username
        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'Username already exists.'
            )

            return render(
                request,
                'home/member_register.html'
            )

        # Check email
        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                'Email already registered.'
            )

            return render(
                request,
                'home/member_register.html'
            )

        # Check membership ID
        if Member.objects.filter(
            membership_id=membership_id
        ).exists():

            messages.error(
                request,
                'Membership ID already exists.'
            )

            return render(
                request,
                'home/member_register.html'
            )

        # Create Django User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create Member
        Member.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            membership_id=membership_id
        )

        messages.success(
            request,
            'Registration successful. Please login.'
        )

        return redirect('member_login')

    return render(
        request,
        'home/member_register.html'
    )


# =========================
# MEMBER DASHBOARD
# =========================

def member_dashboard(request):

    if not request.user.is_authenticated:

        return redirect('member_login')

    if not hasattr(request.user, 'member'):

        return redirect('login')

    member = request.user.member

    my_issues = Issue.objects.filter(
        member=member
    ).order_by(
        '-issue_date'
    )

    available_books = Book.objects.filter(
        available_quantity__gt=0
    )

    return render(
        request,
        'home/member_dashboard.html',
        {
            'member': member,
            'my_issues': my_issues,
            'available_books': available_books,
        }
    )


# =========================
# LOGOUT
# =========================

def user_logout(request):

    logout(request)

    return redirect('login')