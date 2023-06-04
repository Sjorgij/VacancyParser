import os
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable
  

def count_vacs(name, salary, vac_info):
    for vac in vac_info.keys():
        if vac.lower() in name.lower():
            vac_info[vac]["vacancies_found"] += 1
            if salary:
                vac_info[vac]["average_salary"] += int(salary)
                vac_info[vac]["vacancies_processed"] += 1


def parse_vacs_hh(url, params, vac_info):
    response = requests.get(f"{url}/vacancies", params=params)
    response.raise_for_status()
    for page in range(response.json()["pages"]):
        params["page"] = page
        response = requests.get(f"{url}/vacancies", params=params)
        response.raise_for_status()
        for vacancy in response.json()["items"]:
            count_vacs(vacancy["name"], predict_rub_salary_hh(vacancy["salary"]), vac_info)
    for vac in vac_info:
        if vac_info[vac]["average_salary"] == 0: continue
        vac_info[vac]["average_salary"] = int(vac_info[vac]["average_salary"] / vac_info[vac]["vacancies_processed"])  


def parse_vacs_sj(url, header, params, vac_info):
    response = requests.get(url, headers = header, params=params)
    response.raise_for_status()
    while response.json()["more"]:
        response = requests.get(url, headers = header, params=params)
        response.raise_for_status()
        for vacancy in response.json()["objects"]:
            count_vacs(vacancy["profession"], predict_rub_salary_sj(vacancy), vac_info)
        params["page"] += 1
    for vac in vac_info:
        if vac_info[vac]["average_salary"] == 0: continue
        vac_info[vac]["average_salary"] = int(vac_info[vac]["average_salary"] / vac_info[vac]["vacancies_processed"])  
    

def predict_rub_salary_hh(vacancy):
    if vacancy["currency"] != "RUR": return None
    salary = predict_rub_salary(vacancy["from"], vacancy["to"])
    return salary


def predict_rub_salary_sj(vacancy):
    if vacancy["currency"] != "rub": return None
    salary = predict_rub_salary(vacancy["payment_from"], vacancy["payment_to"])
    return salary


def predict_rub_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to)/2
    elif salary_from:
        return salary_from * 1.2
    else:
        return salary_to * 0.8


def draw_table(data, title):
    result = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата"
        ]
    ]
    for lang in data.keys():
        result.append([lang, *list(data[lang].values())])
    print(AsciiTable(result, title).table)

  

def main():
    URL_hh = "https://api.hh.ru"
    URL_sj = "https://api.superjob.ru/2.0/vacancies"
    params_hh = {
        "area": "1",
        "professional_role": "96",
        "only_with_salary": True,
        "period": 31
    }
    params_sj = {
        "town": "Москва",
        "catalogues": 48,
        "page": 0
    }
    header = {
        "X-Api-App-Id": os.environ["SUPERJOB_API_TOKEN"]
    }
    vac_info_hh = {
        "JavaScript": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Python": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Java": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "C/С++": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "PHP": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "C#": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Swift": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Kotlin": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Go": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Ruby": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Rust": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "1с": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        }
    }

    vac_info_sj = {
        "JavaScript": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Python": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Java": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "C/С++": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "PHP": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "C#": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Swift": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Kotlin": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Go": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Ruby": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "Rust": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        },
        "1с": {
            "vacancies_found": 0,
            "vacancies_processed": 0,
            "average_salary": 0
        }
    }
  
    parse_vacs_hh(URL_hh, params_hh, vac_info_hh)
    parse_vacs_sj(URL_sj, header, params_sj, vac_info_sj)

    draw_table(vac_info_hh, "HeadHunter Moscow")
    draw_table(vac_info_sj, "SuperJob Moscow")


if __name__ == "__main__":
    load_dotenv()
    main()