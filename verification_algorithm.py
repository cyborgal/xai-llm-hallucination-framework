def verify_tool_output(tool_result, llm_expected):
prolog_program = generate_prolog_facts(tool_result)
prolog_result = swi_prolog_query(prolog_program, llm_expected.time)
if prolog_result['valid']:
return prolog_result['match']
else:
return {'valid': False, 'justification': prolog_result['reason']}
