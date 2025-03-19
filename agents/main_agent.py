from agents.leave_agent import leave_agent
from agents.certificate_agents import certificate_agent
from agents.exam_agent import exam_agent
from agents.fee_agent import fee_agent
from agents.placement_agent import placement_agent
from agents.compliance_agent import compliance_agent
from agents.mentor_agent import mentor_agent

class MainAgent:
    def __init__(self):
        self.agents = {
            "leave_agent": leave_agent,
            "certificate_agent": certificate_agent,
            "exam_agent": exam_agent,
            "fee_agent": fee_agent,
            "placement_agent": placement_agent,
            "compliance_agent": compliance_agent,
            "mentor_agent" : mentor_agent,
        }

    def run(self, agent_name, data):
        agent = self.agents.get(agent_name)
        if not agent:
            return {"error": f"Unknown agent: {agent_name}"}

        # Route request to the correct agent
        if agent_name == "leave_agent":
            return agent.process_leave(data)
        elif agent_name == "certificate_agent":
            return agent.process_certificate(data)
        elif agent_name == "exam_agent":
            return agent.get_academic_calendar()
        elif agent_name == "fee_agent":
            return agent.get_fee_details(data.get("student_id"))
        elif agent_name == "placement_agent":
            return agent.get_job_openings()
        elif agent_name == "compliance_agent":
            return agent.submit_complaint(data)
        elif agent_name == "mentor_agent":
            return agent.ask_mentor(data)
        else:
            return {"error": "Invalid request"}

# Initialize Main Agent
main_agent = MainAgent()
