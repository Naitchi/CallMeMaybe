from llm_sdk import Small_LLM_Model

def generate_next_token(llm:Small_LLM_Model ,tokens:list[int]) -> list[int]:
    possible_token = llm.get_logits_from_input_ids(tokens)
    max_value = max(possible_token)
    next_token = [key for key, elem in enumerate(possible_token) if max_value == elem]
    tokens.append(next_token[0])
    return tokens


def get_functions_json(file_name: str = "functions_definition.json")->str:
    print(file_name)


def main():
    jarvis = Small_LLM_Model()
    tokens = jarvis.encode("Do the calcul: '2+2'? Give me just the result. No explanation. Just the number. The Result is :")
    converted_list = list(tokens[0])
    get_functions_json()
    while 1:
        generate_next_token(jarvis, converted_list)
        print(jarvis.decode(converted_list))
    

main()