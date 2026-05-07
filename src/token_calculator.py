import json
from transformers import AutoTokenizer

def count_tokens():
    """
    With this function, I want to count the exact number of tokens for mistral-7b-instruct model.
    I will use the AutoTokenizer from Hugging Face to load the tokenizer for the mistral-7b-instruct model.
    Then, I will read the articles from the input JSONL file and use the tokenizer to count the number of tokens for each article.
    Finally, I will see the minimum, maximum, and average token counts.
    """

    # Load the tokenizer for the mistral-7b-instruct model from Hugging Face
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.2")

    input_file = 'data/aufgabe_a_data.jsonl'
    output_file = 'data/aufgabe_a_results.json'

    prompt= """You are a helpful assistant for extracting information from news articles. You must follow these strict rules:
        SUMMARY: Provide a one-sentence summary. It MUST be extremely concise, aiming for 10-15 words. NEVER exceed 20 words.
        FLAGS: ONLY use the exact predefined categories provided in the schema. Do not invent new flags. Each flag must be UNIQUE.
        ENTITIES: Identify key entities and their types."""

    # Read the articles from the input JSONL file and count the number of tokens for each article, including the prompt and the article text
    input_token_list = []
    with open(input_file, 'r',encoding='utf-8') as f:
        for line in f:
            if line.strip(): 
                article = json.loads(line)
                article_text = article["text"]
                input_text = prompt + " " + article_text
                input_tokens = tokenizer.encode(input_text)
                input_token_list.append(len(input_tokens))

    
    # Read the structured outputs from the output JSON file and count the number of tokens for each output, which includes the summary, entities, sentiment, and flags in a JSON format
    output_token_list = []
    with open(output_file, 'r',encoding='utf-8') as f:
        results = json.load(f)
        for result in results:
            extraction = result["extraction"]

            output_text = json.dumps(extraction) # Convert the structured output to a JSON string for token counting
            output_tokens = tokenizer.encode(output_text)
            output_token_list.append(len(output_tokens))


    print(f"EXACT TOKEN CALCULATOR")

    for i in range(len(input_token_list)):
        print(f"Document {i+1}: Input Tokens: {input_token_list[i]}, Output Tokens: {output_token_list[i]}")

    print(f"Input Tokens: Min: {min(input_token_list)}, Max: {max(input_token_list)}, Average: {int(sum(input_token_list)/len(input_token_list))}")
    print(f"Output Tokens: Min: {min(output_token_list)}, Max: {max(output_token_list)}, Average: {int(sum(output_token_list)/len(output_token_list))}")


if __name__ == "__main__":
    count_tokens()