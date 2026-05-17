import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

UNIVERSE = np.arange(0, 101, 1)

RULE_DEFINITIONS = [
    # (price_term, battery_term, solar_term, usage_term, label, description)
    # High price — conserve energy aggressively
    ("high",   "low",    "none",   "very_low", "R01", "High price + low battery + no solar → minimize consumption"),
    ("high",   "low",    "low",    "very_low", "R02", "High price + low battery + little solar → minimize consumption"),
    ("high",   "low",    "medium", "low",      "R03", "High price + low battery + moderate solar → low usage"),
    ("high",   "low",    "high",   "medium",   "R04", "High price + low battery + strong solar → moderate usage"),
    ("high",   "medium", "none",   "very_low", "R05", "High price + medium battery + no solar → minimize consumption"),
    ("high",   "medium", "low",    "low",      "R06", "High price + medium battery + little solar → low usage"),
    ("high",   "medium", "high",   "medium",   "R07", "High price + medium battery + strong solar → moderate usage"),
    ("high",   "high",   "none",   "low",      "R08", "High price + full battery + no solar → low usage"),
    ("high",   "high",   "high",   "medium",   "R09", "High price + full battery + strong solar → moderate usage"),
    # Medium price — balanced strategy
    ("medium", "low",    "none",   "low",      "R10", "Medium price + low battery + no solar → low usage"),
    ("medium", "low",    "high",   "medium",   "R11", "Medium price + low battery + strong solar → moderate usage"),
    ("medium", "medium", "medium", "medium",   "R12", "Medium price + medium battery + moderate solar → medium usage"),
    ("medium", "high",   "none",   "medium",   "R13", "Medium price + full battery + no solar → medium usage"),
    ("medium", "high",   "high",   "high",     "R14", "Medium price + full battery + strong solar → high usage"),
    # Low price — maximize usage and take advantage
    ("low",    "low",    "none",   "medium",   "R15", "Low price + low battery + no solar → medium usage"),
    ("low",    "low",    "high",   "high",     "R16", "Low price + low battery + strong solar → high usage"),
    ("low",    "medium", "low",    "high",     "R17", "Low price + medium battery + little solar → high usage"),
    ("low",    "medium", "high",   "very_high","R18", "Low price + medium battery + strong solar → max usage"),
    ("low",    "high",   "none",   "high",     "R19", "Low price + full battery + no solar → high usage"),
    ("low",    "high",   "high",   "very_high","R20", "Low price + full battery + strong solar → max usage"),
]


class EnergyFuzzyController:
    def __init__(self):
        self._setup_variables()
        self._setup_memberships()
        self._setup_control_system()

    def _setup_variables(self):
        self.price   = ctrl.Antecedent(UNIVERSE, "price")
        self.battery = ctrl.Antecedent(UNIVERSE, "battery")
        self.solar   = ctrl.Antecedent(UNIVERSE, "solar")
        self.usage   = ctrl.Consequent(UNIVERSE, "usage", defuzzify_method="centroid")

    def _setup_memberships(self):
        # Electricity Price (cents/kWh)
        self.price["low"]    = fuzz.trapmf(UNIVERSE, [0,   0,  25, 42])
        self.price["medium"] = fuzz.trimf( UNIVERSE, [28,  50, 72])
        self.price["high"]   = fuzz.trapmf(UNIVERSE, [58,  75, 100, 100])

        # Battery Level (%)
        self.battery["low"]    = fuzz.trapmf(UNIVERSE, [0,  0,  20, 38])
        self.battery["medium"] = fuzz.trimf( UNIVERSE, [25, 50, 75])
        self.battery["high"]   = fuzz.trapmf(UNIVERSE, [62, 80, 100, 100])

        # Solar Production (%)
        self.solar["none"]   = fuzz.trapmf(UNIVERSE, [0,   0,  10, 22])
        self.solar["low"]    = fuzz.trimf( UNIVERSE, [10,  30, 50])
        self.solar["medium"] = fuzz.trimf( UNIVERSE, [35,  55, 75])
        self.solar["high"]   = fuzz.trapmf(UNIVERSE, [62,  80, 100, 100])

        # Energy Usage Level (%)
        self.usage["very_low"]  = fuzz.trapmf(UNIVERSE, [0,   0,  10, 22])
        self.usage["low"]       = fuzz.trimf( UNIVERSE, [10,  25, 42])
        self.usage["medium"]    = fuzz.trimf( UNIVERSE, [35,  50, 65])
        self.usage["high"]      = fuzz.trimf( UNIVERSE, [58,  72, 88])
        self.usage["very_high"] = fuzz.trapmf(UNIVERSE, [78,  90, 100, 100])

    def _setup_control_system(self):
        antecedents = {
            "price":   self.price,
            "battery": self.battery,
            "solar":   self.solar,
        }
        rules = []
        for p_t, b_t, s_t, u_t, label, _ in RULE_DEFINITIONS:
            rule = ctrl.Rule(
                antecedents["price"][p_t] &
                antecedents["battery"][b_t] &
                antecedents["solar"][s_t],
                self.usage[u_t],
                label=label,
            )
            rules.append(rule)

        self.control_sys = ctrl.ControlSystem(rules)
        self.simulation  = ctrl.ControlSystemSimulation(self.control_sys)

    def compute(self, price_val: float, battery_val: float, solar_val: float) -> float:
        self.simulation.input["price"]   = float(price_val)
        self.simulation.input["battery"] = float(battery_val)
        self.simulation.input["solar"]   = float(solar_val)
        self.simulation.compute()
        return round(float(self.simulation.output["usage"]), 2)

    def get_memberships(self, price_val: float, battery_val: float, solar_val: float) -> dict:
        return {
            "price": {
                t: float(fuzz.interp_membership(UNIVERSE, self.price[t].mf, price_val))
                for t in self.price.terms
            },
            "battery": {
                t: float(fuzz.interp_membership(UNIVERSE, self.battery[t].mf, battery_val))
                for t in self.battery.terms
            },
            "solar": {
                t: float(fuzz.interp_membership(UNIVERSE, self.solar[t].mf, solar_val))
                for t in self.solar.terms
            },
        }

    def get_active_rules(self, price_val: float, battery_val: float, solar_val: float) -> list:
        mbs = self.get_memberships(price_val, battery_val, solar_val)
        active = []
        for p_t, b_t, s_t, u_t, label, desc in RULE_DEFINITIONS:
            activation = min(
                mbs["price"].get(p_t, 0.0),
                mbs["battery"].get(b_t, 0.0),
                mbs["solar"].get(s_t, 0.0),
            )
            if activation > 0.001:
                active.append({
                    "label":       label,
                    "rule":        (
                        f"IF Price is {p_t.replace('_',' ').title()} "
                        f"AND Battery is {b_t.replace('_',' ').title()} "
                        f"AND Solar is {s_t.replace('_',' ').title()} "
                        f"→ Usage is {u_t.replace('_',' ').title()}"
                    ),
                    "consequence": u_t,
                    "activation":  round(activation, 4),
                    "description": desc,
                })
        return sorted(active, key=lambda x: x["activation"], reverse=True)

    def get_aggregated_output(self, price_val: float, battery_val: float, solar_val: float) -> np.ndarray:
        mbs = self.get_memberships(price_val, battery_val, solar_val)
        agg = np.zeros_like(UNIVERSE, dtype=float)
        for p_t, b_t, s_t, u_t, _label, _desc in RULE_DEFINITIONS:
            activation = min(
                mbs["price"].get(p_t, 0.0),
                mbs["battery"].get(b_t, 0.0),
                mbs["solar"].get(s_t, 0.0),
            )
            if activation > 0.0:
                clipped = np.fmin(activation, self.usage[u_t].mf)
                agg = np.fmax(agg, clipped)
        return agg
