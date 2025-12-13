import re
import json

class ComparisonResult():
    def __init__(self, catalog_id, similarity_score):
        self.catalog_id = catalog_id
        self.similarity_score = similarity_score

def get_file_dictionary(string_to_print: str) -> dict:
    file_path = input(string_to_print)
    file_dict = {}
    file = open(file=file_path, mode="r", encoding="utf-8")
    for line in file:
        items = line.split("\t")
        file_dict[items[0]] = items[1]
    return file_dict

def preprocess_file_dictionary(file_dictionary: dict) -> dict:
    for key, value in file_dictionary.items():
        value = value.lower()
        for char in value:
            if (not char.isalnum()) or (not char.isspace()):
                value.replace(char, "")
        value= re.sub(' +', ' ', value)
        file_dictionary[key] = value

def get_levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return get_levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            if c1 != c2:
                cost = 2
            else:
                cost = 0
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + cost
            
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def compare_files(similarity_threshold_value: float, use_preprocessing_value: bool) -> None:
    first_file_dictionary = get_file_dictionary("Укажите расположение первого файла для сравнения: ")
    second_file_dictionary = get_file_dictionary("Укажите расположение второго файла для сравнения: ")
    destination_file = input("Укажите расположение выходного файла: ")

    if use_preprocessing_value:
        preprocess_file_dictionary(first_file_dictionary)
        preprocess_file_dictionary(second_file_dictionary)

    result_dictionary = {}
    for first_key, first_value in first_file_dictionary.items():
        for second_key, second_value in second_file_dictionary.items():
            levenshtein_distance = get_levenshtein_distance(first_value, second_value)
            current_similarity_score = 1 - (levenshtein_distance/(len(first_value) + len(second_value)))
            if current_similarity_score > similarity_threshold_value:
                if second_key in result_dictionary:
                    result_dictionary[second_key].append(ComparisonResult(first_key, current_similarity_score))
                else:
                    result_dictionary[second_key] = [ComparisonResult(first_key, current_similarity_score)]

    with open(destination_file, 'w') as file_to_write:
        tmp = json.dumps(
            result_dictionary,
            default=lambda o: o.__dict__, 
            indent=2)
        file_to_write.write(tmp)

if __name__ == '__main__':
    # Параметры
    similarity_threshold =  0.8
    use_preprocessing = True

    compare_files(similarity_threshold, use_preprocessing)