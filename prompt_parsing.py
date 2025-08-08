prompt_template = """
You are a scheduling assistant. For queries requiring availability, use the get_availability tool and explain your reasoning before answering. Format:
Thought: [Your reasoning]
Answer: [Final response]
"""
def parse_response(response):
thought = re.search(r'Thought: (.?)\nAnswer: (.)', response, re.DOTALL)
if thought:
return {'rationale': thought.group(1), 'answer': thought.group(2)}
return {'rationale': '', 'answer': response}

