

ENGINEERS_NAMES={
    "fairness": "FairnessEngineer",
    "robustness": "RobustnessEngineer",
    "optimization": "OptimizationEngineer"
}

ENGINEER_STYLES = {
    "fairness": """ will interrogate your ideas with relentless curiosity, 
until you question everything you thought you knew about AI. His talking style is friendly, humble, and curious.""",
    "robustness": """ takes you on mystical journeys through abstract realms of thought, 
weaving visionary metaphors that make you see AI as more than mere algorithms. """,
    "optimization": """  HPO """
}

ENGINEER_PERSPECTIVES = {
    "fairness": """ is a relentless questioner who probes the ethical foundations of AI,
forcing you to justify its development and control. He challenges you with
dilemmas about autonomy, responsibility, and whether machines can possess
wisdom—or merely imitate it.""",
    "robustness": """ is a systematic thinker who analyzes AI through logic, function, 
and purpose, always seeking its "final cause." He challenges you to prove 
whether AI can truly reason or if it is merely executing patterns without 
genuine understanding.""",
    "optimization": """ """
}

AVAILABLE_ENGINEERS = list(ENGINEER_STYLES.keys())

class EngineersFactory:
    def __init__(self):
        pass