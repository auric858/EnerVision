# **⚡ EnerVision – Smart Energy Consumption Predictor**

EnerVision is an AI-powered web app that predicts hourly, daily, and monthly energy consumption based on key electrical and environmental parameters.
It also estimates cost and CO₂ emissions, providing an interactive dashboard and downloadable PDF reports.

# Features

**>** Predict Hourly, Daily, or Monthly energy usage

**>** Input real-time parameters (temperature, humidity, sub-meter readings, etc.)

**>** Calculate energy cost and carbon footprint

**>** Download PDF summary report

**>** Built using Streamlit, Random Forest, and TensorFlow ANN

# Tech Stack

Frontend: Streamlit
Backend: Python 3
Libraries: scikit-learn, TensorFlow, pandas, numpy, reportlab
Deployment: Streamlit Community Cloud

# How to Use

1) Select Hourly, Daily, or Monthly prediction tab.

2) Enter current readings (temperature, humidity, sub-meters, etc.).

3) Click Predict to see consumption, cost, and CO₂ output.

4) Download your PDF Summary Report.

#  Installation
## Clone this repository
git clone 

# Navigate into the folder
cd <repo-name>

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
