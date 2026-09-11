from django.contrib import admin
from django.urls import path
from home import views


urlpatterns = [

    # =========================
    # DJANGO ADMIN
    # =========================

    path(
        'admin/',
        admin.site.urls
    ),


    # =========================
    # HOME
    # =========================

    path(
        '',
        views.home,
        name='home'
    ),


    # =========================
    # BOOKS
    # =========================

    path(
        'books/',
        views.books,
        name='books'
    ),

    path(
        'book/<int:book_id>/',
        views.book_detail,
        name='book_detail'
    ),

    path(
        'add-book/',
        views.add_book,
        name='add_book'
    ),

    path(
        'edit-book/<int:book_id>/',
        views.edit_book,
        name='edit_book'
    ),

    path(
        'delete-book/<int:book_id>/',
        views.delete_book,
        name='delete_book'
    ),


    # =========================
    # MEMBERS
    # =========================

    path(
        'members/',
        views.members,
        name='members'
    ),

    path(
        'add-member/',
        views.add_member,
        name='add_member'
    ),

    path(
        'edit-member/<int:member_id>/',
        views.edit_member,
        name='edit_member'
    ),

    path(
        'delete-member/<int:member_id>/',
        views.delete_member,
        name='delete_member'
    ),


    # =========================
    # ADMIN MANAGEMENT
    # =========================

    path(
        'admins/',
        views.admins,
        name='admins'
    ),

    path(
        'add-admin/',
        views.add_admin,
        name='add_admin'
    ),


    # =========================
    # ISSUE BOOK
    # =========================

    path(
        'issue-book/',
        views.issue_book,
        name='issue_book'
    ),


    # =========================
    # ISSUED BOOKS
    # =========================

    path(
        'issued-books/',
        views.issued_books,
        name='issued_books'
    ),


    # =========================
    # RETURN BOOK
    # =========================

    path(
        'return-book/<int:issue_id>/',
        views.return_book,
        name='return_book'
    ),


    # =========================
    # LOGIN
    # =========================

    path(
        'login/',
        views.login_page,
        name='login'
    ),

    path(
        'admin-login/',
        views.admin_login,
        name='admin_login'
    ),

    path(
        'member-login/',
        views.member_login,
        name='member_login'
    ),


    # =========================
    # MEMBER REGISTRATION
    # =========================

    path(
        'member-register/',
        views.member_register,
        name='member_register'
    ),


    # =========================
    # MEMBER DASHBOARD
    # =========================

    path(
        'member-dashboard/',
        views.member_dashboard,
        name='member_dashboard'
    ),


    # =========================
    # LOGOUT
    # =========================

    path(
        'logout/',
        views.user_logout,
        name='logout'
    ),
    path(
    'add-admin/',
    views.add_admin,
    name='add_admin'
),

]