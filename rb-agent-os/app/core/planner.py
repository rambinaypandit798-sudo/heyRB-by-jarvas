"""
Task Execution Planner for RB Agent OS.
Deconstructs complex intents into structured, executable, and verifiable steps.
"""

from typing import Any, Dict, List
import uuid
from .router import IntentClassification

class TaskPlanStep:
    def __init__(
        self,
        step_order: int,
        description: str,
        tool_name: str,
        input_data: Dict[str, Any]
    ):
        self.step_order = step_order
        self.description = description
        self.tool_name = tool_name
        self.input_data = input_data

class TaskPlan:
    def __init__(self, title: str, intent: str, steps: List[TaskPlanStep]):
        self.title = title
        self.intent = intent
        self.steps = steps

class Planner:
    def create_plan(self, prompt: str, classification: IntentClassification) -> TaskPlan:
        steps: List[TaskPlanStep] = []
        intent = classification.intent
        entities = classification.entities

        if intent == "android_action":
            tool = classification.recommended_tools[0] if classification.recommended_tools else "termux_battery_status"
            if tool == "termux_battery_status":
                steps.append(TaskPlanStep(
                    step_order=1,
                    description="Query device battery level via Termux:API",
                    tool_name="termux_battery_status",
                    input_data={}
                ))
            elif tool == "termux_toast":
                steps.append(TaskPlanStep(
                    step_order=1,
                    description=f"Display screen toast: {entities.get('message', '')}",
                    tool_name="termux_toast",
                    input_data={"message": entities.get("message", "RB Agent Alert")}
                ))
            elif tool == "termux_vibrate":
                steps.append(TaskPlanStep(
                    step_order=1,
                    description=f"Trigger device vibration ({entities.get('duration_ms', 300)}ms)",
                    tool_name="termux_vibrate",
                    input_data={"duration_ms": entities.get("duration_ms", 300)}
                ))
            elif tool == "android_open_intent":
                steps.append(TaskPlanStep(
                    step_order=1,
                    description=f"Open external URI intent: {entities.get('uri', '')}",
                    tool_name="android_open_intent",
                    input_data={"uri": entities.get("uri", "")}
                ))

        elif intent == "file_operation":
            tool = classification.recommended_tools[0]
            if tool == "list_files":
                steps.append(TaskPlanStep(
                    step_order=1,
                    description="Inspect files in workspace directory",
                    tool_name="list_files",
                    input_data={"path": entities.get("path", ".")}
                ))
            elif tool == "read_file":
                steps.append(TaskPlanStep(
                    step_order=1,
                    description=f"Read contents of file '{entities.get('path', '')}'",
                    tool_name="read_file",
                    input_data={"path": entities.get("path", "")}
                ))
            elif tool == "write_file":
                content = entities.get("content", prompt)
                steps.append(TaskPlanStep(
                    step_order=1,
                    description=f"Write content to workspace file '{entities.get('path', 'output.txt')}'",
                    tool_name="write_file",
                    input_data={"path": entities.get("path", "output.txt"), "content": content}
                ))

        elif intent == "code_execution":
            code = entities.get("code") or 'print("RB Agent OS execution check passed.")'
            steps.append(TaskPlanStep(
                step_order=1,
                description="Execute isolated Python script in workspace",
                tool_name="run_python",
                input_data={"code": code}
            ))

        elif intent == "research":
            query = entities.get("query", prompt)
            steps.append(TaskPlanStep(
                step_order=1,
                description=f"Perform factual online research for: {query}",
                tool_name="web_search",
                input_data={"query": query}
            ))

        return TaskPlan(
            title=f"Plan for: {prompt[:40]}",
            intent=intent,
            steps=steps
        )

planner = Planner()
