from llm_sdk import Small_LLM_Model
from parsing import is_valid_filename
import json

def generate_next_token(llm: Small_LLM_Model, tokens: list[int]) -> list[int]:
    possible_token = llm.get_logits_from_input_ids(tokens)
    max_value = max(possible_token)
    next_token = [key for key, elem in enumerate(possible_token) if max_value == elem]
    tokens.append(next_token[0])
    return tokens


def get_functions_json(filename: str = "functions_definition.json") -> str:
    # TODO faire une function pour recuperer le fonction et check si le format dans la reponse est bon ou pas
    try:
        is_valid_filename(filename)
        with open(
            f"../data/input/{filename}",
            "r"
        ) as original:
            available_functions = json.load(original)
            print(available_functions)

    except (FileNotFoundError, FileExistsError, ValueError, Exception) as e:
        print(e)


def create_prompt() -> str:
    pass


def main():
    # jarvis = Small_LLM_Model()
    # prompt:str = create_prompt()
    # "Do the calcul: '2+2'? Give me just the result. No explanation. Just the number. The Result is :"
    # tokens = jarvis.encode(prompt)
    # converted_list = list(tokens[0])
    get_functions_json()
    # while 1:
    #     generate_next_token(jarvis, converted_list)
    #     print(jarvis.decode(converted_list))
    

main()