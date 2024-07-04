import re
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json


class BrokerInfoScraper:
    def __init__(self, crd_number):
        self.crd_number = crd_number
        self.roles = {
            "IA": "Investment Advisor",
            "B": "Broker",
            "PR": "Previously Registered",
        }
        self.broker_info = {}

    def scrape_info(self):
        url = f"https://brokercheck.finra.org/individual/summary/{self.crd_number}"
        options = webdriver.ChromeOptions()
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        options.add_argument("accept-language=en-US,en;q=0.9")
        options.add_argument("--disable-features=NetworkService")
        options.add_argument("headless")

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )

        driver.get(url)
        # Wait for the loader to disappear and actual content to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "investor-tools-big-name"))
            )
        except:
            print("Content did not load in time")
            driver.quit()
            return None

        # Adding an extra delay to ensure everything is loaded
        time.sleep(4)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        try:
            self.extract_broker_info(soup)
        except Exception as e:
            print(f"Error extracting broker info: {e}")
            traceback.print_exc()
            return None

    def extract_broker_info(self, soup):
        # Extracting the name
        name_tag = soup.find("investor-tools-big-name")
        self.broker_info["name"] = (
            name_tag.find("span", class_="text-lg").text.strip() if name_tag else "N/A"
        )

        # Extracting the address
        address_div = soup.find("investor-tools-address")
        self.broker_info["address"] = (
            address_div.get_text(strip=True) if address_div else "N/A"
        )

        # Extracting years of experience
        experience_spans = soup.find_all("span", class_="text-sm")
        for span in experience_spans:
            if "Years of Experience" in span.text:
                experience_number_span = span.find_previous(
                    "span",
                    class_="sm:text-lg sm:font-semibold text-3xl ng-star-inserted",
                )
                if experience_number_span:
                    self.broker_info["experience"] = experience_number_span.text.strip()
                else:
                    self.broker_info["experience"] = "N/A"
                break
            else:
                self.broker_info["experience"] = "N/A"

        # Extracting firms
        firm_spans = soup.find_all("span", class_="text-sm")
        for span in firm_spans:
            if "Firms" in span.text:
                firm_number_span = span.find_previous(
                    "span",
                    class_="sm:text-lg sm:font-semibold text-3xl ng-star-inserted",
                )
                if firm_number_span:
                    self.broker_info["firms"] = firm_number_span.text.strip()
                else:
                    self.broker_info["firms"] = "N/A"
                break
        else:
            self.broker_info["firms"] = "N/A"

        # Extracting exams passed
        for span in experience_spans:
            if "Exams Passed" in span.text:
                exam_number_span = span.find_previous(
                    "span",
                    class_="sm:text-lg sm:font-semibold text-3xl ng-star-inserted",
                )
                if exam_number_span:
                    self.broker_info["exams_passed"] = exam_number_span.text.strip()
                else:
                    self.broker_info["exams_passed"] = "N/A"
                break
        else:
            self.broker_info["exams_passed"] = "N/A"

        # Extracting state licenses
        for span in experience_spans:
            if "State Licenses" in span.text:
                license_number_span = span.find_previous(
                    "span",
                    class_="sm:text-lg sm:font-semibold text-3xl ng-star-inserted",
                )
                if license_number_span:
                    self.broker_info["state_licenses"] = (
                        license_number_span.text.strip()
                    )
                else:
                    self.broker_info["state_licenses"] = "N/A"
                break
        else:
            self.broker_info["state_licenses"] = "N/A"
        # Extracting disclosures
        disclosures_div = soup.find("div", class_="flex-1 flex flex-col justify-center")
        if disclosures_div:
            disclosures_text = disclosures_div.find(
                "span", class_="sm:text-lg sm:font-semibold text-3xl ng-star-inserted"
            ).text.strip()
            self.broker_info["disclosures"] = disclosures_text
        else:
            self.broker_info["disclosures"] = "N/A"

        # Extracting firms
        firms_div = soup.find_all(
            "div",
            class_="flex flex-row items-center gap-1 sm:my-0 sm:h-auto my-2 h-9 ng-star-inserted",
        )
        self.broker_info["firms"] = "N/A"
        for div in firms_div:
            span_texts = div.find_all("span")
            if span_texts and "Firms" in span_texts[-1].text:
                self.broker_info["firms"] = span_texts[0].text.strip()
                break

        # Extracting exams passed
        # self.broker_info['exams_passed'] = experience_tags[1].find_all('span', class_='ng-star-inserted')[0].text.strip() if len(experience_tags) > 1 and len(experience_tags[1].find_all('span', class_='ng-star-inserted')) > 0 else "N/A"

        # Extracting state licenses
        # self.broker_info['state_licenses'] = experience_tags[1].find_all('span', class_='ng-star-inserted')[1].text.strip() if len(experience_tags) > 1 and len(experience_tags[1].find_all('span', class_='ng-star-inserted')) > 1 else "N/A"

        # Extracting timeline data
        self.broker_info["timeline"] = []
        timeline_tags = soup.find_all("g", class_="group")
        for tag in timeline_tags:
            firm_info = tag.find("text", class_="firm-info")
            years_info = tag.find("text", class_="years")
            if firm_info and years_info:
                firm = firm_info.text.strip()
                years = years_info.text.strip()
                self.broker_info["timeline"].append({"firm": firm, "years": years})

        # Extracting exams data
        self.broker_info["exams"] = []
        category_divs = soup.find_all("div", class_="px-3 my-2 ng-star-inserted")
        for category_div in category_divs:
            category_tag = category_div.find(
                "h2", class_="flex-1 text-base text-gray-80"
            )
            if category_tag:
                category_name = category_tag.text.strip()
                exams_list = []
                exam_divs = category_div.find_all(
                    "div", class_="flex flex-row items-center my-3 ng-star-inserted"
                )
                for exam_div in exam_divs:
                    exam_name = exam_div.find("span", class_="flex-1").text.strip()
                    exam_date = exam_div.find("span", class_="w-44").text.strip()
                    exams_list.append({"name": exam_name, "date": exam_date})
                self.broker_info["exams"].append(
                    {"category": category_name, "exams": exams_list}
                )

        # Extracting state registrations
        self.broker_info["state_registrations"] = []
        state_section = soup.find("div", class_="flex-1 ng-star-inserted")
        if state_section:
            state_divs = state_section.find_all(
                "div", class_="flex flex-1 flex-row flex-wrap"
            )
            for div in state_divs:
                state_name = (
                    div.find("span", class_="text-sm w-32").text.strip()
                    if div.find("span", class_="text-sm w-32")
                    else "N/A"
                )
                if state_name != "N/A":
                    self.broker_info["state_registrations"].append(state_name)

        # Extracting SRO registrations
        self.broker_info["sro_registrations"] = []
        sro_section = soup.find(
            "div", class_="w-4/12 xs:w-full sm:w-full ng-star-inserted"
        )
        if sro_section:
            sro_divs = sro_section.find_all(
                "div", class_="flex flex-row items-center gap-2 py-3"
            )
            for div in sro_divs:
                sro_name = (
                    div.find("span", class_="flex-1 text-sm").text.strip()
                    if div.find("span", class_="flex-1 text-sm")
                    else "N/A"
                )
                if sro_name != "N/A":
                    self.broker_info["sro_registrations"].append(sro_name)

        # Extracting current registrations
        self.broker_info["current_registrations"] = []
        current_registrations_section = soup.find(
            "investor-tools-current-registrations"
        )
        if current_registrations_section:
            registration_divs = current_registrations_section.find_all(
                "div", class_="flex flex-row items-start p-2 gap-1 ng-star-inserted"
            )
            for div in registration_divs:
                avatar_tag = div.find("investor-tools-avatar")
                avatar_text = avatar_tag.text.strip() if avatar_tag else "N/A"
                firm_tag = div.find("investor-tools-scoped-link").find(
                    "a", class_="ng-star-inserted"
                )
                firm_name = firm_tag.text.strip() if firm_tag else "N/A"
                crd_number = (
                    firm_tag["href"].split("/")[-1]
                    if firm_tag and "href" in firm_tag.attrs
                    else "N/A"
                )
                if not crd_number:
                    crd_number_match = re.search(r"\(CRD#:(\d+)\)", firm_name)
                    crd_number = (
                        crd_number_match.group(1) if crd_number_match else "N/A"
                    )
                address_tag = div.find("investor-tools-address")
                address = address_tag.text.strip() if address_tag else "N/A"
                registration_date_tag = div.find("div", class_="text-sm text-gray-75")
                registration_date = (
                    registration_date_tag.text.strip()
                    if registration_date_tag
                    else "N/A"
                )

                registration_info = {
                    "firm_name": firm_name,
                    "crd_number": crd_number,
                    "address": address,
                    "registration_date": registration_date,
                    "as_a": self.roles[avatar_text],
                }

                self.broker_info["current_registrations"].append(registration_info)

        # Extracting previous registrations
        self.broker_info["previous_registrations"] = []
        previous_registrations_section = soup.find(
            "investor-tools-previous-registrations"
        )
        if previous_registrations_section:
            table = previous_registrations_section.find("table")
            if table:
                rows = table.find_all("tr", class_="ng-star-inserted")

                for row in rows:
                    avatar_tag = row.find("investor-tools-avatar")
                    avatar_text = avatar_tag.text.strip() if avatar_tag else "N/A"
                    registration_period_tag = row.find(
                        "td", class_="pt-3 pr-3 align-top text-sm w-44"
                    )
                    registration_period = (
                        registration_period_tag.text.strip()
                        if registration_period_tag
                        else "N/A"
                    )
                    firm_tag = row.find("investor-tools-scoped-link").find(
                        "a", class_="ng-star-inserted"
                    )
                    firm_name = firm_tag.text.strip() if firm_tag else "N/A"
                    crd_number = firm_tag["href"].split("/")[-1] if firm_tag else "N/A"
                    location_tag = row.find("td", class_="pt-3 align-top text-sm w-32")
                    location = location_tag.text.strip() if location_tag else "N/A"

                    registration_info = {
                        "as_a": self.roles[avatar_text],
                        "registration_period": registration_period,
                        "firm_name": firm_name,
                        "crd_number": crd_number,
                        "location": location,
                    }

                    self.broker_info["previous_registrations"].append(registration_info)

    def get_broker_info(self):
        return self.broker_info
