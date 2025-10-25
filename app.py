import streamlit as st
import numpy as np

import pickle
from io import BytesIO
from streamlit_option_menu import option_menu
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from tensorflow.keras.models import load_model

with open("hourly_energy_prediction_france.pkl","rb") as f:
    model_hourly=pickle.load(f)

model_daily= load_model("daily_energy_prediction_france.keras")

with open("x_scaler.pkl","rb") as f2:
    scaler_x=pickle.load(f2)
with open("y_scaler.pkl","rb") as f3:
    scaler_y=pickle.load(f3)
with open("monthly_energy_prediction_france.pkl","rb") as f4:
    model_monthly=pickle.load(f4)

if "hourly_result" not in st.session_state:
    st.session_state.hourly_result = None
if "daily_result" not in st.session_state:
    st.session_state.daily_result = None
if "monthly_result" not in st.session_state:
    st.session_state.monthly_result = None

st.set_page_config(page_title="EnerVision", layout="centered")
# sidebar for navigation
with st.sidebar:
    selected = option_menu(
        menu_title="Energy Consumption Dashboard",      # title of the sidebar
        options=[
            "Hourly Prediction",
            "Daily Prediction",
            "Monthly Prediction",
            "Download Report"

        ],
        icons=["clock", "calendar","calendar3","file-earmark-pdf"],  # bootstrap icons
        menu_icon="cast",   # icon for the whole menu
        default_index=0
    )
#HOURLY PRED PAGE
if selected == "Hourly Prediction":
    st.title("Hourly Energy Prediction ⏰ ")
    sub_meter_1=st.number_input("Sub Meter 1(kitchen) Reading")
    sub_meter_2 = st.number_input("Sub Meter 2(laundry) Reading")
    sub_meter_3 = st.number_input("Sub Meter 3(bedroom) Reading")
    hour = st.number_input("Hour (0-23)", min_value=0, max_value=23)
    power_factor = st.number_input("Power Factor", min_value=0.0, max_value=1.0, value=0.9)
    voltage = st.number_input("Voltage", min_value=180.0, max_value=260.0, value=230.0)
    temp = st.number_input("Temperature (°C)", value=4.20)

    # creating a button for Prediction
    if st.button("Predict"):
        user_input =[sub_meter_1,sub_meter_2,sub_meter_3,hour,power_factor,voltage,temp]
        user_input = [float(x) for x in user_input]
        pred=model_hourly.predict([user_input])
        hourly_pred=pred[0]
        # Model prediction
        st.subheader("Predicted Hourly Consumption")
        st.success(f"⚡ {hourly_pred:.2f} kWh")
        # France avg ~0.05 kg CO₂ / kWh
        emission_factor = 0.05
        co2_kg = hourly_pred * emission_factor
        st.info(f"🌱 Estimated CO₂ emissions: **{co2_kg:.3f} kg CO₂**")
        # hourly electricity cost
        # tariff ~0.21 €/kWh
        price_per_kwh = 0.21
        cost_eur = hourly_pred * price_per_kwh
        st.info(f"💰 Estimated hourly cost: **€{cost_eur:.2f}**")
        # Peak usage hours (simple indicator)
        # Typical French residential peaks: 18–21h
        w=""
        if 18 <= hour <= 21:
            w="🔺 This hour is a **typical national peak period** (18–21h)."
            st.warning(w)
        elif hourly_pred > 2.5:
            w="🔺 Your predicted usage is high compared to normal baseline."
            st.warning(w)

        st.session_state.hourly_result = {
                "kwh": hourly_pred,
                "co2": co2_kg,
                "cost": cost_eur,
                "warning":w
        }


if selected =="Daily Prediction":
    st.title("Daily Energy Prediction 🗓 ")
    sub_meter_1 = st.number_input("Sub Meter 1(kitchen) Reading")
    sub_meter_2 = st.number_input("Sub Meter 2(laundry) Reading")
    sub_meter_3 = st.number_input("Sub Meter 3(bedroom) Reading")
    power_factor = st.number_input("Power Factor", min_value=0.0, max_value=1.0, value=0.9)
    is_holiday = st.selectbox(
        "Is today a holiday?",
        ("No", "Yes")
    )
    is_holiday = 1 if is_holiday == "Yes" else 0
    is_weekend = st.selectbox(
        "Is today a weekend?",
        ("No", "Yes")
    )
    is_weekend = 1 if is_weekend == "Yes" else 0
    temp = st.number_input("Temperature (°C)", value=5.8)
    month = st.number_input("Month (1-12)", value=11)
    if st.button("Predict"):
        month_sin=np.sin(2*np.pi*month/12)
        month_cos=np.cos(2*np.pi*month/12)
        numerical_cols = np.array([[sub_meter_1, sub_meter_2,sub_meter_3,power_factor,temp,month_sin,month_cos]])
        binary_cols = np.array([[is_weekend, is_holiday]])
        user_input_scaled=scaler_x.transform(numerical_cols)
        user_input=np.hstack([user_input_scaled,binary_cols])

        prediction = model_daily.predict([user_input])
        daily_prediction=scaler_y.inverse_transform(prediction)
        daily_prediction=daily_prediction[0][0]
        # Model prediction
        st.subheader("Predicted Daily Consumption")
        st.success(f"⚡ {daily_prediction:.2f} kWh")
        # France avg ~0.05 kg CO₂ / kWh
        emission_factor = 0.05
        co2_kg = daily_prediction * emission_factor
        st.info(f"🌱 Estimated CO₂ emissions: **{co2_kg:.3f} kg CO₂**")
        # daily electricity cost
        # tariff ~0.21 €/kWh
        price_per_kwh = 0.21
        cost_eur =daily_prediction * price_per_kwh
        st.info(f"💰 Estimated daily cost: **€{cost_eur:.2f}**")
        st.session_state.daily_result = {
            "kwh": daily_prediction,
            "co2": co2_kg,
            "cost": cost_eur

        }
if selected == "Monthly Prediction":
    st.title("Monthly Energy Prediction ")
    sub_meter_1=st.number_input("Sub Meter 1(kitchen) Reading")
    sub_meter_2 = st.number_input("Sub Meter 2(laundry) Reading")
    sub_meter_3 = st.number_input("Sub Meter 3(bedroom) Reading")
    power_factor = st.number_input("Power Factor", min_value=0.0, max_value=1.0, value=0.99)
    temp = st.number_input("Temperature (°C)", value=4.20)
    month = st.number_input("Month (1-12)", value=11)


    # creating a button for Prediction
    if st.button("Predict"):
        user_input =[sub_meter_1,sub_meter_2,sub_meter_3,power_factor,temp,month]
        user_input = [float(x) for x in user_input]
        pred=model_monthly.predict([user_input])
        monthly_pred=pred[0]
        # Model prediction
        st.subheader("Predicted Monthly Consumption")
        st.success(f"⚡ {monthly_pred:.2f} kWh")
        # France avg ~0.05 kg CO₂ / kWh
        emission_factor = 0.05
        co2_kg = monthly_pred * emission_factor
        st.info(f"🌱 Estimated CO₂ emissions: **{co2_kg:.3f} kg CO₂**")
        # hourly electricity cost
        # tariff ~0.21 €/kWh
        price_per_kwh = 0.21
        cost_eur = monthly_pred * price_per_kwh
        st.info(f"💰 Estimated Monthly cost: **€{cost_eur:.2f}**")
        st.session_state.monthly_result = {
            "kwh": monthly_pred,
            "co2": co2_kg,
            "cost": cost_eur

        }
if selected == "Download Report":
    st.title("📄 Download Full Energy Report")
    if (st.session_state.hourly_result and st.session_state.daily_result and st.session_state.monthly_result):
        if st.button("Generate PDF Report"):
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []
            elements.append(Paragraph("EnerVision: Energy Usage Report", styles['Title']))
            elements.append(Spacer(1, 12))
            def add_section(title, data):
                elements.append(Paragraph(f"<b>{title}</b>", styles['Heading2']))
                if title=="Hourly Prediction" and data["warning"]!="":
                    elements.append(Paragraph(f"Consumption: {data['kwh']:.2f} kWh<br/>"
                                              f"CO_2 Emissions: {data['co2']:.3f} kg<br/>"
                                              f"Estimated Cost: €{data['cost']:.2f}<br/>"
                                              f"{data["warning"]}", styles['Normal']))
                    elements.append(Spacer(1, 12))
                else:
                    elements.append(Paragraph(f"Consumption: {data['kwh']:.2f} kWh<br/>"
                                              f"CO_2 Emissions: {data['co2']:.3f} kg<br/>"
                                              f"Estimated Cost: €{data['cost']:.2f}"
                                              , styles['Normal']))
                    elements.append(Spacer(1, 12))



            add_section("Hourly Prediction", st.session_state.hourly_result)
            add_section("Daily Prediction", st.session_state.daily_result)
            add_section("Monthly Prediction", st.session_state.monthly_result)

            doc.build(elements)
            buffer.seek(0)

            st.download_button(label="⬇️ Download Report as PDF",
                    data=buffer,
                    file_name="EnerVision_Report.pdf",
                    mime="application/pdf"
                )
    else:
        st.warning("⚠️ Please complete all three predictions before generating the report.")
