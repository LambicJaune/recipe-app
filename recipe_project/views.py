from django.shortcuts import render, redirect  
#Django authentication libraries           
from django.contrib.auth import authenticate, login, logout
#Django Form for authentication
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

# define a function view called signup_view that takes a request from user
def signup_view(request):
    """
    Handle user signup by processing the UserCreationForm.
    If the form is valid, create a new user (POST), log them in, and redirect to the recipes overview.
    Otherwise, display the signup form (GET).

    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The HTTP response with the signup form or a redirect.
    """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("recipes:recipes_overview")
    else:
        form = UserCreationForm()

    return render(request, "auth/signup.html", {"form": form})

#define a function view called login_view that takes a request from user
def login_view(request):
    """
    Handle user login by processing the AuthenticationForm.
    If the form is valid, authenticate and log in the user (POST), then redirect to the recipes overview.
    Otherwise, display the login form (GET) with any error messages.
    
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The HTTP response with the login form or a redirect.
    """
    #initialize:
    #error_message to None                                 
    error_message = None   
    #form object with username and password fields                             
    form = AuthenticationForm()                            

    #when user hits "login" button, then POST request is generated
    if request.method == 'POST':       
       #read the data sent by the form via POST request                   
       form =AuthenticationForm(data=request.POST)

       #check if form is valid
       if form.is_valid():                                
           username=form.cleaned_data.get('username')      #read username
           password = form.cleaned_data.get('password')    #read password

           #use Django authenticate function to validate the user
           user=authenticate(username=username, password=password)
           if user is not None:                    #if user is authenticated
          #then use pre-defined Django function to login
               login(request, user)                
               return redirect('recipes:recipes_overview') #& send the user to desired page
       else:                                               #in case of error
           error_message ='ooops.. something went wrong'   #print error message

    #prepare data to send from view to template
    context ={                                             
       'form': form,                                 #send the form data
       'error_message': error_message                     #and the error_message
 }
    #load the login page using "context" information
    return render(request, 'auth/login.html', context)     

#define a function view called logout_view that takes a request from user
def logout_view(request):  
    """
    Handle user logout by calling the logout function and redirecting to the login page.

    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: A redirect to the login page.
    """
    logout(request)             #pre-defined Django function to logout
    return redirect('login')    #after logging out go to login form