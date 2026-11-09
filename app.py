import streamlit as st
import sqlite3
import pandas as pd
import uuid
from datetime import date

# ================= CONFIG =================
st.set_page_config(
    page_title="Moon Light Saloon",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= DATABASE =================
conn = sqlite3.connect(
    "taj_parlor.db",
    check_same_thread=False
)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    service TEXT,
    barber TEXT,
    booking_date TEXT,
    booking_time TEXT,
    status TEXT
)
""")
conn.commit()

# ================= DESIGN =================
st.markdown("""
<style>
.stApp {
    background: #101010;
    color: white;
}
h1, h2, h3, p, label {
    color: white !important;
}
.hero {
    text-align: center;
    padding: 30px 10px;
    background: linear-gradient(135deg,#171717,#302515);
    border: 1px solid #b89550;
    border-radius: 18px;
    margin-bottom: 20px;
}
.gold {
    color: #d6b66c !important;
}
div.stButton > button {
    background: #c5a45e;
    color: black;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    min-height: 45px;
}
div.stButton > button:hover {
    background: #e4ca8a;
    color: black;
}
div[data-testid="stForm"] {
    border: 1px solid #a78a4b;
    border-radius: 15px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="hero">
    <h1 class="gold">✂️ MOON LIGHT SALOON</h1>
    <p>STYLE • CLASS • CONFIDENCE</p>
    <p>Premium Grooming & Online Appointment</p>
</div>
""", unsafe_allow_html=True)

# ================= NAVIGATION =================
tab1, tab2, tab3 = st.tabs([
    "📅 Book Appointment",
    "🔎 Check Booking",
    "🛠️ Admin Dashboard"
])

# ================= SERVICES =================
SERVICES = [
    "Hair Cutting",
    "Beard Trimming",
    "Hair Spa",
    "Facial",
    "Massage",
    "Hair Color",
    "Premium Grooming"
]

BARBERS = [
    "Any Available",
    "Junaid",
    "Mazhar"
]

# ================= CUSTOMER BOOKING =================
with tab1:

    st.subheader("✂️ Book Your Appointment")

    with st.form("customer_booking"):

        name = st.text_input(
            "Customer Name",
            placeholder="Enter your full name"
        )

        service = st.selectbox(
            "Choose Service",
            SERVICES
        )

        barber = st.selectbox(
            "Choose Barber",
            BARBERS
        )

        booking_date = st.date_input(
            "Appointment Date",
            min_value=date.today()
        )

        booking_time = st.time_input(
            "Appointment Time"
        )

        submitted = st.form_submit_button(
            "CONFIRM BOOKING REQUEST",
            use_container_width=True
        )

    if submitted:

        if not name.strip():
            st.error("Please enter your name.")

        else:
            cursor.execute("""
                INSERT INTO bookings
                (customer_name, service, barber,
                booking_date, booking_time, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name.strip(),
                service,
                barber,
                str(booking_date),
                str(booking_time),
                "Pending"
            ))

            booking_id = cursor.lastrowid
            conn.commit()

            st.toast("Appointment received!", icon="🔔")

            st.success("🎉 Booking request submitted!")

            st.markdown(f"""
            ### Booking Details

            **Booking ID:** #{booking_id}

            **Name:** {name}

            **Service:** {service}

            **Barber:** {barber}

            **Date:** {booking_date}

            **Time:** {booking_time}

            **Status:** ⏳ Pending Approval
            """)

            st.info(
                "Please save your Booking ID to check your appointment."
            )

            st.balloons()

# ================= CHECK BOOKING =================
with tab2:

    st.subheader("🔔 Track Your Appointment")

    check_id = st.number_input(
        "Enter Booking ID",
        min_value=1,
        step=1,
        value=1
    )

    if st.button("CHECK STATUS", key="check_status"):

        cursor.execute("""
            SELECT * FROM bookings WHERE id=?
        """, (check_id,))

        booking = cursor.fetchone()

        if booking:

            st.write(f"Customer: **{booking[1]}**")
            st.write(f"Service: **{booking[2]}**")
            st.write(f"Barber: **{booking[3]}**")
            st.write(f"Date: **{booking[4]}**")
            st.write(f"Time: **{booking[5]}**")

            if booking[6] == "Confirmed":
                st.success("✅ Your appointment is CONFIRMED!")

            elif booking[6] == "Rejected":
                st.error("❌ Your appointment has been rejected.")

            else:
                st.warning("⏳ Your appointment is pending approval.")

        else:
            st.error("Booking ID not found.")

# ================= ADMIN DASHBOARD =================
with tab3:

    st.subheader("🛠️ Admin Dashboard")

    # Change password in Streamlit secrets
    admin_password = st.secrets.get(
        "ADMIN_PASSWORD", "Moonlight123"
    )

    password = st.text_input(
        "Admin Password",
        type="password"
    )

    if password == admin_password:

        st.success("Admin Login Successful!")

        df = pd.read_sql_query(
            "SELECT * FROM bookings ORDER BY id DESC",
            conn
        )

        total = len(df)
        pending = len(df[df["status"] == "Pending"])
        confirmed = len(df[df["status"] == "Confirmed"])
        rejected = len(df[df["status"] == "Rejected"])

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        col1.metric("Total Bookings", total)
        col2.metric("Pending", pending)
        col3.metric("Confirmed", confirmed)
        col4.metric("Rejected", rejected)

        st.markdown("---")

        st.subheader("All Appointments")

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        st.subheader("Update Appointment")

        booking_id = st.number_input(
            "Booking ID",
            min_value=1,
            step=1,
            key="admin_booking_id"
        )

        new_status = st.selectbox(
            "Select Status",
            ["Confirmed", "Rejected", "Pending"]
        )

        if st.button("UPDATE BOOKING"):

            cursor.execute(
                "SELECT id FROM bookings WHERE id=?",
                (booking_id,)
            )

            exists = cursor.fetchone()

            if exists:

                cursor.execute("""
                    UPDATE bookings
                    SET status=?
                    WHERE id=?
                """, (new_status, booking_id))

                conn.commit()

                st.success(
                    f"Booking #{booking_id} updated to {new_status}."
                )

                st.toast("Booking updated!", icon="🔔")

                st.rerun()

            else:
                st.error("Invalid Booking ID.")

    elif password:
        st.error("Incorrect password.")

    else:
        st.info("Please enter admin password.")

# ================= FOOTER =================
st.markdown("---")

st.markdown("""
<div style="text-align:center; padding:15px;">
    <h3 style="color:#d6b66c;">MOON LIGHT SALOON ✂️</h3>
    <p>Thank you for choosing us!</p>
    <p>© 2026 Moon Light Saloon</p>
</div>
""", unsafe_allow_html=True)

conn.close()