# ⚡ Smart Energy Consumption Controller

A **Mamdani Fuzzy Logic System** that intelligently determines the optimal energy usage level based on real-time electricity price, battery state, and solar production.

---

## What This Project Does

This system acts as a smart energy controller for a home or microgrid. Given three inputs, it uses fuzzy logic to decide how aggressively the system should consume energy:

| Input | Range | Description |
|---|---|---|
| Electricity Price | 0–100 ¢/kWh | Current grid purchase price |
| Battery Level | 0–100 % | State of charge of battery storage |
| Solar Production | 0–100 % | Solar panel output as % of peak capacity |

| Output | Range | Meaning |
|---|---|---|
| Energy Usage Level | 0–100 % | How much energy the system should consume |

The system uses **20 fuzzy IF-THEN rules**, **Mamdani inference**, and **centroid defuzzification**.

---

## Prerequisites

Make sure you have the following installed on your machine before starting:

- **Python 3.11** (recommended) — [Download here](https://www.python.org/downloads/)
- **Git** — [Download here](https://git-scm.com/)
- **VS Code** — [Download here](https://code.visualstudio.com/)

---

## Setup Steps

### 1. Clone the Repository

Open a terminal (or the VS Code integrated terminal) and run:

```bash
git clone <your-repository-url>
cd <repository-folder-name>
```

> Replace `<your-repository-url>` with the actual GitHub URL of this project.

---

### 2. Open in VS Code

```bash
code .
```

Or open VS Code manually, go to **File → Open Folder**, and select the project folder.

---

### 3. Create a Python Virtual Environment

A virtual environment keeps the project dependencies isolated from your global Python installation.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear at the start of your terminal prompt — this confirms the virtual environment is active.

---

### 4. Install All Required Packages

With the virtual environment active, install everything from `requirements.txt`:

```bash
pip install -r requirements.txt
```

This installs the following packages:

| Package | Purpose |
|---|---|
| `streamlit` | Interactive web GUI |
| `scikit-fuzzy` | Fuzzy logic inference engine |
| `scipy` | Required by scikit-fuzzy (math backend) |
| `numpy` | Numerical computation and array operations |
| `matplotlib` | Plotting membership functions and output graphs |
| `networkx` | Required by scikit-fuzzy (graph structures) |

> Installation usually takes 1–3 minutes depending on your internet speed.

---

### 5. Run the Application

```bash
streamlit run app.py
```

Streamlit will automatically open the app in your default browser at:

```
http://localhost:8501
```

If it doesn't open automatically, copy and paste that URL into your browser.

---

## Project Structure

```
smart-energy-controller/
│
├── app.py                   # Main Streamlit application (UI, plots, tabs)
│
├── fuzzy_system/
│   ├── __init__.py          # Package exports
│   └── controller.py        # Fuzzy variables, MFs, 20 rules, inference engine
│
├── .streamlit/
│   └── config.toml          # Streamlit server configuration
│
├── requirements.txt         # All Python dependencies
└── README.md                # This file
```

---

## How to Use the App

1. **Adjust the sliders** in the left sidebar:
   - Electricity Price (¢/kWh)
   - Battery Level (%)
   - Solar Production (%)

2. **Click the ⚡ Calculate button** to run the fuzzy inference engine.

3. **Explore the 4 tabs:**

| Tab | Contents |
|---|---|
| 📈 Membership Functions | Plots all fuzzy sets for each variable with a live input marker |
| ⚡ Results & Active Rules | Output value, aggregated fuzzy set, centroid, and all fired rules with activation strength |
| 🧪 Testing Scenarios | 10 predefined test cases with analysis and output bar chart |
| 📖 System Overview | Full academic breakdown: variables, rule table, inference method, Fuzzy vs ML comparison |

---

## VS Code Tips

- Install the **Python extension** (`ms-python.python`) in VS Code for syntax highlighting and IntelliSense.
- Select your virtual environment as the Python interpreter:
  - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
  - Type **Python: Select Interpreter**
  - Choose the one that shows `venv` in the path
- The integrated terminal in VS Code (`Ctrl+\``) can be used for all commands above.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'scipy'` | Run `pip install scipy` inside your virtual environment |
| `ModuleNotFoundError: No module named 'skfuzzy'` | Run `pip install scikit-fuzzy` |
| `streamlit: command not found` | Make sure your virtual environment is activated (see Step 3) |
| Port already in use | Run `streamlit run app.py --server.port 8502` to use a different port |
| Blank page in browser | Wait a few seconds and refresh — Streamlit may still be loading |

---

## Technical Overview

- **Inference method:** Mamdani (min–max)
- **Defuzzification:** Centroid (centre of mass)
- **Membership function shapes:** Triangular (middle terms) and Trapezoidal (boundary terms)
- **Rules:** 20 IF-THEN rules covering low / medium / high price tiers
- **Output terms:** Very Low, Low, Medium, High, Very High

---

## Dependencies Summary

```
streamlit>=1.35.0
scikit-fuzzy>=0.4.2
scipy>=1.10.0
numpy>=1.24.0
matplotlib>=3.7.0
networkx>=3.0
```
