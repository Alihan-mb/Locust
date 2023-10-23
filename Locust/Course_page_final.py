import re
import time

from locust import HttpUser, SequentialTaskSet, task, between, FastHttpUser, constant
from bs4 import BeautifulSoup
import logging
from locust.exception import StopUser

hhhh = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8', 'Cache-Control': 'no-cache',
    'Connection': 'keep-alive', 'Content-Length': '221', 'Content-Type': 'application/x-www-form-urlencoded',
    'Host': '10.70.115.108', 'Origin': 'http://10.70.115.108', 'Pragma': 'no-cache',
    'Referer': 'http://10.70.115.108/Auth/Login', 'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'}

started_users = 0
class userbehaviour(SequentialTaskSet):
    def __init__(self, parent):
        super().__init__(parent)
        self.antiforgery_cookie = ""
        self.data = None

    def on_start(self):
        global started_users
        started_users += 1
        print(f"{self.__class__.__name__} started, total started users: {started_users}")

        resp = self.client.get("/Auth/Login", name="launching the login page",
                               headers={"Accept": "text/html; charset=utf-8"})
        for_token = re.findall("<input name=\"__RequestVerificationToken\" type=\"hidden\" value=\"(.*?)\" />",
                               resp.text, re.DOTALL)
        token = for_token[0]
        self.data = {
            "username": "alikhan",
            "password": "LR74PggznZW4vWd",
            "__RequestVerificationToken": token
        }
        params = [(b'Login', b'alikhan'), (b'Password', b'LR74PggznZW4vWd'),
                  (b'__RequestVerificationToken', f'{token}')]

        with self.client.post("/Auth/Login", data=self.data, name="logging_in", allow_redirects=True,
                              params=params,
                              catch_response=True) as resp1:
            if resp1.status_code == 200:
                resp1.success()
            else:
                resp1.failure("The status code is " + str(resp1.status_code))

                raise StopUser

    @task(1)
    def launching(self):
        with self.client.get("/Courses/View", name="main page", catch_response=True) as main_page:
            if ("alikhan") in main_page.text and main_page.status_code == 200:
                main_page.success()
            else:
                main_page.failure(f"Status code is {main_page.status_code} or the username is wrong")

    @task(1)
    def switching_to6th_page(self):
        parameters = {"currentPage": "6",
                      "pageSize": "8",
                      "keyword": '',
                      "availableToMe": "false"}
        with self.client.get("/Courses/View", name="page 6", params=parameters,
                             headers={"header-name": "XMLHttpRequest"}, catch_response=True) as page6:
            # soup = BeautifulSoup(page6.text, "html.parser")
            # course_names = soup.find_all("a")
            #
            # expected_text = "Квест «По следам злоумышленника»"
            # found = any(anchor.text.strip() == expected_text for anchor in course_names)
            if page6.status_code == 200:
                page6.success()
            else:
                page6.failure("It's not here")

    @task(1)
    def course_page(self):
        with self.client.get("/Courses/Detail/133", name="course_page", catch_response=True) as course_page:
            if course_page.url != "http://10.70.115.108/Courses/Detail/133":
                course_page.failure(f"Url is different {course_page.url}")
            else:
                course_page.success()
    @task(1)
    def page_theme(self):
        with self.client.get("/Themes/Detail/806", name="page_theme", catch_response=True) as page_theme:
            if page_theme.status_code != 200:
                page_theme.failure(f"status code is {page_theme.status_code}")
            elif page_theme.url != "http://10.70.115.108/Themes/Detail/806":
                page_theme.failure(f"url is {page_theme.url}")
            elif ("Структура Linux") not in page_theme.text:
                page_theme.failure("Text not present")
            else:
                page_theme.success()

    @task(1)
    def quizz(self):
        self.client.get("/Themes/Quiz?themeId=806", name="Опросник")


class myuser(FastHttpUser):
    tasks = [userbehaviour]
    wait_time = between(2, 4)
    host = "http://10.70.115.108"

