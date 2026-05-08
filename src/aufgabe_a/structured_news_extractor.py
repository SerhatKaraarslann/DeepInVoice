import time # for time measurement
import json # for handling JSON data
from langchain_ollama import ChatOllama # for interacting with Ollama
from pydantic import BaseModel, Field, ValidationError # for data validation and settings management
from typing import List, Literal # for type annotations
from langchain_core.prompts import ChatPromptTemplate # for creating chat prompts

class Entity(BaseModel):
    """Represents a key entity extracted from the article"""
    name: str = Field(description="The name of the entity")
    type: str = Field(description="The type of the entity")

class ArticleExtraction(BaseModel):
    """Represents the structured output of the article extraction process like task output schema"""
    summary_one_sentence: str = Field(...,description="Summary in one sentence. Must be 20 words or less!")
    entities : List[Entity]
    sentiment : Literal["positive","neutral","negative"]
    flags: List[Literal["is_tech", "is_political", "has_financial_impact", "is_sport", "is_entertainment", "is_other"]] = Field(..., description='Select appropriate flags from the exact list provided.')

# Configuration 
input_file = 'data/aufgabe_a_data.jsonl' 
output_file = 'data/aufgabe_a_results.json'
model  = 'mistral:7b-instruct-q4_K_M' 

# Load articles from the input JSONL file and store them in a list for processing
articles = []
with open(input_file, 'r',encoding='utf-8') as f:
    for line in f:
        if line.strip(): 
            articles.append(json.loads(line))

# I have defined a strict prompt template to ensure that the results fit the schema requirements, especially the 20-word limit for the summary and the flags.
prompt = ChatPromptTemplate.from_messages([
        ("system","""You are a helpful assistant for extracting information from news articles. You must follow these strict rules:
        SUMMARY: Provide a one-sentence summary. It MUST be extremely concise, aiming for 10-15 words. NEVER exceed 20 words.
        FLAGS: ONLY use the exact predefined categories provided in the schema. Do not invent new flags. Each flag must be UNIQUE.
        ENTITIES: Identify key entities and their types."""),
        ("human","Here is the article: {article}")
    ])

llm = ChatOllama(model=model, temperature=0)
structured_model = llm.with_structured_output(ArticleExtraction)
chain = prompt | structured_model

# Measure the time and other relevant metrics for the extraction process
start_time = time.time()
successful_responses = 0
validation_errors = 0
word_limit_success = 0

results = [] # Results list to store the structured outputs and any errors 

# Iterate through each article 
for index, article in enumerate(articles):
    article_text = article["text"] 
    article_id = article["id"]

    try:
        # Invoke the chain with the article text and store the structured response, while counting successful responses and validation errors
        response = chain.invoke(
            {           
             "article": article_text
            }
        )
        successful_responses += 1

        # I saw that some responses has the same flag multiple times, so I added a check to count only unique flags for the word limit success metric and now I use set to ensure that every response has only unique flags.
        response.flags = list(set(response.flags))

        word_count = len(response.summary_one_sentence.split())
        if word_count <= 20:
            word_limit_success += 1

        results.append({
            "id": article_id,
            "extraction":response.model_dump() # Store the structured output of the extraction process for the article, including the summary, entities, sentiment, and flags in a dictionary format for later analysis and output to a JSON file
        })

    # handle errors and store them in the results list with details
    except ValidationError as e:
        validation_errors += 1
        print(f"Validation error for article ID {article_id}")
        results.append({
            "id": article_id,
            "error": "ValidationError",
            "details": json.loads(e.json())
        })
    except Exception as e:
        print(f"Error for article ID {article_id}")
        results.append({
            "id": article_id,
            "error": "Exception",
            "details": str(e)
        })

# After processing all articles, calculate the total time taken and the average response time per article
end_time = time.time()
average_time = (end_time - start_time) / len(articles)

# Store the overall results and metrics in a dictionary for output to a JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4, ensure_ascii=False)


print(f"EXTRACTION SUMMARY")
print(f"Total Time: {round(end_time - start_time, 2)} seconds")
print(f"Average Response Time: {round(average_time, 2)} seconds/article")
print(f"Successful Extractions: {successful_responses}/{len(articles)}")
print(f"Schema Validation Errors: {validation_errors}")
print(f"Max 20 Words Passed: {word_limit_success}/{successful_responses if successful_responses > 0 else 1}")