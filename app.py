import matplotlib
matplotlib.use("Agg")

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from fuzzy_system.controller import EnergyFuzzyController, UNIVERSE, RULE_DEFINITIONS

st.set_page_config(
    page_title="Smart Energy Controller",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Shared palette ─────────────────────────────────────────────────────────
BG_DARK   = "#0E1117"
BG_PANEL  = "#1A1D27"
BG_CARD   = "#22263A"
GRID_CLR  = "#2A2D3A"
TEXT_WH   = "#E8EAF6"
ACCENT    = "#4FC3F7"
CENTROID  = "#FF7043"
MF_COLORS = ["#4FC3F7", "#81C784", "#FFB74D", "#CE93D8", "#EF9A9A"]


def apply_dark_axes(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(BG_PANEL)
    ax.tick_params(colors=TEXT_WH, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_CLR)
    ax.set_xlabel(xlabel, fontsize=9, color=TEXT_WH)
    ax.set_ylabel(ylabel, fontsize=9, color=TEXT_WH)
    ax.set_title(title, fontsize=11, fontweight="bold", color=TEXT_WH, pad=8)
    ax.grid(True, alpha=0.18, color=GRID_CLR, linewidth=0.8)
    ax.set_xlim([0, 100])
    ax.set_ylim([-0.04, 1.12])


# ─── Controller (singleton) ─────────────────────────────────────────────────
@st.cache_resource
def get_controller():
    return EnergyFuzzyController()

ctrl = get_controller()

# ─── Session state defaults ─────────────────────────────────────────────────
for key, default in [
    ("result", None),
    ("active_rules", []),
    ("agg_output", None),
    ("price_val", 70),
    ("battery_val", 30),
    ("solar_val", 20),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ System Inputs")
    st.markdown("Set the real-time conditions and press **Calculate** to run the fuzzy inference engine.")
    st.divider()

    price_val   = st.slider("💰 Electricity Price (cents/kWh)", 0, 100, st.session_state.price_val,
                            help="Grid electricity purchase price")
    battery_val = st.slider("🔋 Battery Level (%)", 0, 100, st.session_state.battery_val,
                            help="State of charge of the battery storage system")
    solar_val   = st.slider("☀️ Solar Production (%)", 0, 100, st.session_state.solar_val,
                            help="Current solar panel output as a percentage of peak capacity")

    st.divider()
    calc_clicked = st.button("⚡ Calculate", type="primary", use_container_width=True)

    st.divider()
    st.markdown(
        "**System Info**\n"
        "- Inference: Mamdani\n"
        "- Defuzzification: Centroid\n"
        "- Variables: 3 inputs, 1 output\n"
        "- Rules: 20\n"
        "- Terms: 3–4 per input, 5 output"
    )

# ─── Run inference ───────────────────────────────────────────────────────────
if calc_clicked:
    st.session_state.price_val   = price_val
    st.session_state.battery_val = battery_val
    st.session_state.solar_val   = solar_val
    try:
        output_val   = ctrl.compute(price_val, battery_val, solar_val)
        active_rules = ctrl.get_active_rules(price_val, battery_val, solar_val)
        agg_output   = ctrl.get_aggregated_output(price_val, battery_val, solar_val)
        st.session_state.result       = output_val
        st.session_state.active_rules = active_rules
        st.session_state.agg_output   = agg_output
    except Exception as e:
        st.error(f"Inference error: {e}")

# ─── Helper ──────────────────────────────────────────────────────────────────
def usage_label(val):
    if   val < 20: return "Very Low",  "🟢", "#4CAF50"
    elif val < 38: return "Low",        "🟡", "#8BC34A"
    elif val < 62: return "Medium",     "🟠", "#FF9800"
    elif val < 80: return "High",       "🔴", "#F44336"
    else:          return "Very High",  "🔴", "#B71C1C"


# ─── Page title ──────────────────────────────────────────────────────────────
st.title("⚡ Smart Energy Consumption Controller")
st.markdown(
    "A **Mamdani Fuzzy Logic System** that intelligently determines the optimal energy "
    "usage level based on electricity price, battery state, and solar production."
)
st.divider()

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_mf, tab_result, tab_scenarios, tab_about = st.tabs([
    "📈 Membership Functions",
    "⚡ Results & Active Rules",
    "🧪 Testing Scenarios",
    "📖 System Overview",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Membership Functions
# ══════════════════════════════════════════════════════════════════════════════
with tab_mf:
    st.subheader("Membership Functions")
    st.markdown(
        "Each variable is partitioned into overlapping fuzzy sets defined by triangular "
        "and trapezoidal membership functions. The **dashed white line** marks the current input value."
    )

    p_val = st.session_state.price_val
    b_val = st.session_state.battery_val
    s_val = st.session_state.solar_val

    fig, axes = plt.subplots(2, 2, figsize=(13, 7))
    fig.patch.set_facecolor(BG_DARK)

    vars_cfg = [
        (ctrl.price,   p_val, "Electricity Price (cents/kWh)", "Price"),
        (ctrl.battery, b_val, "Battery Level (%)",             "Battery Level"),
        (ctrl.solar,   s_val, "Solar Production (%)",          "Solar Production"),
        (ctrl.usage,   None,  "Energy Usage Level (%)",        "Output: Energy Usage"),
    ]

    for idx, (var, val, xlabel, title) in enumerate(vars_cfg):
        ax = axes[idx // 2][idx % 2]
        apply_dark_axes(ax, title=title, xlabel=xlabel, ylabel="μ(x)")
        for i, (term_name, term) in enumerate(var.terms.items()):
            color = MF_COLORS[i % len(MF_COLORS)]
            lbl   = term_name.replace("_", " ").title()
            ax.plot(UNIVERSE, term.mf, color=color, linewidth=2.2, label=lbl)
            ax.fill_between(UNIVERSE, term.mf, alpha=0.07, color=color)
        if val is not None:
            ax.axvline(x=val, color="white", linestyle="--", linewidth=1.8, alpha=0.85,
                       label=f"Current: {val}")
        ax.legend(fontsize=8, loc="upper right",
                  facecolor=BG_CARD, edgecolor=GRID_CLR, labelcolor=TEXT_WH)

    plt.tight_layout(pad=2.0)
    st.pyplot(fig)
    plt.close(fig)

    st.info(
        "**Shapes used:** Trapezoidal (flat-topped) for boundary terms (e.g., Low at the "
        "lower end, High at the upper end) and Triangular for middle terms — this avoids "
        "hard cut-offs at the extremes."
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Results & Active Rules
# ══════════════════════════════════════════════════════════════════════════════
with tab_result:
    if st.session_state.result is None:
        st.info("Adjust the sliders in the sidebar and press **⚡ Calculate** to run the fuzzy controller.")
    else:
        output_val   = st.session_state.result
        active_rules = st.session_state.active_rules
        agg_output   = st.session_state.agg_output
        lbl, icon, color = usage_label(output_val)

        # ── Metrics row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Energy Usage Level", f"{output_val:.1f}%")
        c2.metric("Linguistic Output",  f"{icon} {lbl}")
        c3.metric("Active Rules",       f"{len(active_rules)} / {len(RULE_DEFINITIONS)}")
        c4.metric("Defuzzification",    "Centroid")

        st.divider()

        # ── Output aggregation plot
        st.subheader("Aggregated Output & Centroid Defuzzification")
        st.markdown(
            "The **cyan area** is the union of all clipped consequence membership functions "
            "(Mamdani aggregation). The **orange dashed line** is the centroid — the crisp output."
        )

        fig2, ax2 = plt.subplots(figsize=(11, 4))
        fig2.patch.set_facecolor(BG_DARK)
        apply_dark_axes(ax2,
                        title="Aggregated Output Fuzzy Set",
                        xlabel="Energy Usage Level (%)",
                        ylabel="μ(x)")

        # Individual output MFs (dim)
        for i, (term_name, term) in enumerate(ctrl.usage.terms.items()):
            ax2.plot(UNIVERSE, term.mf, "--", alpha=0.25, color=MF_COLORS[i], linewidth=1.2,
                     label=term_name.replace("_", " ").title())

        # Aggregated output
        ax2.fill_between(UNIVERSE, agg_output, alpha=0.30, color=ACCENT)
        ax2.plot(UNIVERSE, agg_output, color=ACCENT, linewidth=2.2, label="Aggregated")

        # Centroid marker
        ax2.axvline(x=output_val, color=CENTROID, linewidth=2.5, linestyle="--",
                    label=f"Centroid: {output_val:.1f}%")
        ax2.fill_betweenx([0, 1.05], output_val - 1.2, output_val + 1.2,
                          alpha=0.25, color=CENTROID)

        ax2.legend(fontsize=8.5, facecolor=BG_CARD, edgecolor=GRID_CLR, labelcolor=TEXT_WH)
        plt.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

        st.divider()

        # ── Active rules
        st.subheader(f"Activated Rules — {len(active_rules)} of {len(RULE_DEFINITIONS)} fired")
        if active_rules:
            # Activation bar chart
            labels_chart = [r["label"] for r in active_rules]
            vals_chart   = [r["activation"] for r in active_rules]

            fig3, ax3 = plt.subplots(figsize=(max(6, len(active_rules) * 0.7), 3.5))
            fig3.patch.set_facecolor(BG_DARK)
            apply_dark_axes(ax3, title="Rule Activation Strengths",
                            xlabel="Rule", ylabel="Activation Degree")
            bars = ax3.bar(labels_chart, vals_chart, color=ACCENT, alpha=0.82, edgecolor=GRID_CLR)
            ax3.set_ylim([0, 1.1])
            for bar, v in zip(bars, vals_chart):
                ax3.text(bar.get_x() + bar.get_width() / 2, v + 0.03, f"{v:.3f}",
                         ha="center", va="bottom", fontsize=8, color=TEXT_WH)
            plt.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

            st.markdown("**Rule Detail:**")
            for rule in active_rules:
                pct = int(rule["activation"] * 100)
                col_lbl, col_rule, col_bar, col_val = st.columns([0.8, 5, 3, 0.9])
                with col_lbl:
                    st.markdown(f"**{rule['label']}**")
                with col_rule:
                    st.caption(rule["rule"])
                with col_bar:
                    st.progress(pct)
                with col_val:
                    st.caption(f"{rule['activation']:.3f}")
        else:
            st.warning("No rules activated for the current inputs. Try different slider values.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Testing Scenarios
# ══════════════════════════════════════════════════════════════════════════════
with tab_scenarios:
    st.subheader("Predefined Test Scenarios")
    st.markdown(
        "The following scenarios systematically test the system across the full input space. "
        "Results verify that the fuzzy rules produce logically consistent behaviour."
    )

    SCENARIOS = [
        # (name, price, battery, solar, expected, reasoning)
        ("Peak Grid, Empty Battery, No Sun",    90, 10, 5,  "Very Low",
         "Worst case: grid is expensive, battery nearly empty, no solar. "
         "System must minimise load to avoid cost and battery drain."),
        ("Peak Grid, Empty Battery, Full Sun",  90, 10, 90, "Medium",
         "Expensive grid but solar is producing plenty — moderate usage is sustainable "
         "from solar without drawing from the grid."),
        ("Peak Grid, Full Battery, No Sun",     88, 90, 5,  "Low",
         "Grid expensive; battery is full so slight discharge is possible, "
         "but conserving battery for later is prudent → low usage."),
        ("Peak Grid, Full Battery, Full Sun",   85, 90, 90, "Medium",
         "Even with full resources the high price incentivises restraint. "
         "Medium usage draws primarily from solar."),
        ("Cheap Grid, Empty Battery, No Sun",   10, 10, 5,  "Medium",
         "Price is low — good time to draw from grid even with low battery and no sun."),
        ("Cheap Grid, Full Battery, Full Sun",  10, 90, 90, "Very High",
         "Best case: grid is cheap, battery full, solar at peak — "
         "maximize consumption and potentially store excess."),
        ("Cheap Grid, Full Battery, No Sun",    12, 90, 5,  "High",
         "Low price and full battery: high usage is economic even without solar."),
        ("Medium Grid, Balanced Resources",     50, 50, 50, "Medium",
         "All inputs at midpoint — system should output a balanced, neutral response."),
        ("Medium Grid, Low Battery, Low Sun",   52, 15, 12, "Low",
         "Moderate price, scarce resources — cautious low usage is logical."),
        ("Medium Grid, High Battery, High Sun", 48, 85, 82, "High",
         "Moderate price but rich in stored and renewable energy — high usage justified."),
    ]

    # Run all scenarios
    results = []
    for name, p, b, s, expected, reasoning in SCENARIOS:
        try:
            output = ctrl.compute(p, b, s)
            lbl, icon, _ = usage_label(output)
        except Exception:
            output, lbl, icon = 0.0, "Error", "❌"
        results.append((name, p, b, s, output, lbl, expected, icon, reasoning))

    # Table
    import pandas as pd
    df = pd.DataFrame([
        {
            "Scenario":          r[0],
            "Price (¢/kWh)":     r[1],
            "Battery (%)":       r[2],
            "Solar (%)":         r[3],
            "Output (%)":        f"{r[4]:.1f}",
            "Linguistic Output": f"{r[7]} {r[5]}",
            "Expected":          r[6],
        }
        for r in results
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Scatter / response plot
    st.divider()
    st.subheader("Output Distribution Across Scenarios")

    fig4, ax4 = plt.subplots(figsize=(11, 4))
    fig4.patch.set_facecolor(BG_DARK)
    apply_dark_axes(ax4,
                    title="Output Value per Scenario",
                    xlabel="Scenario Index",
                    ylabel="Energy Usage Level (%)")

    x_pos   = list(range(len(results)))
    y_vals  = [r[4] for r in results]
    colors_ = [usage_label(v)[2] for v in y_vals]
    ax4.bar(x_pos, y_vals, color=colors_, alpha=0.75, edgecolor=GRID_CLR)
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels([f"S{i+1}" for i in x_pos], color=TEXT_WH, fontsize=9)
    ax4.set_ylim([0, 105])
    for xi, yi in zip(x_pos, y_vals):
        ax4.text(xi, yi + 2, f"{yi:.0f}%", ha="center", fontsize=8, color=TEXT_WH)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close(fig4)

    # Per-scenario detail
    st.divider()
    st.subheader("Scenario Analysis")
    for i, (name, p, b, s, output, lbl, expected, icon, reasoning) in enumerate(results):
        with st.expander(f"S{i+1} — {name}  →  {icon} {lbl} ({output:.1f}%)"):
            cols = st.columns(3)
            cols[0].metric("Electricity Price", f"{p} ¢/kWh")
            cols[1].metric("Battery Level",     f"{b}%")
            cols[2].metric("Solar Production",  f"{s}%")
            st.metric("System Output", f"{output:.1f}%  ({lbl})")
            st.markdown(f"**Analysis:** {reasoning}")
            active = ctrl.get_active_rules(p, b, s)
            if active:
                st.markdown(
                    "**Fired rules:** " +
                    ", ".join(f"{r['label']} ({r['activation']:.2f})" for r in active)
                )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — System Overview
# ══════════════════════════════════════════════════════════════════════════════
with tab_about:
    st.subheader("Problem Definition")
    st.markdown("""
Modern homes and microgrids face a constant trade-off: **when** to consume energy, **how much**
to draw from the grid versus stored or renewable sources, and **how aggressively** to conserve.
Classical control approaches require precise models; fuzzy logic mirrors human expert reasoning —
"if the price is high and the battery is low, minimise consumption" — without needing exact thresholds.

**Why fuzzy logic is appropriate here:**
- Electricity price, battery state, and solar output are inherently imprecise and continuously varying.
- Human experts reason in linguistic terms ("the battery is almost full"), not crisp numbers.
- The decision boundaries are gradual, not sharp — a slightly expensive price shouldn't trigger a
  completely different response than a moderately expensive one.
- The system must be explainable and interpretable, unlike a black-box ML model.
""")

    st.divider()
    st.subheader("System Variables")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Inputs**")
        st.markdown("""
| Variable | Range | Linguistic Terms |
|---|---|---|
| Electricity Price | 0–100 ¢/kWh | Low, Medium, High |
| Battery Level | 0–100 % | Low, Medium, High |
| Solar Production | 0–100 % | None, Low, Medium, High |
""")
    with col_b:
        st.markdown("**Output**")
        st.markdown("""
| Variable | Range | Linguistic Terms |
|---|---|---|
| Energy Usage Level | 0–100 % | Very Low, Low, Medium, High, Very High |
""")

    st.divider()
    st.subheader("Rule Base (20 rules)")
    rules_df_data = []
    for p_t, b_t, s_t, u_t, label, desc in RULE_DEFINITIONS:
        rules_df_data.append({
            "Rule": label,
            "IF Price":   p_t.replace("_", " ").title(),
            "AND Battery":b_t.replace("_", " ").title(),
            "AND Solar":  s_t.replace("_", " ").title(),
            "THEN Usage": u_t.replace("_", " ").title(),
        })
    import pandas as pd
    st.dataframe(pd.DataFrame(rules_df_data), use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Inference Method")
    st.markdown("""
**Mamdani Inference Engine (min–max):**
1. **Fuzzification** — each crisp input is mapped to membership degrees via the MFs above.
2. **Rule evaluation** — each rule fires with strength = min(antecedent memberships).
3. **Aggregation** — consequence MFs are clipped at the rule strength, then unioned (max).
4. **Defuzzification (Centroid)** — the crisp output is the centre of mass of the aggregated fuzzy set:

$$z^* = \\frac{\\int \\mu(z)\\, z\\, dz}{\\int \\mu(z)\\, dz}$$
""")

    st.divider()
    st.subheader("Comparison: Fuzzy Logic vs Modern AI Approaches")
    st.markdown("""
| Criterion | Fuzzy Logic | Machine Learning / Neural Nets |
|---|---|---|
| **Interpretability** | ✅ Human-readable rules | ❌ Black box |
| **Training data** | ✅ Not required | ❌ Requires labelled dataset |
| **Computational cost** | ✅ Very low | ❌ Can be high |
| **Rule design** | ⚠️ Expert knowledge needed | ✅ Learned automatically |
| **Scalability** | ⚠️ Rule explosion with many inputs | ✅ Scales well |
| **Adaptability** | ⚠️ Manual rule updates | ✅ Retrainable |
| **Edge cases** | ✅ Handled gracefully by MF overlap | ⚠️ May fail on out-of-distribution data |

**Conclusion:** Fuzzy logic is the right tool for this domain — interpretability, real-time performance,
and no need for training data outweigh the limitation of manual rule design for a 3-input system.
For a 10+ input industrial energy management system, a hybrid fuzzy-neural approach (ANFIS) would be preferred.
""")
