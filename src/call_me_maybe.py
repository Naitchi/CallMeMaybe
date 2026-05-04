from llm_sdk import Small_LLM_Model
from parsing import (
    get_functions_json,
    get_prompts_json,
    make_output,
    sanitize_llm_json_response,
)


def generate_next_token(
        llm: Small_LLM_Model,
        tokens: list[int],
) -> int:
    possible_token = llm.get_logits_from_input_ids(tokens)
    max_value = max(possible_token)
    next_token = [
        key for key,
        elem in enumerate(possible_token)
        if max_value == elem
    ]
    tokens.append(next_token[0])
    return next_token[0]


def check_for_ended_response(response: str) -> bool:
    accolades: list = []
    for char in response:
        if char == '[' or char == '{':
            accolades.append(char)
        if char == ']' or char == '}':
            if (
                (accolades[-1] == '[' and char == ']')
                or (accolades[-1] == '{' and char == '}')
            ):
                accolades.pop(-1)
            else:
                return False
    if len(accolades) < 1:
        return False
    return True


def create_prompt(prompt: str, available_functions: str) -> tuple[str, str]:
    if len(prompt) < 1:
        raise ValueError("Error the prompt cannot be empty")
    prompt = prompt.replace('"', "\\\"")
    return (
        "".join([
            "With this prompt: \"",
            prompt,
            "\" Use this list of function: ",
            available_functions,
            " and return only JSON with prompt (prompt), the name of the "
            "function",
            " (name) you will use, and the parameters (parameters). ",
            "The Answer: {",
            " \"prompt\": \"",
            prompt,
            "\", \"name\": \""
        ]),
        "".join([
            "{",
            " \"prompt\": \"",
            prompt,
            "\", \"name\": \""
        ])
    )


def main():
    # TODO faire pour qu'on recupere les args et les passe dans get_functions_json et get_prompt_json (changer pour verifier les donnees avant et pas dans les fonctions comme maintenant(sale))
    # "Do the calcul: '2x8'? Give me just the result. No explanation. Just the number. Put a point after your response. The Result is :"
    available_functions: list[dict] = get_functions_json()
    prompts: list[dict] = get_prompts_json()
    jarvis: Small_LLM_Model = Small_LLM_Model()
    anwsers: list[str] = []
    for user_prompt in prompts:
        try:
            response: str = ""
            prompt: str = ""
            (prompt, response) = create_prompt(
                user_prompt["prompt"],
                str(available_functions)
            )
            tokens = jarvis.encode(prompt)
            converted_list = list(tokens[0])
            while check_for_ended_response(response):
                response = "".join([
                    response,
                    jarvis.decode(generate_next_token(jarvis, converted_list))]
                )
                # TODO si le dernier caractere de response est '"' ou '",' etc ajouter en dur le prochain champ pour accelerer la generation de la reponse
            response = sanitize_llm_json_response(response)
            anwsers.append(response)
        except (
            FileNotFoundError,
            FileExistsError,
            ValueError,
            Exception
        )as e:
            print(e)
    try:
        make_output(anwsers)
    except (Exception)as e:
        print(e)


main()
