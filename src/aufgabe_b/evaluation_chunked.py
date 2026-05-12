import json # for handling JSON data

def load_json(filepath):
    """Utility function to load JSON data from a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
    
def evaluate_results():
    """This function evaluates the results of the structured contract analysis by comparing the extracted tags against a gold standard.
    It calculates true positives, false positives, true negatives, and false negatives for each of the 16 legal clauses, and then computes precision, recall, and F1 score to assess the performance of the model."""
    
    results_file = 'data/aufgabe_b_results_chunked.json'
    goldstandard_file = 'data/goldstandard.json'

    # I created a list of all 16 tags to properly calculate the True Negatives later
    ALL_TAGS = {
        "exclusivity", "non_compete", "change_of_control", "anti_assignment",
        "auto_renewal", "minimum_term", "termination_convenience", "most_favored_nation",
        "ip_transfer", "license_grant", "liability_cap", "insurance_required",
        "audit_rights", "governing_law", "minimum_commitment", "warranty"
    }

    # load results and gold standard data with error handling
    try:
        results_data = load_json(results_file)
        goldstandard_data = load_json(goldstandard_file)
       
    except Exception as e:
        print(f"Error loading JSON files: {e}")
        return

    # I saw that my results data is wrapped in a "results" key with metrics, so I extract the list here
    if isinstance(results_data, dict) and "results" in results_data:
        results_list = results_data["results"]
    else:
        results_list = results_data

    # I noticed the goldstandard is wrapped in an "annotations" key, so I extract the list directly to avoid string index errors
    if isinstance(goldstandard_data, dict) and "annotations" in goldstandard_data:
        goldstandard_list = goldstandard_data["annotations"]
    else:
        goldstandard_list = goldstandard_data
        
    # create a dictionary from the gold standard list for easy lookup by contract_id
    gold_dict = {}
    for item in goldstandard_list:
        if isinstance(item, dict) and "contract_id" in item: # ensure that the item is a dictionary and contains the expected key
            gold_dict[item["contract_id"]] = item.get("expected_tags", [])

    true_positives = 0 # count of correctly identified tags 
    false_positives = 0 # count of incorrectly identified tags 
    true_negatives = 0 # count of correctly identified absence of tags
    false_negatives = 0 # count of incorrectly identified absence of tags

    evaluated_contracts = 0 # count of contracts that were evaluated against the gold standard

    # iterate through the results and compare the predicted tags with the actual tags from the gold standard, while counting true positives, false positives, true negatives, and false negatives for each clause
    for result in results_list:
        contract_id = result.get("id") # get the contract id from the result

        if contract_id not in gold_dict: # if the contract id not found in the gold standard
            continue    
        else:
            evaluated_contracts += 1 
           
            # I use Python sets because it makes mathematical operations (intersection, difference) extremely easy and fast
            predicted_tags = set(result.get("extracted_tags", [])) #predicted tags from the model output, converted to a set for easier comparison
            actual_tags = set(gold_dict[contract_id]) # actual tags from the gold standard, converted to a set for easier comparison

            # calculate metrics for each clause using set operations 
            tp_set = predicted_tags.intersection(actual_tags) # tags that are correctly identified as present in the contract
            fp_set = predicted_tags.difference(actual_tags) # tags that are incorrectly identified as present in the contract
            fn_set = actual_tags.difference(predicted_tags) # tags that are incorrectly identified as absent in the contract
            tn_set = ALL_TAGS.difference(predicted_tags.union(actual_tags)) # tags that are correctly identified as absent in the contract

            true_positives += len(tp_set) # count of true positives is increased by the number of tags in the tp_set
            false_positives += len(fp_set) # count of false positives is increased by the number of tags in the fp_set
            false_negatives += len(fn_set) # count of false negatives is increased by the number of tags in the fn_set
            true_negatives += len(tn_set) # count of true negatives is increased by the number of tags in the tn_set

    # calculate precision, recall, and F1 score based on the counts of true positives, false positives, true negatives, and false negatives
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0 
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

    # Output Table
    print(f"Evaluated Contracts: {evaluated_contracts}")
    print(f"True Positives: {true_positives}")
    print(f"False Positives: {false_positives}")
    print(f"True Negatives: {true_negatives}")
    print(f"False Negatives: {false_negatives}")
    print(f"Precision: {precision:.4f} ({precision:.2%})")
    print(f"Recall: {recall:.4f} ({recall:.2%})")
    print(f"F1 Score: {f1_score:.4f} ({f1_score:.2%})")

if __name__ == "__main__":
    evaluate_results()