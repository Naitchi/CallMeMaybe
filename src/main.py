from llm_sdk import Small_LLM_Model
from parsing import is_valid_filename, check_json_functions
import json

def generate_next_token(llm: Small_LLM_Model, tokens: list[int]) -> list[int]:
    possible_token = llm.get_logits_from_input_ids(tokens)
    max_value = max(possible_token)
    print(max_value)
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
            check_json_functions(available_functions)
            return available_functions
    except (FileNotFoundError, FileExistsError, ValueError, Exception) as e:
        print(e)

def get_prompts_json(filename: str = "function_calling_tests.json") -> list[dict]:
    try:
        is_valid_filename(filename)
        with open(
            f"../data/input/{filename}",
            "r"
        ) as original:
            return json.load(original)
    except (FileNotFoundError, FileExistsError, ValueError, Exception) as e:
        print(e)

def create_prompt(prompt: str, available_functions: str) -> str:
    if len(prompt) < 1:
        raise ValueError("Error the prompt cannot be empty")
    return "".join([
        "With this prompt: \"", 
        prompt,
        "\" Use this list of function: ", 
        available_functions, 
        " and return only JSON with prompt (prompt), the name of the function (name) you will use, and the parameters (parameters). The Answer: { \"prompt\": \"",
        prompt,
        "\", \"name\": "
    ])


def main():
    # TODO faire pour qu'on recupere les args et les passe dans get_functions_json et get_prompt_json (changer pour verifier les donnees avant et pas dans les fonctions comme maintenant(sale))
    # "Do the calcul: '2x8'? Give me just the result. No explanation. Just the number. Put a point after your response. The Result is :"
    available_functions = get_functions_json()
    prompts = get_prompts_json()
    jarvis = Small_LLM_Model()
    for user_prompt in prompts:
        try :
            prompt:str = create_prompt(user_prompt["prompt"], str(available_functions))
            tokens = jarvis.encode(prompt)
            print(tokens)
            converted_list = list(tokens[0])
            while 1:
                generate_next_token(jarvis, converted_list)
                print(jarvis.decode(converted_list))
        except (FileNotFoundError, FileExistsError, ValueError, Exception) as e:
            print(e)

main()