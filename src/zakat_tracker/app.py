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

class ZakatLedger(toga.App):
    def startup(self):

        self.icon = toga.Icon.APP_ICON

        if not os.path.exists(self.paths.data):
            os.makedirs(self.paths.data)
        path = f'{self.paths.data}/zakat.pickle'
        print(f'db: {path}')
        self.db = ZakatTracker(path)

        # logo_view = toga.ImageView(id="view", image="resources/zakat_tracker_logo.png")
        # logo_view.style.padding = 120
        # logo_view.style.flex = 1
        # self.main_box.add(logo_view)

        self.main_window = toga.MainWindow(
            title=f'متتبع الزكاة ({self.formal_name})',
            size=(800, 600),
        )
        self.accounts_page()
        self.main_window.show()
    
    # pages

    def accounts_page(self):
        print('accounts_page')
        accounts_box = toga.Box(style=Pack(direction=COLUMN, flex=1))
        add_button = toga.Button(
            "إضافة (Add)",
            on_press=self.form,
            style=Pack(flex=1),
        )
        transfer_button = toga.Button(
            "تحويل (Transfer)",
            on_press=self.transfer_form,
            style=Pack(flex=1),
        )
        self.accounts = toga.Table(
            headings=["الحساب (Account)", "الرصيد (Balance)", "صندوق (Box)", "حركة (Log)"],
            data=self.accounts_table_items(),
            on_select=self.account_table_on_select,
            on_activate=self.account_table_on_activate,
            missing_value="-",
            style=Pack(flex=1),
        )

        accounts_box.add(toga.Box(
            children=[
                add_button, 
                transfer_button,
            ],
            style=Pack(direction=ROW, padding=5),
        ))
        accounts_box.add(self.accounts)
        self.main_box = toga.OptionContainer(
            content=[
                ("الحسابات (Accounts)", accounts_box),
                ("الزكاة (Zakat)", toga.Box(), toga.Icon("pasta")),
                ("التاريخ (History)", toga.Box()),
            ],
        )
        self.main_window.content = self.main_box

    def boxes_page(self, widget, account):
        print('boxes_page', account)
        page = toga.Box(style=Pack(direction=COLUMN, flex=1))

        page_label = toga.Label(f'صناديق [{account}] Boxes of ', style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10))

        # id, capital, count, last, rest, total 
        self.boxes = toga.Table(
            headings=["X", "المتبقي (Rest)", "راس المال (Capital)", "العدد (Count)", "آخر زكاة (Last)", "الإجمالي (Total)"],
            data=self.boxes_table_items(account),
            missing_value="-",
            style=Pack(flex=1),
        )

        back_button = toga.Button("رجوع (Back)", on_press=self.cancel, style=Pack(flex=1))

        page.add(page_label)
        page.add(self.boxes)
        page.add(back_button)

        self.main_window.content = toga.ScrollContainer(content=page)

    # generators

    def accounts_table_items(self):
        return [(k, v, self.db.box_size(k), self.db.log_size(k)) for k,v in self.db.accounts().items()]

    def boxes_table_items(self, account: str):
        return [(k, v['rest'], v['capital'], v['count'], v['last'], v['total']) for k,v in sorted(self.db.boxes(account).items(), reverse=True)]

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
        print('account_table_on_activate', row.الحساب_account)
        self.boxes_page(widget, row.الحساب_account)

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

    def transfer_form(self, widget):
        print('transfer_form')

        transfer_form = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # header

        form_label = toga.Label("نموذج التحويل المالي (Financial Transfer Form)", style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10))

        accounts = self.accounts_selection_items()

        # from_account
        from_account_box = toga.Box(style=Pack(direction=COLUMN))
        self.from_account_select = toga.Selection(
            items=accounts,
            on_change=self.from_account_select_on_change,
        )
        from_account_label = toga.Label("من الحساب (From Account)", style=Pack(padding=(0, 5), text_align='center', font_weight='bold'))
        self.from_account_input = toga.TextInput(
            placeholder="أدخل اسم الحساب المحول منه...Enter the name of the account you are transferring from",
            on_change=self.from_account_input_on_change,
            style=Pack(flex=1),
        )
        from_account_box.add(from_account_label)
        from_account_box.add(self.from_account_select)
        from_account_box.add(self.from_account_input)

        # to_account
        to_account_box = toga.Box(style=Pack(direction=COLUMN))
        self.to_account_select = toga.Selection(
            items=accounts,
            on_change=self.to_account_select_on_change,
        )
        to_account_label = toga.Label("إلى الحساب (To Account)", style=Pack(padding=(0, 5), text_align='center', font_weight='bold'))
        self.to_account_input = toga.TextInput(
            placeholder="أدخل اسم الحساب المحول إليه...Enter the name of the account you are transferring to",
            on_change=self.to_account_input_on_change,
            style=Pack(flex=1),
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
        transfer_form.add(self.footer_widget("تحويل (Transfer)", on_press=self.transfer))
        transfer_form.add(toga.Divider())

        self.main_window.content = toga.ScrollContainer(content=transfer_form)

    def form(self, widget):
        print('form')

        form = toga.Box(style=Pack(direction=COLUMN, flex=1))

        # header

        form_label = toga.Label("نموذج عملية مالية (Financial Transaction Form)", style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10))

        account_box = toga.Box(style=Pack(direction=COLUMN))
        # selection
        self.account_select = toga.Selection(
            items=self.accounts_selection_items(),
            on_change=self.account_select_on_change,
        )

        # account
        account_label = toga.Label("الحساب (Account)", style=Pack(padding=(0, 5)))
        self.account_input = toga.TextInput(
            placeholder="أدخل اسم الحساب...Enter the account name",
            on_change=self.account_input_on_change,
            style=Pack(flex=1),
        )
        account_box.add(account_label)
        account_box.add(self.account_select)
        account_box.add(self.account_input)

        # switch
        self.switch_input = toga.Switch("هل عملية خصم؟ - Is this a discount process?", style=Pack(flex=1, text_align='center'))

        # form order

        form.add(form_label)
        form.add(toga.Divider())
        form.add(self.switch_input)
        form.add(toga.Divider())
        form.add(account_box)
        form.add(toga.Divider())
        form.add(self.desc_widget())
        form.add(toga.Divider())
        form.add(self.amount_widget())
        form.add(toga.Divider())
        form.add(self.datetime_widget())
        form.add(toga.Divider())
        form.add(self.footer_widget("حفظ (Save)", on_press=self.save))
        form.add(toga.Divider())

        self.main_window.content = toga.ScrollContainer(content=form)

    # actions

    def cancel(self, widget):
        print('cancel')
        self.main_window.content = self.main_box

    def update(self, widget):
        self.accounts.data = self.accounts_table_items()

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
        discount = self.switch_input.value
        print(f'discount: {discount}')
        print(f'account: {account}')
        print(f'desc: {desc}')
        print(f'amount: {amount}')
        print(f'datetime: {datetime_value}')
        if not account or not desc or not amount or not year or not month or not day or not hour or not minute or not second:
            self.main_window.error_dialog(
                "خطأ في البيانات (Data error)",
                "يرجى ملئ كل الحقول المطلوبة (Please fill out all required fields)",
            )
            return
        try:
            if discount:
                self.db.sub(amount, desc, account, created=ZakatTracker.time(datetime_value))
            else:
                self.db.track(amount, desc, account, created=ZakatTracker.time(datetime_value))
            self.update(widget)
            self.cancel(widget)
            self.main_window.info_dialog(
                "تمت العملية بنجاح (Operation Accomplished Successfully)",
                "حالة الرسالة (Message Status)",
            )
        except Exception as e:
            self.main_window.error_dialog(
                "حدث خطأ (An Error Occurred)",
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
                "خطأ في البيانات (Data error)",
                "يرجى ملئ كل الحقول المطلوبة (Please fill out all required fields)",
            )
            return
        if from_account == to_account:
            self.main_window.error_dialog(
                "خطأ في البيانات (Data error)",
                "لا يمكن تحويل من وإلى الحساب نفسه (It is not possible to transfer to and from the same account)",
            )
            return

        try:
            self.db.transfer(amount, from_account, to_account, desc, created=ZakatTracker.time(datetime_value))
            self.db.free(self.db.lock()) # !!! need-revise: update zakat library, it should be auto freed.
            self.update(widget)
            self.cancel(widget)
            self.main_window.info_dialog(
                "تمت العملية بنجاح (Operation Accomplished Successfully)",
                "حالة الرسالة (Message Status)",
            )
        except Exception as e:
            self.main_window.error_dialog(
                "حدث خطأ (An Error Occurred)",
                str(e),
            )

    # widgets

    def desc_widget(self):
        desc_label = toga.Label("الوصف (Desc)", style=Pack(padding=(0, 5)))
        self.desc_input = toga.MultilineTextInput(
            placeholder="أكتب وصف للعملية المحاسبية...Write a description of the accounting process",
            style=Pack(flex=1),
        )
        desc_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1))
        desc_box.add(desc_label)
        desc_box.add(self.desc_input)
        return desc_box

    def amount_widget(self):
        # amount
        amount_label = toga.Label("المبلغ (Amount)", style=Pack(padding=(0, 5)))
        self.amount_input = toga.NumberInput(min=0, step=0.000_001, style=Pack(flex=1))
        amount_box = toga.Box(style=Pack(direction=ROW, padding=5))
        amount_box.add(amount_label)
        amount_box.add(self.amount_input)
        return amount_box

    def datetime_widget(self):
        now = datetime.now()
        datetime_box = toga.Box(style=Pack(direction=COLUMN, padding=5))
        datetime_label = toga.Label("تاريخ وتوقيت العملية (Date and timing of the operation)", style=Pack(padding=(0, 5), text_align="center", font_weight='bold'))

        year_label = toga.Label("سنة/Year", style=Pack(padding=(0, 5)))
        self.year_input = toga.NumberInput(min=1000, value=now.year, style=Pack(flex=1, width=66))
        month_label = toga.Label("شهر/Month", style=Pack(padding=(0, 5)))
        self.month_input = toga.NumberInput(min=1, max=12, value=now.month, style=Pack(flex=1, width=45))
        day_label = toga.Label("يوم/Day", style=Pack(padding=(0, 5)))
        self.day_input = toga.NumberInput(min=1, max=31, value=now.day, style=Pack(flex=1, width=45))

        date_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1))
        date_box.add(year_label)
        date_box.add(self.year_input)
        date_box.add(month_label)
        date_box.add(self.month_input)
        date_box.add(day_label)
        date_box.add(self.day_input)

        hour_label = toga.Label("ساعة/Hour", style=Pack(padding=(0, 5)))
        self.hour_input = toga.NumberInput(min=0, max=23, value=now.hour, style=Pack(flex=1, width=45))
        minute_label = toga.Label("دقيقة/Min.", style=Pack(padding=(0, 5)))
        self.minute_input = toga.NumberInput(min=0, max=59, value=now.minute, style=Pack(flex=1, width=45))
        second_label = toga.Label("ثانية/Sec.", style=Pack(padding=(0, 5)))
        self.second_input = toga.NumberInput(min=0, max=59, value=now.second, style=Pack(flex=1, width=45))
        
        time_box = toga.Box(style=Pack(direction=ROW, padding=5, flex=1))
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
        footer = toga.Box(style=Pack(direction=ROW, padding=5))
        cancel_button = toga.Button("إلغاء (Cancel)", on_press=self.cancel, style=Pack(flex=1))
        save_button = toga.Button(text, on_press=on_press, style=Pack(flex=1))

        footer.add(cancel_button)
        footer.add(save_button)
        return footer

def main():
    return ZakatLedger()
