import json

# класс для размещения выходных данных
class ComparisonResult():
    def __init__(self, catalog_id, similarity_score):
        self.catalog_id = catalog_id
        self.similarity_score = similarity_score

# метод для чтения исзодных данных по указанному адресу
def get_file_dictionary(string_to_print: str) -> dict:
    file_path = input(string_to_print)
    file_dict = {}
    file = open(file=file_path, mode="r", encoding="utf-8")
    for line in file:
        items = line.split("\t")
        file_dict[items[0]] = items[1]
    file.close()
    return file_dict

# метод для предобработки исходных данных
def preprocess_file_dictionary(file_dictionary: dict) -> dict:
    for key, value in file_dictionary.items():
        # приведение к нижнему регистру
        value = value.lower()
        for char in value:
            # удаление симолов, которые не являются буквенными, числовыми или пробелами
            if (not char.isalnum()) or (not char.isspace()):
                value.replace(char, "")
        # удаление лишних пробелов
        value = ' '.join(value.split())
        file_dictionary[key] = value

# метод для расчета расстония Левенштейна
def get_levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return get_levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    # единовременно используются только две строки таблицы: текущая и предыдущая
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

# метод для сравнения файлов
def compare_files(similarity_threshold_value: float, use_preprocessing_value: bool, result_file_name: str) -> None:
    # получение путей исходных и итогового файла, подготовка словарей для работы с данными
    first_file_dictionary = get_file_dictionary("Укажите расположение первого файла для сравнения: ")
    second_file_dictionary = get_file_dictionary("Укажите расположение второго файла для сравнения: ")
    destination_folder_path = input("Укажите директорию для добавления выходного файла: ")
    destination_file_path = destination_folder_path + result_file_name
 
    # предобработка исходных данных, если указан соответсвующий флаг
    if use_preprocessing_value:
        preprocess_file_dictionary(first_file_dictionary)
        preprocess_file_dictionary(second_file_dictionary)
    
    # заполнение итоговых данных 
    result_dictionary = {}
    # сравнение каждой строки первого файла с каждой строкой второго файла попарно
    for first_key, first_value in first_file_dictionary.items():
        for second_key, second_value in second_file_dictionary.items():
            # нахождение расстояния Левенштейна 
            levenshtein_distance = get_levenshtein_distance(first_value, second_value)
            # расчет коэффициента схожести
            current_similarity_score = 1 - (levenshtein_distance/(len(first_value) + len(second_value)))
            # добавление элемента в файл, если значение коэффициента схожести выше порога
            if current_similarity_score > similarity_threshold_value:
                if second_key in result_dictionary:
                    result_dictionary[second_key].append(ComparisonResult(first_key, current_similarity_score))
                else:
                    result_dictionary[second_key] = [ComparisonResult(first_key, current_similarity_score)]
    
    # запись итоговых данных в указанную директорию в файл duplicates в формате json
    with open(destination_file_path, 'w') as file_to_write:
        tmp = json.dumps(
            result_dictionary,
            default=lambda o: o.__dict__, 
            indent=2)
        file_to_write.write(tmp)

if __name__ == '__main__':
    # Параметры
    similarity_threshold =  0.8
    use_preprocessing = True
    result_file_name = 'duplicates.json'

    compare_files(similarity_threshold, use_preprocessing, result_file_name)