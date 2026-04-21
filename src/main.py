from llm_sdk import Small_LLM_Model

def get_index_max(logic_ids:list[int]) -> int:
    max_value = max(logic_ids)
    rslt = [key for key, elem in enumerate(logic_ids) if max_value == elem]
    return rslt[0]


def main():
    jarvis = Small_LLM_Model()
    tokens = jarvis.encode("Combien font 2 + 2 ?")
    print(tokens)
    converted_list = list(tokens[0])
    print(converted_list)
    logic_ids = jarvis.get_logits_from_input_ids(converted_list)
    print(get_index_max(logic_ids))
    logic_ids.remove(max(logic_ids))
    print(get_index_max(logic_ids))


main()