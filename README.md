# Smart Energy Consumption Controller

A Mamdani fuzzy logic system that determines the optimal energy usage level from electricity price, battery state, and solar production.

## Live Demo

- Live Streamlit app: add your deployed Streamlit URL here.
- Local app: run `./run_app.sh`

This is a Streamlit application. For the main app to show directly online, deploy it on Streamlit Community Cloud or another host that supports long-running Streamlit apps.

## Screenshots

Add dashboard screenshots in `assets/screenshots/` and reference them here.

```md
![Dashboard](assets/screenshots/dashboard.png)
![Active Rules](assets/screenshots/active-rules.png)
```

## What This Project Does

This system acts as a smart energy controller for a home or microgrid. Given three inputs, it uses fuzzy logic to decide how aggressively the system should consume energy.

| Input | Range | Description |
|---|---:|---|
| Electricity Price | 0-100 cents/kWh | Current grid purchase price |
| Battery Level | 0-100% | State of charge of battery storage |
| Solar Production | 0-100% | Solar panel output as percentage of peak capacity |

| Output | Range | Meaning |
|---|---:|---|
| Energy Usage Level | 0-100% | How much energy the system should consume |

The system uses 20 fuzzy IF-THEN rules, Mamdani inference, and centroid defuzzification.

## Quick Start

Run the app with one command:

```bash
./run_app.sh
```

The script creates `venv/` if needed, installs missing dependencies from `requirements.txt`, and starts Streamlit.

Open the app at:

```text
http://localhost:8501
```

To use a different port:

```bash
PORT=5000 ./run_app.sh
```

## Manual Setup

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## How to Use the App

1. Adjust the sidebar sliders for electricity price, battery level, and solar production.
2. Click `Calculate` to run the fuzzy inference engine.
3. Explore the tabs for membership functions, active rules, testing scenarios, and the system overview.

## Technical Overview

- Inference method: Mamdani min-max
- Defuzzification: centroid
- Membership functions: triangular and trapezoidal
- Inputs: electricity price, battery level, solar production
- Output: energy usage level
- Rule base: 20 IF-THEN rules

## Deploying the Main App

Use Streamlit Community Cloud for a direct live app:

1. Push the repository to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app from this repository.
4. Set the main file path to `app.py`.
5. Deploy.

Vercel is not recommended for this app because its Python runtime expects an ASGI/WSGI entrypoint like `app`, `application`, or `handler`, while Streamlit runs its own interactive app server.
