from django.shortcuts import render,redirect
from django.db import connection
from django.contrib import messages


def index(request):
    return render(request, 'index.html')

def admindashboard(request):
    return render(request, 'admindashboard.html')

def adminlogin(request):
    return render(request, 'adminlogin.html')

ADMIN_USERNAME = "athul007"
ADMIN_PASSWORD = "athul@9841"

def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect('libwebb:library')
        else:
            return render(request, "adminlogin.html", {"error": "Invalid Username or Password"})

    return render(request, "adminlogin.html")

from django.db import connection

def add_book(request):
    if request.method == "POST":
        data = [
            request.POST.get('book_id'),
            request.POST.get('title'),
            request.POST.get('author'),
            request.POST.get('language'),
            request.POST.get('date_of_buy'),
            request.POST.get('category'),
            'Available', # Default status for new books
            request.POST.get('remarks')
        ]
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO books (book_id, title, author, language, date_of_buy, category, status, remarks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, data)
        return redirect('library') # Go back to dashboard to see the new book

def delete_book(request):
    if request.method == "POST":
        book_id = request.POST.get('book_id')
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM books WHERE book_id = %s", [book_id])
        return redirect('libwebb:library')

def logout_view(request):
    # Since you aren't using Django Auth, just redirect to login
    return redirect('adminlogin')

def library(request):

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM books")
        books = cursor.fetchall()

    return render(request, "library.html", {"books": books})

from django.http import JsonResponse

from django.http import JsonResponse
import logging

def get_book_details(request):
    book_id = request.GET.get('book_id', None)
    try:
        # Using a dictionary cursor so we fetch by name, not number
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT title, author, language, category, date_of_buy, status, remarks 
                FROM books 
                WHERE book_id = %s
            """, [book_id])
            
            row = cursor.fetchone()
            
            # Debugging: This will print to your terminal so you can see the data
            print(f"DEBUG: Found row: {row}")

            if row:
                # We map based on the EXACT order in the SELECT above
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
        print(f"Database Error: {e}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    

def update_book(request):
    if request.method == "POST":
        book_id = request.POST.get('book_id')
        title = request.POST.get('title')
        author = request.POST.get('author')
        language = request.POST.get('language')
        category = request.POST.get('category')
        date_of_buy = request.POST.get('date_of_buy')
        status = request.POST.get('status')
        remarks = request.POST.get('remarks') if status == 'Borrowed' else ""

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE books 
                SET title = %s, author = %s, language = %s, category = %s, date_of_buy = %s, status = %s, remarks = %s
                WHERE book_id = %s
            """, [title, author, language, category, date_of_buy, status, remarks, book_id])
        
        messages.success(request, f"Book {book_id} updated successfully!")
        return redirect('libwebb:library')
    
from django.http import JsonResponse
from django.db import connection

def get_all_book_titles(request):
    try:
        with connection.cursor() as cursor:
            # Fetching ID and Title for the suggestion list
            cursor.execute("SELECT book_id, title FROM books")
            rows = cursor.fetchall()
            # Format: "#101 - Harry Potter"
            suggestions = [f"{row[0]} - {row[1]}" for row in rows]
            return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        return JsonResponse({'suggestions': []}, status=500)
    
import os
print(f"DEBUG: Looking for templates in: {os.path.join(os.getcwd(), 'templates')}")