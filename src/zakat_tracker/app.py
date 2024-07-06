"""
Personal Accounting Software using Zakat way for all transactions from the beginning to the end
"""

import re
import os
import toga
import toga.sources
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from zakat import ZakatTracker
from datetime import datetime
from .i18n import i18n, Lang
from .config import Config
import pathlib

class ZakatLedger(toga.App):
    def startup(self):

        self.icon = toga.Icon.APP_ICON

        # set database

        if not os.path.exists(self.paths.data):
            pathlib.Path.mkdir(self.paths.data)
        db_path = os.path.join(self.paths.data, 'zakat.pickle')
        print(f'db: {db_path}')
        self.db = ZakatTracker(db_path)

        # load config

        if not os.path.exists(self.paths.config):
            pathlib.Path.mkdir(self.paths.config)
        config_path = os.path.join(self.paths.config, 'config.json')
        print(f'config: {config_path}')
        self.config = Config(config_path)
        
        # set translations

        if not os.path.exists(config_path):
            self.i18n = i18n(Lang.AR_EN)
            self.config.set('lang', Lang.AR_EN.value)
        else:
            self.i18n = i18n(Lang(self.config.get('lang')))

        self.dir = self.i18n.t('dir', 'rtl')
        self.text_align = self.i18n.t('text_align', 'right')

        # logo_view = toga.ImageView(id="view", image="resources/zakat_tracker_logo.png")
        # logo_view.style.padding = 120
        # logo_view.style.flex = 1
        # self.main_box.add(logo_view)

        self.main_window = toga.MainWindow(
            title=self.i18n.t('formal_name'),
            size=(800, 600),
        )
        self.main_tabs_page()
        self.main_window.show()
    
    # pages

    def main_tabs_page(self):
        print('main_tabs_page')
        self.main_box = toga.OptionContainer(
            content=[
                (self.i18n.t('accounts'), self.accounts_page()),
                (self.i18n.t('zakat'), self.zakat_page(), toga.Icon("pasta")),
                (self.i18n.t('settings'), self.settings_page()),
            ],
            style=Pack(text_direction=self.dir),
        )
        self.main_window.content = self.main_box

    def zakat_page(self):
        print('zakat_page')
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        page_label = toga.Label(self.i18n.t('zakat'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        page.add(page_label)
        return page

    def settings_page(self):
        print('settings_page')
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # lang
        lang_box = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        lang_label = toga.Label(self.i18n.t('language'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        lang_selection = toga.Selection(
            items=[lang.value for lang in Lang],
            value=self.config.get('lang', Lang.AR_EN.value),
            on_change=lambda e: self.config.set('lang', e.value),
            style=Pack(text_direction=self.dir)
        )
        lang_note = toga.Label(self.i18n.t('lang_note'), style=Pack(flex=1, text_align='center', text_direction=self.dir))
        lang_box.add(lang_label)
        lang_box.add(lang_selection)
        lang_box.add(lang_note)

        page.add(lang_box)
        return page

    def accounts_page(self):
        print('accounts_page')
        accounts_box = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        add_button = toga.Button(
            self.i18n.t('add'),
            on_press=self.form,
            style=Pack(flex=1, text_direction=self.dir),
        )
        transfer_button = toga.Button(
            self.i18n.t('transfer'),
            on_press=self.transfer_form,
            style=Pack(flex=1, text_direction=self.dir),
        )
        self.accounts = toga.Table(
            headings=[
                self.i18n.t('account'),
                self.i18n.t('balance'),
                self.i18n.t('box'),
                self.i18n.t('log'),
            ],
            data=self.accounts_table_items(),
            on_select=self.account_table_on_select,
            on_activate=self.account_table_on_activate,
            missing_value="-",
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )

        accounts_box.add(toga.Box(
            children=[
                add_button, 
                transfer_button,
            ],
            style=Pack(direction=ROW, padding=5, text_direction=self.dir),
        ))
        accounts_box.add(self.accounts)
        return accounts_box

    def account_tabs_page(self, widget, account):
        tabs = toga.OptionContainer(
            content=[
                (self.i18n.t('boxes'), self.boxes_page(widget, account)),
                (self.i18n.t('logs'), self.logs_page(widget, account), toga.Icon("pasta")),
                (self.i18n.t('exchanges'), self.exchanges_page(widget, account)),
            ],
            style=Pack(flex=1, text_direction=self.dir),
        )
        back_button = toga.Button(self.i18n.t('back'), on_press=self.goto_main_page, style=Pack(flex=1, text_direction=self.dir))
        self.account_tabs = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        self.account_tabs.add(tabs)
        self.account_tabs.add(back_button)

        self.main_window.content = self.account_tabs

    def boxes_page(self, widget, account):
        print('boxes_page', account)
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # id, capital, count, last, rest, total
        self.boxes = toga.Table(
            headings=[
                self.i18n.t('date'),
                self.i18n.t('rest'),
                self.i18n.t('capital'),
                self.i18n.t('count'),
                self.i18n.t('last'),
                self.i18n.t('total'),
            ],
            data=self.boxes_table_items(account),
            missing_value="-",
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )

        page.add(self.account_tab_page_label_widget(account))
        page.add(self.boxes)
        return page

    def logs_page(self, widget, account):
        print('logs_page', account)
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # id, value, desc
        self.logs = toga.Table(
            headings=[
                self.i18n.t('date'),
                self.i18n.t('value'),
                self.i18n.t('desc'),
            ],
            data=self.logs_table_items(account),
            missing_value="-",
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )

        page.add(self.account_tab_page_label_widget(account))
        page.add(self.logs)
        return page

    def exchanges_page(self, widget, account):
        print('exchanges_page', account)
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        add_button = toga.Button(
            self.i18n.t('add'),
            on_press=lambda e: self.exchange_form(widget, account),
            style=Pack(flex=1, text_direction=self.dir),
        )

        # id, rate, description
        self.exchanges = toga.Table(
            headings=[
                self.i18n.t('date'),
                self.i18n.t('rate'),
                self.i18n.t('desc'),
            ],
            data=self.exchanges_table_items(account),
            missing_value="-",
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )

        page.add(self.account_tab_page_label_widget(account))
        page.add(add_button)
        page.add(self.exchanges)
        return page

    # generators

    def accounts_table_items(self):
        return [(k, v, self.db.box_size(k), self.db.log_size(k)) for k,v in self.db.accounts().items()]

    def boxes_table_items(self, account: str):
        return [(ZakatTracker.time_to_datetime(k), v['rest'], v['capital'], v['count'], v['last'], v['total']) for k,v in sorted(self.db.boxes(account).items(), reverse=True)]

    def logs_table_items(self, account: str):
        return [(ZakatTracker.time_to_datetime(k), v['value'], v['desc']) for k,v in sorted(self.db.logs(account).items(), reverse=True)]

    def exchanges_table_items(self, account: str):
        exchanges = self.db.exchanges()
        if not account in exchanges:
            exchange = self.db.exchange(account)
            return [(ZakatTracker.time_to_datetime(ZakatTracker.time()), exchange['rate'], exchange['description'])]
        return [(ZakatTracker.time_to_datetime(k), v['rate'], v['description']) for k,v in sorted(exchanges[account].items(), reverse=True)]

    def accounts_selection_items(self):
        return [""] + [ f'{k} ({v})' for k,v in sorted(self.db.accounts().items())]

    # helpers

    def transform_account_name(self, account: str) -> str:
        """
        Extracts account name and balance from strings like "Sudan account (1655.000000)", returning a tuple.

        Args:
            account (str): The account name string to transform.

        Returns:
            tuple or None: A tuple (account, balance) if successful, or None if not.
        """
        pattern = r'(\w+.*?)\s*\((\d+\.\d+)\)\s*'  # Updated pattern
        match = re.search(pattern, account)

        if match:
            name = match.group(1)
            balance = float(match.group(2))  # Convert to float
            return name, balance
        else:
            return None  # Return None if no match

    # handlers

    def account_table_on_select(self, widget):
        print('account_table_on_select', widget.selection)

    def account_table_on_activate(self, widget, row: toga.sources.list_source.Row):
        access_key = self.i18n.t('table_account_access_key')
        print('account_table_on_activate', f'access_key({access_key})')
        account = getattr(row, access_key)
        print('account_table_on_activate', account)
        self.account_tabs_page(widget, account)

    def account_select_on_change(self, widget):
        print('account_select_on_change', widget.value)
        if widget.value:
            self.account_input.value, _ = self.transform_account_name(widget.value)

    def from_account_select_on_change(self, widget):
        print('from_account_select_on_change', widget.value)
        if widget.value:
            self.from_account_input.value, _ = self.transform_account_name(widget.value)

    def to_account_select_on_change(self, widget):
        print('to_account_select_on_change', widget.value)
        if widget.value:
            self.to_account_input.value, _ = self.transform_account_name(widget.value)

    def from_account_input_on_change(self, widget):
        print('from_account_input_on_change', widget.value)
        self.from_account_select.value = ''

    def to_account_input_on_change(self, widget):
        print('to_account_input_on_change', widget.value)
        self.to_account_select.value = ''

    def account_input_on_change(self, widget):
        print('account_input_on_change', widget.value)
        self.account_select.value = ''

    # forms

    def exchange_form(self, widget, account):
        print('exchange_form', account)
        form = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # header

        form_label = toga.Label(self.i18n.t('exchange_form_label'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))

        # form order

        form.add(form_label)
        form.add(toga.Divider())
        form.add(self.readonly_account_widget(account))
        form.add(toga.Divider())
        form.add(self.rate_widget())
        form.add(toga.Divider())
        form.add(self.desc_widget())
        form.add(toga.Divider())
        form.add(self.datetime_widget())
        form.add(toga.Divider())

        def cancel(widget):
            self.main_window.content = self.account_tabs
        footer = toga.Box(style=Pack(direction=ROW, padding=5, text_direction=self.dir))
        cancel_button = toga.Button(self.i18n.t('cancel'), on_press=cancel, style=Pack(flex=1, text_direction=self.dir))
        save_button = toga.Button(self.i18n.t('save'), on_press=lambda e: self.exchange(widget, account), style=Pack(flex=1, text_direction=self.dir))

        footer.add(cancel_button)
        footer.add(save_button)

        form.add(footer)
        form.add(toga.Divider())

        self.main_window.content = toga.ScrollContainer(content=form, style=Pack(text_direction=self.dir))

    def transfer_form(self, widget):
        print('transfer_form')

        transfer_form = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # header

        form_label = toga.Label(self.i18n.t('financial_transfer_form'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))

        accounts = self.accounts_selection_items()

        # from_account
        from_account_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir))
        self.from_account_select = toga.Selection(
            items=accounts,
            on_change=self.from_account_select_on_change,
        )
        from_account_label = toga.Label(self.i18n.t('from_account'), style=Pack(padding=(0, 5), text_align='center', font_weight='bold', text_direction=self.dir))
        self.from_account_input = toga.TextInput(
            placeholder=self.i18n.t('form_account_input_placeholder'),
            on_change=self.from_account_input_on_change,
            style=Pack(flex=1, text_direction=self.dir),
        )
        from_account_box.add(from_account_label)
        from_account_box.add(self.from_account_select)
        from_account_box.add(self.from_account_input)

        # to_account
        to_account_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir))
        self.to_account_select = toga.Selection(
            items=accounts,
            on_change=self.to_account_select_on_change,
            style=Pack(text_direction=self.dir),
        )
        to_account_label = toga.Label(self.i18n.t('to_account'), style=Pack(padding=(0, 5), text_align='center', font_weight='bold', text_direction=self.dir))
        self.to_account_input = toga.TextInput(
            placeholder=self.i18n.t('to_account_input_placeholder'),
            on_change=self.to_account_input_on_change,
            style=Pack(flex=1, text_direction=self.dir),
        )
        to_account_box.add(to_account_label)
        to_account_box.add(self.to_account_select)
        to_account_box.add(self.to_account_input)

        # form
        transfer_form.add(form_label)
        transfer_form.add(toga.Divider())
        transfer_form.add(from_account_box)
        transfer_form.add(toga.Divider())
        transfer_form.add(to_account_box)
        transfer_form.add(toga.Divider())
        transfer_form.add(self.desc_widget())
        transfer_form.add(toga.Divider())
        transfer_form.add(self.amount_widget())
        transfer_form.add(toga.Divider())
        transfer_form.add(self.datetime_widget())
        transfer_form.add(toga.Divider())
        transfer_form.add(self.footer_widget(self.i18n.t('transfer'), on_press=self.transfer))
        transfer_form.add(toga.Divider())

        self.main_window.content = toga.ScrollContainer(content=transfer_form, style=Pack(text_direction=self.dir))

    def form(self, widget):
        print('form')

        form = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # header

        form_label = toga.Label(self.i18n.t('financial_transaction_form'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))

        account_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir))
        # selection
        self.account_select = toga.Selection(
            items=self.accounts_selection_items(),
            on_change=self.account_select_on_change,
        )

        # account
        account_label = toga.Label(self.i18n.t('account'), style=Pack(padding=(0, 5), text_direction=self.dir))
        self.account_input = toga.TextInput(
            placeholder=self.i18n.t('account_input_placeholder'),
            on_change=self.account_input_on_change,
            style=Pack(flex=1, text_direction=self.dir),
        )
        account_box.add(account_label)
        account_box.add(self.account_select)
        account_box.add(self.account_input)

        # switch
        self.is_discount_switch = toga.Switch(self.i18n.t('is_discount_switch_text'), style=Pack(flex=1, text_align='center', text_direction=self.dir))

        # form order

        form.add(form_label)
        form.add(toga.Divider())
        form.add(self.is_discount_switch)
        form.add(toga.Divider())
        form.add(account_box)
        form.add(toga.Divider())
        form.add(self.desc_widget())
        form.add(toga.Divider())
        form.add(self.amount_widget())
        form.add(toga.Divider())
        form.add(self.datetime_widget())
        form.add(toga.Divider())
        form.add(self.footer_widget(self.i18n.t('save'), on_press=self.save))
        form.add(toga.Divider())

        self.main_window.content = toga.ScrollContainer(content=form, style=Pack(text_direction=self.dir))

    # actions

    def goto_main_page(self, widget):
        print('cancel')
        self.main_window.content = self.main_box

    def update_accounts(self, widget):
        self.accounts.data = self.accounts_table_items()
    
    def update_exchanges(self, widget, account):
        self.exchanges.data = self.exchanges_table_items(account)

    def exchange(self, widget, account):
        print('exchange', account)
        rate = self.rate_input.value
        desc = self.desc_input.value
        year = int(self.year_input.value)
        month = int(self.month_input.value)
        day = int(self.day_input.value)
        hour = int(self.hour_input.value)
        minute = int(self.minute_input.value)
        second = int(self.second_input.value)
        datetime_value = datetime(year, month, day, hour, minute, second)
        print(f'rate: {rate}')
        print(f'desc: {desc}')
        print(f'datetime: {datetime_value}')
        if not rate or not desc or not year or not month or not day or not hour or not minute or not second:
            self.main_window.error_dialog(
                self.i18n.t('data_error'),
                self.i18n.t('all_fields_required_message'),
            )
            return
        try:
            self.db.exchange(account, created=ZakatTracker.time(datetime_value), rate=rate, description=desc, debug=True)
            self.update_exchanges(widget, account)
            self.main_window.content = self.account_tabs
            self.main_window.info_dialog(
                self.i18n.t('operation_accomplished_successfully'),
                self.i18n.t('message_status'),
            )
            print('6')
        except Exception as e:
            self.main_window.error_dialog(
                self.i18n.t('an_error_occurred'),
                str(e),
            )

    def save(self, widget):
        print('save')
        account = self.account_input.value
        desc = self.desc_input.value
        amount = self.amount_input.value
        year = int(self.year_input.value)
        month = int(self.month_input.value)
        day = int(self.day_input.value)
        hour = int(self.hour_input.value)
        minute = int(self.minute_input.value)
        second = int(self.second_input.value)
        datetime_value = datetime(year, month, day, hour, minute, second)
        discount = self.is_discount_switch.value
        print(f'discount: {discount}')
        print(f'account: {account}')
        print(f'desc: {desc}')
        print(f'amount: {amount}')
        print(f'datetime: {datetime_value}')
        if not account or not desc or not amount or not year or not month or not day or not hour or not minute or not second:
            self.main_window.error_dialog(
                self.i18n.t('data_error'),
                self.i18n.t('all_fields_required_message'),
            )
            return
        try:
            if discount:
                self.db.sub(amount, desc, account, created=ZakatTracker.time(datetime_value))
            else:
                self.db.track(amount, desc, account, created=ZakatTracker.time(datetime_value))
            self.update_accounts(widget)
            self.goto_main_page(widget)
            self.main_window.info_dialog(
                self.i18n.t('operation_accomplished_successfully'),
                self.i18n.t('message_status'),
            )
        except Exception as e:
            self.main_window.error_dialog(
                self.i18n.t('an_error_occurred'),
                str(e),
            )

    def transfer(self, widget):
        print('transfer')
        from_account = self.from_account_input.value
        to_account = self.to_account_input.value
        desc = self.desc_input.value
        amount = self.amount_input.value
        year = int(self.year_input.value)
        month = int(self.month_input.value)
        day = int(self.day_input.value)
        hour = int(self.hour_input.value)
        minute = int(self.minute_input.value)
        second = int(self.second_input.value)
        datetime_value = datetime(year, month, day, hour, minute, second)
        print(f'from_account: {from_account}')
        print(f'to_account: {to_account}')
        print(f'desc: {desc}')
        print(f'amount: {amount}')
        print(f'datetime: {datetime_value}')
        if not from_account or not to_account or not desc or not amount or not year or not month or not day or not hour or not minute or not second:
            self.main_window.error_dialog(
                self.i18n.t('data_error'),
                self.i18n.t('all_fields_required_message'),
            )
            return
        if from_account == to_account:
            self.main_window.error_dialog(
                self.i18n.t('data_error'),
                self.i18n.t('transfer_to_the_same_account_error_message'),
            )
            return

        try:
            self.db.transfer(amount, from_account, to_account, desc, created=ZakatTracker.time(datetime_value))
            self.db.free(self.db.lock()) # !!! need-revise: update zakat library, it should be auto freed.
            self.update_accounts(widget)
            self.goto_main_page(widget)
            self.main_window.info_dialog(
                self.i18n.t('operation_accomplished_successfully'),
                self.i18n.t('message_status'),
            )
        except Exception as e:
            self.main_window.error_dialog(
                self.i18n.t('an_error_occurred'),
                str(e),
            )

    # widgets

    def account_tab_page_label_widget(self, account):
        balance = self.db.balance(account)
        page_label = toga.Label(f'{account} - {balance}', style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        return page_label

    def desc_widget(self):
        desc_label = toga.Label(self.i18n.t('desc'), style=Pack(padding=(0, 5), text_direction=self.dir))
        self.desc_input = toga.MultilineTextInput(
            placeholder=self.i18n.t('desc_input_placeholder'),
            style=Pack(flex=1, text_direction=self.dir),
        )
        desc_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1, text_direction=self.dir))
        desc_box.add(desc_label)
        desc_box.add(self.desc_input)
        return desc_box

    def amount_widget(self):
        # amount
        amount_label = toga.Label(self.i18n.t('amount'), style=Pack(padding=(0, 5), text_direction=self.dir))
        self.amount_input = toga.NumberInput(min=0, step=0.000_001, style=Pack(flex=1, text_direction=self.dir))
        amount_box = toga.Box(style=Pack(direction=ROW, padding=5, text_direction=self.dir))
        amount_box.add(amount_label)
        amount_box.add(self.amount_input)
        return amount_box

    def rate_widget(self):
        # rate
        rate_label = toga.Label(self.i18n.t('rate'), style=Pack(padding=(0, 5), text_direction=self.dir))
        self.rate_input = toga.NumberInput(min=0.01, step=0.01, style=Pack(flex=1, text_direction=self.dir))
        rate_box = toga.Box(style=Pack(direction=ROW, padding=5, text_direction=self.dir))
        rate_box.add(rate_label)
        rate_box.add(self.rate_input)
        return rate_box
    
    def readonly_account_widget(self, account):
        # account
        account_label = toga.Label(self.i18n.t('account'), style=Pack(padding=(0, 5), text_direction=self.dir))
        account_input = toga.TextInput(value=account, readonly=True, style=Pack(flex=1, text_direction=self.dir))
        account_box = toga.Box(style=Pack(direction=ROW, padding=5, text_direction=self.dir))
        account_box.add(account_label)
        account_box.add(account_input)
        return account_box

    def datetime_widget(self):
        now = datetime.now()
        datetime_box = toga.Box(style=Pack(direction=COLUMN, padding=5, text_direction=self.dir))
        datetime_label = toga.Label(self.i18n.t('datetime_widget_label'), style=Pack(padding=(0, 5), text_align="center", font_weight='bold', text_direction=self.dir))

        year_label = toga.Label(self.i18n.t('year'), style=Pack(padding=(0, 5), text_direction=self.dir))
        self.year_input = toga.NumberInput(min=1000, value=now.year, style=Pack(flex=1, width=66, text_direction=self.dir))
        month_label = toga.Label(self.i18n.t('month'), style=Pack(padding=(0, 5)))
        self.month_input = toga.NumberInput(min=1, max=12, value=now.month, style=Pack(flex=1, width=45, text_direction=self.dir))
        day_label = toga.Label(self.i18n.t('day'), style=Pack(padding=(0, 5)))
        self.day_input = toga.NumberInput(min=1, max=31, value=now.day, style=Pack(flex=1, width=45, text_direction=self.dir))

        date_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1, text_direction=self.dir))
        date_box.add(year_label)
        date_box.add(self.year_input)
        date_box.add(month_label)
        date_box.add(self.month_input)
        date_box.add(day_label)
        date_box.add(self.day_input)

        hour_label = toga.Label(self.i18n.t('hour'), style=Pack(padding=(0, 5), text_direction=self.dir))
        self.hour_input = toga.NumberInput(min=0, max=23, value=now.hour, style=Pack(flex=1, width=45, text_direction=self.dir))
        minute_label = toga.Label(self.i18n.t('minute'), style=Pack(padding=(0, 5)))
        self.minute_input = toga.NumberInput(min=0, max=59, value=now.minute, style=Pack(flex=1, width=45, text_direction=self.dir))
        second_label = toga.Label(self.i18n.t('second'), style=Pack(padding=(0, 5)))
        self.second_input = toga.NumberInput(min=0, max=59, value=now.second, style=Pack(flex=1, width=45, text_direction=self.dir))
        
        time_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1, text_direction=self.dir))
        time_box.add(hour_label)
        time_box.add(self.hour_input)
        time_box.add(minute_label)
        time_box.add(self.minute_input)
        time_box.add(second_label)
        time_box.add(self.second_input)

        datetime_box.add(datetime_label)
        datetime_box.add(toga.Divider())
        datetime_box.add(date_box)
        datetime_box.add(time_box)
        return datetime_box

    def footer_widget(self, text: str, on_press: toga.widgets.button.OnPressHandler | None = None):
        footer = toga.Box(style=Pack(direction=ROW, padding=5, text_direction=self.dir))
        cancel_button = toga.Button(self.i18n.t('cancel'), on_press=self.goto_main_page, style=Pack(flex=1, text_direction=self.dir))
        save_button = toga.Button(text, on_press=on_press, style=Pack(flex=1, text_direction=self.dir))

        footer.add(cancel_button)
        footer.add(save_button)
        return footer

def main():
    return ZakatLedger()
