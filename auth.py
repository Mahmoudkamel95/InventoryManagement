import streamlit as st

USERNAME = "admin"
PASSWORD = "123456"

def check_login():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:

        st.title("🔐 تسجيل الدخول")

        username = st.text_input("اسم المستخدم")
        password = st.text_input(
            "كلمة المرور",
            type="password"
        )

        if st.button("دخول"):

            if (
                username == USERNAME
                and
                password == PASSWORD
            ):
                st.session_state.logged_in = True
                st.rerun()

            else:
                st.error("بيانات الدخول غير صحيحة")

        st.stop()
        
        
def show_logo():
    st.sidebar.image(
        r"C:\Users\WIN 10\Desktop\Inventory_System\Annotation 2026-03-11 213816.png",
        use_container_width=True
    )
    st.sidebar.markdown("---") 
    

    st.sidebar.markdown(
        """
        <div style='text-align:center'>
            <b>Developed By</b><br><br>
            Dr. Mahmoud Kamel<br>
            Pharmacist & Data Analyst
        </div>
        """,
        unsafe_allow_html=True
    )       