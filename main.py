import os
import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def pass_captcha(response):
    backurl = response.url
    response = response.json()
    if response["errors"][0]["value"] == "captcha_required":
        print(f"Для продолжения работы программы необходимо пройти капчу. Ссылка:\n{response['errors'][0]['captcha_url']}&backurl={backurl}")
        while True:
            if "y" in input("Капча решена Yes/No\n").lower():
                break
    else:
        from xmlrpc.client import ResponseError
        raise ResponseError(response["errors"][0]["value"])


def fetch_vacancies_from_hh(url, params, language):
    vacancies_found = 0
    vacancies_processed = 0
    total_salary = 0
    params["text"] = language
    pages = 1
    while params["page"] < pages:
        response = requests.get(f"{url}/vacancies", params=params)
        if response.status_code == 403:
            pass_captcha(response)
            continue
        response.raise_for_status()
        response = response.json()
        pages = response["pages"]
        params["page"] += 1
        response = response["items"]
        for vacancy in response:
            vacancies_found += 1
            salary = predict_rub_salary_hh(vacancy["salary"])
            if salary:
                vacancies_processed += 1
                total_salary += salary
    if vacancies_processed:
        avg_salary = int(total_salary / vacancies_processed)
    else:
        avg_salary = 0
    job_stats_by_language = {
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": avg_salary
    }
    return job_stats_by_language.copy()


def fetch_vacancies_from_sj(url, header, params, language):
    vacancies_found = 0
    vacancies_processed = 0
    total_salary = 0
    params["keyword"] = language
    more = True
    while more:
        response = requests.get(url, headers=header, params=params)
        response.raise_for_status()
        response = response.json()
        for vacancy in response["objects"]:
            vacancies_found += 1
            salary = predict_rub_salary_sj(vacancy)
            if salary:
                vacancies_processed += 1
                total_salary += salary
        params["page"] += 1
        more = response["more"]
    if vacancies_processed:
        avg_salary = int(total_salary / vacancies_processed)
    else:
        avg_salary = 0
    job_stats_by_language = {
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_processed,
        "average_salary": avg_salary
    }
    return job_stats_by_language.copy()


def predict_rub_salary_hh(vacancy):
    if vacancy["currency"] != "RUR":
        return None
    salary = predict_rub_salary(vacancy["from"], vacancy["to"])
    return salary


def predict_rub_salary_sj(vacancy):
    if vacancy["currency"] != "rub":
        return None
    salary = predict_rub_salary(vacancy["payment_from"], vacancy["payment_to"])
    return salary


def predict_rub_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    else:
        return salary_to * 0.8


def draw_table(jobs_table, title):
    table = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата"
        ]
    ]
    for lang in jobs_table.keys():
        table.append([lang, *list(jobs_table[lang].values())])
    return AsciiTable(table, title).table


def main():
    load_dotenv()
    url_hh = "https://api.hh.ru"
    url_sj = "https://api.superjob.ru/2.0/vacancies"
    hh_moscow_id = 1
    hh_programmer_role_id = 96
    days_in_one_month = 31
    sj_programmer_catalogue_id = 48
    params_hh = {
        "area": hh_moscow_id,
        "professional_role": hh_programmer_role_id,
        "only_with_salary": True,
        "period": days_in_one_month,
        "page": 0
    }
    params_sj = {
        "town": "Москва",
        "catalogues": sj_programmer_catalogue_id,
        "page": 0
    }
    header = {
        "X-Api-App-Id": os.environ["SUPERJOB_API_TOKEN"]
    }
    languages = (
        "JavaScript",
        "Python",
        "Java",
        "C/С++",
        "PHP",
        "C#",
        "Swift",
        "Kotlin",
        "Go",
        "Ruby",
        "Rust",
        "1с"
    )

    vacancies_on_hh = dict()
    vacancies_on_sj = dict()
    for lang in languages:
        vacancies_on_hh[lang] = fetch_vacancies_from_hh(url_hh, params_hh.copy(), lang)
        vacancies_on_sj[lang] = fetch_vacancies_from_sj(url_sj, header, params_sj.copy(), lang)

    print(draw_table(vacancies_on_hh, "HeadHunter Moscow"))
    print(draw_table(vacancies_on_sj, "SuperJob Moscow"))


if __name__ == "__main__":
    main()
