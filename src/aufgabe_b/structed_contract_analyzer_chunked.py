import time # for time measurement
import json # for handling JSON data
from langchain_ollama import ChatOllama # for interacting with Ollama
from pydantic import BaseModel, Field, ValidationError # for data validation and settings management
from typing import List, Literal # for type annotations
from langchain_core.prompts import ChatPromptTemplate # for creating chat prompts

# Pydantic Schema for structured output of contract analysis
class ContractEvaluation(BaseModel):
    """Represents the structured true/false evaluation of legal clauses in a contract."""
    # I translated the German descriptions and conditions from regelwerk.json into English 
    # so the model knows exactly what keywords to look for. This acts like a cheat sheet for the LLM.
    exclusivity: bool = Field(..., description="True if the contract requires an exclusive business relationship or excludes competitors. Look for: 'exclusive', 'exclusivity', 'sole provider', 'no other party'.")
    non_compete: bool = Field(..., description="True if a party is restricted from competing in a defined period or area. Look for: 'non-compete', 'shall not compete', 'restraint of trade'.")
    change_of_control: bool = Field(..., description="True if special rights (e.g., termination, consent) trigger upon ownership change or takeover. Look for: 'change of control', 'change in ownership', 'merger or acquisition triggers'.")
    anti_assignment: bool = Field(..., description="True if assigning the contract to third parties without consent is prohibited. Look for: 'shall not assign', 'no assignment without consent', 'non-assignable'.")
    auto_renewal: bool = Field(..., description="True if the contract automatically extends without active termination. Look for: 'auto-renew', 'automatically renew', 'unless terminated'.")
    minimum_term: bool = Field(..., description="True if a fixed minimum term before possible termination is defined. Look for: 'initial term of X years', 'minimum term'.")
    termination_convenience: bool = Field(..., description="True if parties can terminate the contract without cause or reason. Look for: 'termination for convenience', 'terminate without cause', 'terminate at will'.")
    most_favored_nation: bool = Field(..., description="True if a party automatically gets the same or better terms granted to third parties. Look for: 'most favored', 'most favoured nation', 'no less favorable terms'.")
    ip_transfer: bool = Field(..., description="True if the contract governs the transfer or licensing of intellectual property. Look for: 'intellectual property', 'IP rights', 'assignment of inventions', 'license to use'.")
    license_grant: bool = Field(..., description="True if an explicit license to use software, brands, or other rights is granted. Look for: 'grants a license', 'hereby licenses', 'right to use'.")
    liability_cap: bool = Field(..., description="True if liability of parties is capped to a maximum amount or specific damage type. Look for: 'limitation of liability', 'liability shall not exceed', 'cap on damages'.")
    insurance_required: bool = Field(..., description="True if a party must maintain specific insurance coverage. Look for: 'shall maintain insurance', 'insurance coverage of at least', 'liability insurance'.")
    audit_rights: bool = Field(..., description="True if a party has the right to inspect the other's books or records. Look for: 'right to audit', 'audit rights', 'inspect books and records'.")
    governing_law: bool = Field(..., description="True if the applicable legal system or jurisdiction is explicitly specified. Look for: 'governed by the laws of', 'shall be construed in accordance with'.")
    minimum_commitment: bool = Field(..., description="True if a party commits to a minimum purchase or revenue within the term. Look for: 'minimum purchase', 'minimum commitment', 'shall purchase no less than'.")
    warranty: bool = Field(..., description="True if express warranties regarding quality, function, or features are provided. Look for: 'warrants that', 'represents and warrants', 'express warranty'.")
   
# Configuration
contracts_file = 'data/aufgabe_b_contracts.jsonl'
model  = 'mistral:7b-instruct-q4_K_M'
output_file = 'data/aufgabe_b_results_chunked.json'

# Load contracts from the input JSONL file
contracts = []
with open(contracts_file, 'r', encoding='utf-8') as f:
    for line in f:
        if line.strip():
            contracts.append(json.loads(line))


# I defined a strict prompt template to force the model to only output true/false JSON without any extra text
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a highly skilled legal assistant. Read the provided contract text and evaluate the presence of 16 specific legal clauses. For each clauses."
    "Respond ONLY in the required JSON format with true/false values for each clause. Do not provide any explanations or additional text. If a clause is not clearly present, mark it as false."),
    ("human", "Here is the contract: {contract}")
])

llm = ChatOllama(model=model, temperature=0)
structured_model = llm.with_structured_output(ContractEvaluation)
chain = prompt | structured_model

# Measure the time and other relevant metrics for the analysis process
start_time = time.time()
results = []
successful_responses = 0
validation_errors = 0

# Iterate through each contract
for index, contract in enumerate(contracts): 
    contract_id = contract["id"]
    raw_text = contract["text"]
    
    
    # Because my GPU only has 5GB VRAM, feeding the whole contract causes a "CUDA Out of Memory" error. 
    # So I decided to chunk the text into 15000 character pieces. I will send them sequentially to avoid crashing the local model.
    chunk_size = 15000
    chunks = [raw_text[i:i + chunk_size] for i in range(0, len(raw_text), chunk_size)]
    
    # store the final extracted tags for this contract in a set to avoid duplicates
    final_extracted_tags = set()
    contract_failed = False
    
    # Every chunk is read separately and the results are aggregated
    for chunk_index, chunk in enumerate(chunks):
       
        try:
            response = chain.invoke({"contract": chunk})
            response_dict = response.model_dump()
            
            # if the response is valid, we add the true tags to the final_extracted_tags set
            for key, value in response_dict.items():
                if value is True:
                    final_extracted_tags.add(key)

        # validation error and general exception handling for each chunk,
        except ValidationError as e:
            validation_errors += 1
            print(f"Validation error for contract {contract_id} chunk {chunk_index}: {e}")

        # If the model crashes completely on one chunk, I break the loop for this contract to save time, 
        # rather than trying the next chunks which will probably fail too.
        except Exception as e:
            print(f"Error processing contract {contract_id} chunk {chunk_index}: {e}")
            contract_failed = True
            break 

    # store the results for this contract after processing all chunks        
    if not contract_failed:
        successful_responses += 1
        results.append({
            "id": contract_id,
            "title": contract.get("title", ""),
            "extracted_tags": list(final_extracted_tags), 
            "total_chunks": len(chunks) 
        })
    else:
        results.append({
            "id": contract_id,
            "title": contract.get("title", ""),
            "extracted_tags": None, 
            "total_chunks": len(chunks),
            "error": "Contract processing failed due to an error in one of the chunks."
        })

# after processing all contracts, calculate the total time taken and the average time per contract
end_time = time.time()
total_time = end_time - start_time
average_time_per_contract = total_time / len(contracts) if contracts else 0

# store the results and metrics in the output JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        "results": results,
        "metrics": {
            "total_time_seconds": total_time,
            "average_time_per_contract_seconds": average_time_per_contract,
            "successful_responses": successful_responses,
            "validation_errors": validation_errors
        }
    }, f, indent=4) 

print(f"Total time taken: {total_time:.2f} seconds")
print(f"Average time per contract: {average_time_per_contract:.2f} seconds")
print(f"Successful responses: {successful_responses}")
print(f"Validation errors: {validation_errors}")

