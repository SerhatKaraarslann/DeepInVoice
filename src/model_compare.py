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
    summary_one_sentence: str = Field(...,description="Summary in one sentence. Maximum 20 words limit!")
    entities : List[Entity]
    sentiment : Literal["positive","neutral","negative"]
    flags: List[str] = Field(..., description='List of potential issues or concerns in the article: ["is_tech", "is_political", "has_financial_impact", "is_sport", "is_entertainment", "is_other"]')

# 3 test articles from aufgabe_a_data.jsonl for testing the models
test_article = [
    "Indian board plans own telecast of Australia series The Indian cricket board said on Wednesday it was making arrangements on its own to broadcast next month #39;s test series against Australia, which is under threat because of a raging TV rights dispute.",
    "Stocks Higher on Drop in Jobless Claims A sharp drop in initial unemployment claims and bullish forecasts from Nokia and Texas Instruments sent stocks slightly higher in early trading Thursday.",
    "Nuggets 112, Raptors 106 Carmelo Anthony scored 30 points and Kenyon Martin added 24 points and 16 rebounds, helping the Denver Nuggets hold off the Toronto Raptors 112-106 Wednesday night."
]

# List of models to test, including both q4_K_M and q8_0 quantization formats for each base model
models_to_test = [
    "llama3.1:8b-instruct-q4_K_M", 
    "llama3.1:8b-instruct-q8_0",
    "mistral:7b-instruct-q4_K_M",
    "mistral:7b-instruct-q8_0",
    "qwen2.5:7b-instruct-q4_K_M",
    "qwen2.5:7b-instruct-q8_0"
]

# Dictionary to store results for each model
results = {} 

for model_name in models_to_test:
    print(f"Testing model: {model_name}") 

    # Define the prompt template for the article extraction task
    prompt = ChatPromptTemplate.from_messages([
        ("system","You are a helpful assistant for extracting information from news articles. You will be given an article and you need to provide a one-sentence summary, identify key entities, determine the sentiment of the article, and flag any potential issues or concerns based on the content of the article. Please ensure that the one-sentence summary does not exceed 20 words."),
        ("human","Here is the article: {article}")
    ])

    # Initialize the ChatOllama model with the specified model name and temperature 0 for deterministic output
    model = ChatOllama(model=model_name, temperature=0)
    structured_model = model.with_structured_output(ArticleExtraction) # Wrap the model with structured output validation using the ArticleExtraction schema

    chain = prompt | structured_model

    # Measure the time, count successful responses, validation errors, and compliance with the 20-word limit for each model
    start_time = time.time()

    successful_responses = 0
    validation_errors = 0
    word_limit_success = 0
    
    # Iterate test articles
    for article in test_article:
        try :
            # Invoke the chain with the article and validate the response against the ArticleExtraction schema
            response = chain.invoke(
                {"article": article}
            )
            successful_responses += 1 # Count successful responses that passed schema validation
           
            # Check if the one-sentence summary complies with the 20-word limit and count successes
            word_count = len(response.summary_one_sentence.split())
            if word_count <= 20:
                word_limit_success += 1

        # Handle validation errors and other exceptions
        except ValidationError as e:
            validation_errors += 1
            print(f"Validation error for model {model_name} on article: {article}")
            print(e.json()) # Print detailed validation errors in JSON format for better readability
        
        except Exception as e:
            print(f"Error for model {model_name} on article: {article}")
            print(str(e))

    # calculate the average response time for the model and store all relevant metrics in the results dictionary    
    end_time = time.time()
    average_time = (end_time - start_time) / len(test_article)
    results[model_name] = {
        "Average_Response_Time_sec": round(average_time, 2),
        "Successful_Extractions": f"{successful_responses}/{len(test_article)}",
        "Schema_Validation_Errors": validation_errors,
        "Max_20_Words_Passed": f"{word_limit_success}/{successful_responses if successful_responses > 0 else 1}"
    }

print(f"THE RESULTS OF BENCHMARK")
print(json.dumps(results, indent=4)) # Print the results in a formatted JSON structure for better readability
        

import matplotlib.pyplot as plt

# Prepare data for visualization
models = list(results.keys()) # Extract model names from results dictionary for plotting
response_times = [results[model]["Average_Response_Time_sec"] for model in models]   # Extract average response times for each model to plot the performance comparison

# extract the number of successful extractions 
word_success_rates = [int(results[model]["Max_20_Words_Passed"].split('/')[0]) for model in models] 
total_articles = len(test_article)

# 2 subplots. One for the time comparison and one for the successful extractions comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# bar chart with the different colors for Q4 and Q8 models
colors_time = ['#ff9999' if 'q8' in m else '#66b3ff' for m in models]
bars1 = ax1.barh(models, response_times, color=colors_time)
ax1.set_xlabel('Average Response Time (Seconds) - Lower is Better', fontsize=11, fontweight='bold')
ax1.set_title('Model Inference Speed (Performance)', fontsize=14)
ax1.invert_yaxis() 

# Add data labels to the bars to show the exact response time values for better readability
for bar in bars1:
    ax1.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2, # Format the response time to one decimal place and add 's' for seconds, positioned to the right of the bar
             f'{bar.get_width():.1f}s', va='center', fontsize=10)

bars2 = ax2.barh(models, word_success_rates, color='#99ff99')
ax2.set_xlabel(f'Successful Extractions (Max: {total_articles}) - Higher is Better', fontsize=11, fontweight='bold')
ax2.set_title('Constraint Compliance (20-Word Limit)', fontsize=14)
ax2.set_xlim(0, total_articles + 0.5) 
ax2.invert_yaxis()

for bar in bars2:
    ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, # Format the success rate to show the number of successful extractions and the total number of articles, positioned to the right of the bar
             f'{int(bar.get_width())}/{total_articles}', va='center', fontsize=10)

plt.tight_layout() 
plt.savefig('benchmark_results.png', dpi=300, bbox_inches='tight') # save the results as a png datei