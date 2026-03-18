import os
import logging
from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.http import JsonResponse
from dotenv import load_dotenv

# Load environment variables (Make sure ADMIN_USERNAME & ADMIN_PASSWORD are in your .env)
load_dotenv()

# --- PUBLIC VIEWS ---

def index(request):
    return render(request, 'index.html')

def adminlogin(request):
    # 1. If already logged in, don't show the login page, go straight to library
    if request.session.get('is_admin_logged_in'):
        return redirect('libwebb:library')

    # 2. Handle the POST request (The actual login attempt)
    if request.method == "POST":
        ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
        ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
        
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            request.session['is_admin_logged_in'] = True
            return redirect('libwebb:library')
        else:
            return render(request, "adminlogin.html", {"error": "Invalid Username or Password"})

    # 3. Handle the GET request (Just showing the page)
    return render(request, "adminlogin.html")

def logout_view(request):
    if 'is_admin_logged_in' in request.session:
        del request.session['is_admin_logged_in']
    return redirect('libwebb:index')

# --- PROTECTED VIEWS (Admin Only) ---

def library(request):
    # Security Check: Kick out non-admins
    if not request.session.get('is_admin_logged_in'):
        return redirect('libwebb:adminlogin')

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()

    return render(request, "library.html", {"books": books})

def add_book(request):
    if not request.session.get('is_admin_logged_in'):
        return redirect('libwebb:adminlogin')

    if request.method == "POST":
        data = [
            request.POST.get('book_id'),
            request.POST.get('title'),
            request.POST.get('author'),
            request.POST.get('language'),
            request.POST.get('date_of_buy'),
            request.POST.get('category'),
            'Available', 
            request.POST.get('remarks')
        ]
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO books (book_id, title, author, language, date_of_buy, category, status, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, data)
        messages.success(request, "Book added successfully!")
        return redirect('libwebb:library')

def delete_book(request):
    if not request.session.get('is_admin_logged_in'):
        return redirect('libwebb:adminlogin')

    if request.method == "POST":
        book_id = request.POST.get('book_id')
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM books WHERE book_id = %s", [book_id])
        messages.warning(request, f"Book {book_id} deleted.")
        return redirect('libwebb:library')

def update_book(request):
    if not request.session.get('is_admin_logged_in'):
        return redirect('libwebb:adminlogin')

    if request.method == "POST":
        book_id = request.POST.get('book_id')
        title = request.POST.get('title')
        author = request.POST.get('author')
        language = request.POST.get('language')
        category = request.POST.get('category')
        date_of_buy = request.POST.get('date_of_buy')
        status = request.POST.get('status')
        # Logic: If status isn't Borrowed, clear the remarks
        remarks = request.POST.get('remarks') if status == 'Borrowed' else ""

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE books 
                SET title = %s, author = %s, language = %s, category = %s, date_of_buy = %s, status = %s, remarks = %s
                WHERE book_id = %s
            """, [title, author, language, category, date_of_buy, status, remarks, book_id])
        
        messages.success(request, f"Book {book_id} updated successfully!")
        return redirect('libwebb:library')

# --- API / HELPER VIEWS ---

def get_book_details(request):
    book_id = request.GET.get('book_id', None)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT title, author, language, category, date_of_buy, status, remarks 
                FROM books 
                WHERE book_id = %s
            """, [book_id])
            row = cursor.fetchone()

            if row:
                return JsonResponse({
                    'success': True,
                    'title': str(row[0] or ""),
                    'author': str(row[1] or ""),
                    'language': str(row[2] or ""),
                    'category': str(row[3] or ""),
                    'date': str(row[4]) if row[4] else "",
                    'status': str(row[5] or "Available"),
                    'remarks': str(row[6] or "")
                })
            return JsonResponse({'success': False, 'message': 'Book ID not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def get_all_book_titles(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT book_id, title FROM books")
            rows = cursor.fetchall()
            suggestions = [f"{row[0]} - {row[1]}" for row in rows]
            return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        return JsonResponse({'suggestions': []}, status=500)
    
def admindashboard(request):
    # Security check to make sure only logged-in admins see this
    if not request.session.get('is_admin_logged_in'):
        return redirect('libwebb:adminlogin')
    return render(request, 'admindashboard.html')