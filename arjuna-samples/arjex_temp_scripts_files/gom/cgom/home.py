'''
This file is a part of Arjuna
Copyright 2015-2020 Rahul Verma

Website: www.RahulVerma.net

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from enum import Enum, auto
from .basepage import WPBasePage
from .dashboard import DashboardPage

class HomePage(WPBasePage):

    class loc(Enum):
        login = auto()
        password = auto()
        submit = auto()
        view_site = auto()

    def login(self, user, pwd):
        self.element(self.loc.login).text = user
        self.element(self.loc.password).text = pwd
        self.element(self.loc.submit).click()

        self.element(self.loc.view_site).wait_until_visible()
        return DashboardPage(self)

    def login_with_default_creds(self):
        user, pwd = self.config.get_user_option_value("wp.users.admin").split_as_str_list()
        return self.login(user, pwd)
