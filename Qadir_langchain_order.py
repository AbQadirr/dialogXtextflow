import streamlit as st
import firebase_admin
from mcode import main_page
from firebase_admin import credentials
from firebase_admin import auth
 

    # If not initialized, initialize it with a unique app name
if not firebase_admin._apps:    
    cred = credentials.Certificate('dialogtextflow-a98bd48defb4.json')
    firebase_admin.initialize_app(cred)
    # auth = firebase_admin.auth()


# if 'user_authenticated' not in st.session_state:
#     st.session_state.user_authenticated = False
        
        
def app():
    
    
# Usernm = []
    # st.title('Welcome to :violet[Pondering] :sunglasses:')

    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''



    def f(): 
        try:
            user = auth.get_user_by_email(email)
            print(user.uid)
            st.session_state.username = user.uid
            st.session_state.useremail = user.email
            
            global Usernm
            Usernm=(user.uid)
            
            st.session_state.signedout = True
            st.session_state.signout = True    
  
            
        except: 
            st.warning('Login Failed')

    def t():
        st.session_state.signout = False
        st.session_state.signedout = False   
        st.session_state.username = ''


        
    
        
    if "signedout"  not in st.session_state:
        st.session_state["signedout"] = False
    if 'signout' not in st.session_state:
        st.session_state['signout'] = False    
        

        
    
    if  not st.session_state["signedout"]: # only show if the state is False, hence the button has never been clicked
        choice = st.selectbox('Login/Signup',['Login','Sign up'])
        email = st.text_input('Email Address')
        password = st.text_input('Password',type='password')
        

        
        if choice == 'Sign up':
            username = st.text_input("Enter  your unique username")
            
            if st.button('Create my account'):
                user = auth.create_user(email = email, password = password,uid=username)
                
                st.success('Account created successfully!')
                st.markdown('Please Login using your email and password')
                st.balloons()
        else:
            # st.button('Login', on_click=f)          
            st.button('Login', on_click=f)
            # main_page()
            
            
            
    if st.session_state.signout:                
        main_page()

       
        
        # st.sidebar.button('Sign out', on_click=t, key='t')
        
        # # var logoutButton = document.createElement('button');
 
        
    
                
    

                            
    def ap():
        st.write('Posts')
        
app()
