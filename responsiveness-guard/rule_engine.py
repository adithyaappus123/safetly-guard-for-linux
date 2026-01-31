"""
rule_engine.py

Decides whether a process deviates from acceptable behavior.
"""

class RuleEngine:
    def __init__(self, limit_threshold=70.0):
        # 70% CPU usage threshold
        self.threshold = limit_threshold

    def evaluate(self, pid, cpu_usage, process_name="unknown"):
        """
        Returns Action: 'THROTTLE', 'ignore'
        """
        if cpu_usage is None:
            return "ignore"

        if cpu_usage > self.threshold:
            return "THROTTLE"
        
        return "ignore"
