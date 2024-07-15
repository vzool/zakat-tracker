"""
Personal Accounting Software using Zakat way for all transactions from the beginning to the end
"""

import re
import os
import toga
import toga.sources
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from zakat import ZakatTracker, JSONEncoder
from datetime import datetime
from .i18n import i18n, Lang
from .config import Config
from .neknaj_jsonviewer import json_viewer
from .file_server import start_file_server
import pathlib
import json

def format_number(x) -> str:
    y = str(x).rstrip('0').rstrip('.')
    if not x:
        return '0'
    return format(float(y), ',').rstrip('0').rstrip('.')

class ZakatLedger(toga.App):
    def startup(self):

        self.icon = toga.Icon.APP_ICON
        self.os = toga.platform.current_platform.lower()
        self.datetime_supported = self.os in ['android', 'windows']
        print(f'platfom: {self.os} - datetime_supported: {self.datetime_supported}')
        print(f'Zakat Version: {ZakatTracker.Version()}')
        print(f'App Version: {self.version}')

        self.load_db()
        self.load_config()
        self.load_translations()

        # logo_view = toga.ImageView(id="view", image="resources/zakat_tracker_logo.png")
        # logo_view.style.padding = 120
        # logo_view.style.flex = 1
        # self.main_box.add(logo_view)

        self.main_window = toga.MainWindow(
            title=self.i18n.t('formal_name'),
            size=(800, 600),
        )
        self._original_title = self.main_window.title
        self.main_tabs_page()
        self.main_window.show()

    def title(self, text: str = None):
        if text:
            self.main_window.title = f'{self._original_title} - {text}'
        else:
            self.main_window.title = self._original_title

    # loaders

    def load_db(self):
        if not os.path.exists(self.paths.data):
            pathlib.Path.mkdir(self.paths.data)
        self.db_path = os.path.join(self.paths.data, 'zakat.pickle')
        print(f'db: {self.db_path}')
        self.db = ZakatTracker(self.db_path)

    def load_config(self):
        if not os.path.exists(self.paths.config):
            pathlib.Path.mkdir(self.paths.config)
        self.config_path = os.path.join(self.paths.config, 'config.json')
        print(f'config: {self.config_path}')
        self.config = Config(self.config_path)
        self.config_load_from_cache_when_possible = self.config.get('load_from_cache_when_possible', True)
        self.config_show_hidden_accounts = self.config.get('show_hidden_accounts', False)
        self.config_silver_gram_price_in_local_currency = self.config.get('silver_gram_price_in_local_currency', 2.17)
        self.config_silver_nisab_gram_quantity = self.config.get('silver_nisab_gram_quantity', 595)
        self.config_haul_time_cycle_in_days = self.config.get('haul_time_cycle_in_days', 355)

        self.nisab = self.config_silver_gram_price_in_local_currency * self.config_silver_nisab_gram_quantity

    def load_translations(self):
        if not os.path.exists(self.config_path):
            self.i18n = i18n(Lang.AR_EN)
            self.config.set('lang', Lang.AR_EN.value)
        else:
            self.i18n = i18n(Lang(self.config.get('lang')))

        self.dir = self.i18n.t('dir', 'rtl')
        self.text_align = self.i18n.t('text_align', 'right')

    # pages

    def main_tabs_page(self):
        print('main_tabs_page')
        self.main_box = toga.OptionContainer(
            content=[
                (self.i18n.t('accounts'), self.accounts_page(), toga.Icon("resources/icon/accounts.png")),
                (self.i18n.t('zakat'), self.zakat_page(), toga.Icon("resources/icon/zakat.png")),
                (self.i18n.t('history'), self.history_page(), toga.Icon("resources/icon/history.png")),
                (self.i18n.t('settings'), self.settings_page(), toga.Icon("resources/icon/settings.png")),
            ],
            style=Pack(text_direction=self.dir),
        )
        self.main_window.content = self.main_box

    def refresh(self, widget):
        print('refresh')
        self.update_accounts(widget)
        self.refresh_zakat_page()
        self.update_history(widget)

    def zakat_page(self):
        print('zakat_page')
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        self.zakat_on_boxes_note = self.label_note_widget(self.i18n.t('zakat_on_boxes_note'))
        self.table_show_row_details_note = self.label_note_widget(self.i18n.t('table_show_row_details_note'))
        self.zakat_note = toga.Label('', style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        #self.zakat_note_divider = toga.Divider()
        self.zakat_before_note_divider = toga.Divider()
        self.zakat_after_note_divider = toga.Divider()
        self.zakat_has_just_calculated = False

        # refresh_button
        def refresh_zakat_page(widget = None):
            self.update_accounts(widget)
            self.zakat_plan = self.db.check(
                silver_gram_price=self.config_silver_gram_price_in_local_currency,
                nisab=ZakatTracker.Nisab(
                    self.config_silver_gram_price_in_local_currency,
                    self.config_silver_nisab_gram_quantity,
                ),
                cycle=ZakatTracker.TimeCycle(self.config_haul_time_cycle_in_days),
                debug=True,
            )
            exists, stats, zakat = self.zakat_plan
            print(exists, stats, zakat)
            data = []
            total = 0
            for account, x in zakat.items():
                for _, y in x.items():
                    total += y['total']
                    data.append((
                        ZakatTracker.time_to_datetime(y['box_time']),
                        y['box_log'],
                        account,
                        format_number(y['box_capital']),
                        format_number(y['box_rest']),
                        format_number(y['total']),
                        format_number(y['count']),
                        format_number(y['exchange_rate']),
                        ZakatTracker.time_to_datetime(y['exchange_time']),
                        y['exchange_desc'],
                    ))

            self.zakat_table.data = data
            
            if exists:
                if hasattr(self, 'pay_button'):
                    self.pay_button.text = self.i18n.t('pay') + f' {total}'
                else:
                    page.clear()
                    self.pay_button = toga.Button(
                        self.i18n.t('pay') + f' {total}',
                        on_press=self.payment_parts_form,
                        style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir),
                    )
                    page.add(self.pay_button)
                    refresh_zakat_page()
                    create_table()
                    page.add(self.zakat_before_note_divider)
                    page.add(self.zakat_on_boxes_note)
                    page.add(self.table_show_row_details_note)
                    page.add(self.zakat_after_note_divider)
                    page.add(self.zakat_table)
                    self.zakat_table.data = data
                    page.add(self.refresh_button)
            else:
                zakat_str = format_number(round(total, 2))
                total_str = format_number(round(stats[1], 2))
                nisab_str = format_number(round(self.nisab, 2))
                self.zakat_note.text = self.i18n.t('below_nisab_note').format(zakat_str, total_str, nisab_str)
                if self.zakat_has_just_calculated:
                    print('--------- OK ---------')
                    return
                if hasattr(self, 'pay_button'):
                    print('--------- HIT ---------')
                    page.replace(self.pay_button, self.zakat_note)
                    self.zakat_has_just_calculated = True
                else:
                    page.add(self.zakat_note)
                    # page.add(self.zakat_note_divider)
                
        self.refresh_zakat_page = refresh_zakat_page
        self.refresh_button = toga.Button(self.i18n.t('refresh'), on_press=self.refresh, style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))

        def create_table():
            self.zakat_table = toga.Table(
                headings=[
                    self.i18n.t('date'),
                    self.i18n.t('desc'),
                    self.i18n.t('account'),
                    self.i18n.t('capital'),
                    self.i18n.t('rest'),
                    self.i18n.t('zakat'),
                    self.i18n.t('due'),
                    self.i18n.t('exchange_rate'),
                    self.i18n.t('exchange_time'),
                    self.i18n.t('exchange_desc'),
                ],
                missing_value="-",
                on_activate=lambda e, row: self.main_window.info_dialog(
                    self.i18n.t('row_details'),
                    self.row_details_str(self.zakat_table.headings, row),
                ),
                style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
            )

        create_table()
        refresh_zakat_page()

        page.add(self.zakat_before_note_divider)
        page.add(self.zakat_on_boxes_note)
        page.add(self.table_show_row_details_note)
        page.add(self.zakat_after_note_divider)
        page.add(self.zakat_table)

        page.add(self.refresh_button)
        return page

    def recover(self, widget):
        print('recover')
        def on_result(window, confirmed):
            if not confirmed:
                print('cancelled')
                return
            print('confirmed')
            try:
                if self.db.recall(dry=False, debug=True):
                    self.refresh(widget)
                    self.main_window.info_dialog(
                        self.i18n.t('message_status'),
                        self.i18n.t('recover_success'),
                    )
                    return
                self.main_window.error_dialog(
                    self.i18n.t('message_status'),
                    self.i18n.t('recover_failed'),
                )
            except Exception as e:
                print(f'Error in recover: {e}')
                self.main_window.error_dialog(
                    self.i18n.t('unexpected_error'),
                    str(e),
                )
        self.main_window.confirm_dialog(
            self.i18n.t('recover_confirm_title'),
            self.i18n.t('recover_confirm_message'),
            on_result=on_result,
        )

    def history_page(self):
        print('history_page')
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        restore_button = toga.Button(
            self.i18n.t('history_button'),
            on_press=self.recover,
            style=Pack(flex=1, text_direction=self.dir),
        )
        self.history_table = toga.Table(
            headings=[
                self.i18n.t('ref'),
                self.i18n.t('date'),
                self.i18n.t('logs'),
            ],
            missing_value="-",
            data=self.history_table_items(),
            on_select=self.history_table_on_select,
            on_activate=lambda e, row: self.main_window.info_dialog(
                self.i18n.t('row_details'),
                self.row_details_str(self.history_table.headings, row),
            ),
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )
        page.add(restore_button)
        page.add(toga.Divider())
        page.add(self.label_note_widget(self.i18n.t('history_note_1')))
        page.add(self.label_note_widget(self.i18n.t('history_note_2')))
        page.add(self.label_note_widget(self.i18n.t('history_note_3')))
        page.add(toga.Divider())
        page.add(self.history_table)
        page.add(toga.Button(self.i18n.t('refresh'), on_press=self.refresh, style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir)))
        return page

    async def file_server_page(self, widget):
        print('file_server_page')
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        web_view = toga.WebView(style=Pack(flex=1, text_direction=self.dir))
        
        def database_callback(file_path):
            ZakatTracker(db_path=file_path)

        def csv_callback(file_path, database_path, debug):
            x = ZakatTracker(db_path=database_path)
            return x.import_csv(file_path, debug=debug)

        file_name, download_url, upload_url, server_thread, shutdown_server = start_file_server(
            self.db_path,
            database_callback=database_callback,
            csv_callback=csv_callback,
            debug=True,
        )
        def back_button_action(widget):
            shutdown_server()
            self.goto_main_data_management_page(widget)
        back_button = toga.Button(self.i18n.t('back'), on_press=back_button_action, style=Pack(flex=1, text_direction=self.dir))
        await web_view.load_url(upload_url)
        def open_link_button_action(widget):
            try:
                print('open_link_button_action')
                from android.content import Intent
                from android.net import Uri
                intent = Intent(Intent.ACTION_VIEW)
                intent.setData(Uri.parse(upload_url))
                self._impl.start_activity(intent)
            except Exception as e:
                self.main_window.error_dialog(
                    self.i18n.t('unexpected_error'),
                    str(e),
                )
        open_link_button = toga.Button(self.i18n.t('open_in_web_browser'), on_press=open_link_button_action, style=Pack(flex=1, text_direction=self.dir))
        page.add(open_link_button)
        server_thread.start()
        page.add(web_view)
        page.add(back_button)
        self.main_window.content = page

    def show_data_page(self, widget):
        print('show_data_page')
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        web_view = toga.WebView(style=Pack(flex=1, text_direction=self.dir))
        back_button = toga.Button(self.i18n.t('back'), on_press=self.goto_main_data_management_page, style=Pack(flex=1, text_direction=self.dir))

        data = json.dumps(self.db.box(), indent=4 if self.show_raw_data_switch.value else None, cls=JSONEncoder)

        if self.show_raw_data_switch.value:
            web_view.set_content('http://localhost', f"<pre>{data}</pre>")
        else:
            web_view.set_content('http://localhost', json_viewer(data))

        page.add(web_view)
        page.add(back_button)
        self.main_window.content = page

    def data_management_page(self, widget):
        print('data_management_page')
        self.title(self.i18n.t('data_management'))
        self.main_data_management_page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        back_button = toga.Button(self.i18n.t('back'), on_press=self.goto_main_page, style=Pack(flex=1, text_direction=self.dir))
        show_data_button = toga.Button(self.i18n.t('show_data'), on_press=self.show_data_page, style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        file_server_button = toga.Button(self.i18n.t('file_server'), on_press=self.file_server_page, style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        self.show_raw_data_switch = toga.Switch(self.i18n.t('show_raw_data'))
        self.main_data_management_page.add(self.show_raw_data_switch)
        self.main_data_management_page.add(toga.Divider())
        self.main_data_management_page.add(show_data_button)
        self.main_data_management_page.add(toga.Divider())
        self.main_data_management_page.add(file_server_button)
        self.main_data_management_page.add(toga.Divider())
        self.main_data_management_page.add(back_button)
        self.main_window.content = self.main_data_management_page
        
    def settings_page(self):
        print('settings_page')
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # lang
        lang_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir))
        lang_label = toga.Label(self.i18n.t('language'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        lang_selection = toga.Selection(
            items=[lang.value for lang in Lang],
            value=self.config.get('lang', Lang.AR_EN.value),
            on_change=lambda e: self.config.set('lang', e.value),
            style=Pack(text_direction=self.dir)
        )
        lang_note = toga.Label(self.i18n.t('lang_note'), style=Pack(flex=1, text_align='center', text_direction=self.dir, padding=5))
        lang_box.add(lang_label)
        lang_box.add(lang_selection)
        lang_box.add(lang_note)

        # load from cache
        load_from_cache_when_possible_switch = toga.Switch(
            self.i18n.t('load_from_cache_when_possible'),
            value=self.config_load_from_cache_when_possible,
            on_change=lambda e: self.config.set('load_from_cache_when_possible', e.value),
            style=Pack(flex=1, text_direction=self.dir, text_align='center'),
        )

        # show hidden accounts
        def show_hidden_accounts(status):
                self.config_show_hidden_accounts = status
                self.config.set('show_hidden_accounts', status)
                self.refresh(self)
        show_hidden_accounts_switch = toga.Switch(
            self.i18n.t('show_hidden_accounts'),
            value=self.config_show_hidden_accounts,
            on_change=lambda e: show_hidden_accounts(e.value),
            style=Pack(flex=1, text_direction=self.dir, text_align='center'),
        )

        data_management_button = toga.Button(self.i18n.t('data_management'), on_press=self.data_management_page, style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))

        # silver_gram_price
        silver_gram_price_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir, padding=5))
        silver_gram_price_label = toga.Label(self.i18n.t('silver_gram_price_in_local_currency'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        def update_silver_gram_price(value: float):
            self.config_silver_gram_price_in_local_currency = value
            self.config.set('silver_gram_price_in_local_currency', value)
        silver_gram_price_input = toga.NumberInput(
            min=0.01,
            step=0.01,
            value=self.config_silver_gram_price_in_local_currency,
            on_change=lambda e: update_silver_gram_price(float(e.value)),
            style=Pack(flex=1, text_direction=self.dir, text_align='center'),
        )
        silver_gram_price_box.add(silver_gram_price_label)
        silver_gram_price_box.add(silver_gram_price_input)

        # silver_nisab_gram_quantity
        silver_nisab_gram_quantity_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir, padding=5))
        silver_nisab_gram_quantity_label = toga.Label(self.i18n.t('silver_nisab_gram_quantity'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        def update_silver_nisab_gram_quantity(value: float):
            self.config_silver_nisab_gram_quantity = value
            self.config.set('silver_nisab_gram_quantity', value)
        silver_nisab_gram_quantity_input = toga.NumberInput(
            min=0.01,
            step=0.01,
            value=self.config_silver_nisab_gram_quantity,
            on_change=lambda e: update_silver_nisab_gram_quantity(float(e.value)),
            style=Pack(flex=1, text_direction=self.dir, text_align='center'),
        )
        silver_nisab_gram_quantity_box.add(silver_nisab_gram_quantity_label)
        silver_nisab_gram_quantity_box.add(silver_nisab_gram_quantity_input)

        # haul_time_cycle
        haul_time_cycle_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir, padding=5))
        haul_time_cycle_label = toga.Label(self.i18n.t('haul_time_cycle_in_days'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        def update_haul_time_cycle(value: int):
            self.config_haul_time_cycle_in_days = value
            self.config.set('haul_time_cycle_in_days', value)
        haul_time_cycle_input = toga.NumberInput(
            min=1,
            value=self.config_haul_time_cycle_in_days,
            on_change=lambda e: update_haul_time_cycle(int(e.value)),
            style=Pack(flex=1, text_direction=self.dir, text_align='center'),
        )
        haul_time_cycle_box.add(haul_time_cycle_label)
        haul_time_cycle_box.add(haul_time_cycle_input)

        # zakat_version
        zakat_version_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir, padding=5))
        zakat_version_label = toga.Label(self.i18n.t('zakat_library_version'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        zakat_version_value = toga.Label(ZakatTracker.Version(), style=Pack(flex=1, text_align='center', text_direction=self.dir))
        zakat_version_box.add(zakat_version_label)
        zakat_version_box.add(zakat_version_value)
        
        # app_version
        app_version_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir, padding=5))
        app_version_label = toga.Label(self.i18n.t('app_version'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        app_version_value = toga.Label(self.version, style=Pack(flex=1, text_align='center', text_direction=self.dir))
        app_version_box.add(app_version_label)
        app_version_box.add(app_version_value)

        page.add(lang_box)
        page.add(toga.Divider())
        page.add(load_from_cache_when_possible_switch)
        page.add(toga.Divider())
        page.add(show_hidden_accounts_switch)
        page.add(toga.Divider())
        page.add(data_management_button)
        page.add(toga.Divider())
        page.add(silver_gram_price_box)
        page.add(toga.Divider())
        page.add(silver_nisab_gram_quantity_box)
        page.add(toga.Divider())
        page.add(haul_time_cycle_box)
        page.add(toga.Divider())
        page.add(zakat_version_box)
        page.add(toga.Divider())
        page.add(app_version_box)
        return page

    def accounts_page(self):
        print('accounts_page')
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
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
        self.accounts_table = toga.Table(
            headings=[
                self.i18n.t('account'),
                self.i18n.t('balance'),
                self.i18n.t('box'),
                self.i18n.t('log'),
                self.i18n.t('hide'),
                self.i18n.t('zakatable'),
            ],
            missing_value="-",
            data=self.accounts_table_items(),
            on_select=self.account_table_on_select,
            on_activate=lambda e, row: self.main_window.info_dialog(
                self.i18n.t('row_details'),
                self.row_details_str(self.accounts_table.headings, row),
            ),
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )

        page.add(toga.Box(
            children=[
                add_button, 
                transfer_button,
            ],
            style=Pack(direction=ROW, padding=5, text_direction=self.dir),
        ))
        page.add(toga.Divider())
        page.add(self.label_note_widget(self.i18n.t('accounts_table_note')))
        page.add(self.label_note_widget(self.i18n.t('table_show_row_details_note')))
        page.add(toga.Divider())
        page.add(self.accounts_table)
        page.add(toga.Button(self.i18n.t('refresh'), on_press=self.refresh, style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir)))
        return page

    def history_details_page(self, widget, ref):
        print('history_details_page', ref)
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        page_label = toga.Label(
            self.i18n.t('history_details_page_label').format(ref),
            style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir),
        )
        back_button = toga.Button(self.i18n.t('back'), on_press=self.goto_main_page, style=Pack(flex=1, text_direction=self.dir))
        self.history_details_table = toga.Table(
            headings=[
                self.i18n.t('action'),
                self.i18n.t('account'),
                self.i18n.t('ref'),
                self.i18n.t('file'),
                self.i18n.t('key'),
                self.i18n.t('value'),
                self.i18n.t('math'),
            ],
            missing_value="-",
            data=self.history_details_table_items(ref),
            on_activate=lambda e, row: self.main_window.info_dialog(
                self.i18n.t('row_details'),
                self.row_details_str(self.history_details_table.headings, row),
            ),
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )
        page.add(page_label)
        page.add(toga.Divider())
        page.add(self.label_note_widget(self.i18n.t('history_details_page_title').format(ZakatTracker.time_to_datetime(ref))))
        page.add(toga.Divider())
        page.add(self.history_details_table)
        page.add(back_button)
        self.main_window.content = page

    def account_tabs_page(self, widget, account):
        self.title(account)
        tabs = toga.OptionContainer(
            content=[
                (self.i18n.t('boxes'), self.boxes_page(widget, account), toga.Icon("resources/icon/boxes.png")),
                (self.i18n.t('logs'), self.logs_page(widget, account), toga.Icon("resources/icon/logs.png")),
                (self.i18n.t('exchanges'), self.exchanges_page(widget, account), toga.Icon("resources/icon/exchange_rates.png")),
            ],
            style=Pack(flex=1, text_direction=self.dir),
        )

        account_tabs = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # hide_account_switch
        def hide_account(status):
            self.db.hide(account, status)
            self.db.save()
        hide_account_switch = toga.Switch(
            self.i18n.t('hide_account'),
            value=self.db.hide(account),
            on_change=lambda e: hide_account(e.value),
            style=Pack(flex=1, text_direction=self.dir, text_align='center'),
        )
        account_tabs.add(hide_account_switch)

        # zakatable_switch
        def zakatable(status):
            self.db.zakatable(account, status)
            self.refresh(account)
            self.db.save()
        zakatable_switch = toga.Switch(
            self.i18n.t('zakatable'),
            value=self.db.zakatable(account),
            on_change=lambda e: zakatable(e.value),
            style=Pack(flex=1, text_direction=self.dir, text_align='center'),
        )
        account_tabs.add(zakatable_switch)

        back_button = toga.Button(self.i18n.t('back'), on_press=self.goto_main_page, style=Pack(flex=1, text_direction=self.dir))

        # footer

        footer = toga.Box(
            children=[
                back_button,
                hide_account_switch,
                zakatable_switch,
            ],
            style=Pack(direction=ROW, text_direction=self.dir),
        )
        
        account_tabs.add(tabs)
        account_tabs.add(footer)

        self.account_tabs = account_tabs
        self.main_window.content = self.account_tabs

    def boxes_page(self, widget, account):
        print('boxes_page', account)
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # id, capital, count, last, rest, total
        self.boxes_table = toga.Table(
            headings=[
                self.i18n.t('date'),
                self.i18n.t('rest'),
                self.i18n.t('capital'),
                self.i18n.t('count'),
                self.i18n.t('last'),
                self.i18n.t('total'),
            ],
            missing_value="-",
            data=self.boxes_table_items(account),
            on_activate=lambda e, row: self.main_window.info_dialog(
                self.i18n.t('row_details'),
                self.row_details_str(self.boxes_table.headings, row),
            ),
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )

        page.add(self.account_tab_page_label_widget(account))
        page.add(toga.Divider())
        page.add(self.label_note_widget(self.i18n.t('table_show_row_details_note')))
        page.add(toga.Divider())
        page.add(self.boxes_table)
        return page

    def logs_page(self, widget, account):
        print('logs_page', account)
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))

        # id, value, desc
        self.logs_table = toga.Table(
            headings=[
                self.i18n.t('date'),
                self.i18n.t('value'),
                self.i18n.t('desc'),
            ],
            missing_value="-",
            data=self.logs_table_items(account),
            on_activate=lambda e, row: self.main_window.info_dialog(
                self.i18n.t('row_details'),
                self.row_details_str(self.logs_table.headings, row),
            ),
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )

        page.add(self.account_tab_page_label_widget(account))
        page.add(toga.Divider())
        page.add(self.label_note_widget(self.i18n.t('table_show_row_details_note')))
        page.add(toga.Divider())
        page.add(self.logs_table)
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
        self.exchanges_table = toga.Table(
            headings=[
                self.i18n.t('date'),
                self.i18n.t('rate'),
                self.i18n.t('desc'),
            ],
            missing_value="-",
            data=self.exchanges_table_items(account),
            on_activate=lambda e, row: self.main_window.info_dialog(
                self.i18n.t('row_details'),
                self.row_details_str(self.exchanges_table.headings, row),
            ),
            style=Pack(flex=1, text_direction=self.dir, text_align=self.text_align),
        )

        page.add(self.account_tab_page_label_widget(account))
        page.add(add_button)
        page.add(toga.Divider())
        page.add(self.label_note_widget(self.i18n.t('exchanges_note')))
        page.add(self.label_note_widget(self.i18n.t('table_show_row_details_note')))
        page.add(toga.Divider())
        page.add(self.exchanges_table)
        return page

    # generators

    def history_details_table_items(self, ref: int):
        return [(
            v['action'],
            v['account'],
            v['ref'],
            v['file'],
            v['key'],
            v['value'],
            v['math'],
        ) for v in self.db.steps()[ref]]
    
    def history_table_items(self):
        return [(
            k,
            ZakatTracker.time_to_datetime(k),
            format_number(len(v)),
        ) for k, v in sorted(self.db.steps().items(), reverse=True)]

    def accounts_table_items(self):
        return [(
            k,
            format_number(v),
            self.db.box_size(k),
            self.db.log_size(k),
            self.i18n.t('yes') if self.db.hide(k) else self.i18n.t('no'),
            self.i18n.t('yes') if self.db.zakatable(k) else self.i18n.t('no'),
        ) for k,v in self.db.accounts().items() if not self.db.hide(k) or self.config_show_hidden_accounts]

    def boxes_table_items(self, account: str):
        return [(
            ZakatTracker.time_to_datetime(k),
            format_number(v['rest']),
            format_number(v['capital']),
            format_number(v['count']),
            ZakatTracker.time_to_datetime(v['last']) if v['last'] else '-',
            format_number(v['total']),
        ) for k,v in sorted(self.db.boxes(account).items(), reverse=True)]

    def logs_table_items(self, account: str):
        return [(
            ZakatTracker.time_to_datetime(k),
            format_number(v['value']),
            v['desc'],
        ) for k,v in sorted(self.db.logs(account).items(), reverse=True)]

    def exchanges_table_items(self, account: str):
        exchanges = self.db.exchanges()
        if not account in exchanges:
            exchange = self.db.exchange(account)
            return [(
                ZakatTracker.time_to_datetime(ZakatTracker.time()),
                format_number(exchange['rate']),
                exchange['description'],
            )]
        return [(
            ZakatTracker.time_to_datetime(k),
            format_number(v['rate']),
            v['description'],
        ) for k,v in sorted(exchanges[account].items(), reverse=True)]

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
            pattern = " (0)"
            if pattern in account:
                return account.split(pattern)[0], 0
            return None  # Return None if no match

    # handlers

    def history_table_on_select(self, widget):
        print('history_table_on_select', widget.selection)
        access_key = self.i18n.t('ref')
        print('history_table_on_select', f'access_key({access_key})')
        if not hasattr(widget.selection, access_key):
            return
        ref = getattr(widget.selection, access_key)
        print('history_table_on_select', ref)
        self.refresh(widget)
        self.history_details_page(widget, ref)

    def account_table_on_select(self, widget):
        print('account_table_on_select', widget.selection)
        access_key = self.i18n.t('table_account_access_key')
        print('account_table_on_activate', f'access_key({access_key})')
        if not hasattr(widget.selection, access_key):
            return
        account = getattr(widget.selection, access_key)
        print('account_table_on_activate', account)
        self.refresh(widget)
        self.account_tabs_page(widget, account)

    def account_table_on_activate(self, widget, row: toga.sources.list_source.Row):
        pass

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

    def payment_parts_form(self, widget):
        print('payment_parts_form')
        print(self.zakat_plan)
        brief = self.zakat_plan[1]
        print('brief', brief)
        _, _, self.demand = brief
        print('demand', self.demand)
        self.demand = round(self.demand, 2)
        print('demand', self.demand)
        self.payment_parts_widgets = {}
        page = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir))
        form_label = toga.Label(self.i18n.t('payment_parts_form_label'), style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
        self.apply_payment_parts_button = toga.Button(self.i18n.t('apply_payment_parts'), on_press=self.pay, enabled=False, style=Pack(flex=1, text_direction=self.dir))
        self.demand_meter = toga.Label(f'0 / {self.demand}', style=Pack(flex=1, text_align='center', font_weight='bold', font_size=24, text_direction=self.dir))

        def auto_pay_switch(widget):
            for account, widgets in self.payment_parts_widgets.items():
                print('---------- account ----------', account)
                switch, progress_bar, number_input, _ = widgets
                switch.enabled = not widget.value
                switch.value = False
                progress_bar.value = 0
                number_input.value = 0
                if widget.value:
                    if account not in self.zakat_plan[2]:
                        continue
                    for part in self.zakat_plan[2][account].values():
                        print('part', part)
                        progress_bar.value = float(progress_bar.value) + part['total']
                        number_input.value = float(number_input.value) + part['total']
            self.apply_payment_parts_button.enabled = widget.value
            if widget.value:
                self.supply = self.demand
                self.demand_meter.text = f'{self.supply} / {self.demand}'
            else:
                self.demand_meter.text = f'0 / {self.demand}'

        self.auto_pay_switch = toga.Switch(
            self.i18n.t('auto_pay_switch'),
            on_change=auto_pay_switch,
            style=Pack(flex=1, text_direction=self.dir, text_align='center'),
        )
        page.add(form_label)
        page.add(self.demand_meter)
        page.add(self.apply_payment_parts_button)
        page.add(self.auto_pay_switch)

        self.payment_parts = self.db.build_payment_parts(self.demand)
        print('payment_parts', self.payment_parts)

        # build form
        parts_box = toga.Box(style=Pack(direction=COLUMN, flex=1, text_direction=self.dir, padding=12))
        
        parts_box.add(toga.Divider())
        for account, part in self.payment_parts['account'].items():
            print(account, part)
            parts_box.add(self.payment_part_row_widget(widget, account, part['balance'], part['rate']))
            parts_box.add(toga.Divider())
        page.add(toga.ScrollContainer(content=parts_box, style=Pack(flex=1, text_direction=self.dir)))
        back_button = toga.Button(self.i18n.t('back'), on_press=self.goto_main_page, style=Pack(flex=1, text_direction=self.dir))
        page.add(back_button)
        self.main_window.content = page


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
        transfer_form.add(self.label_note_widget(self.i18n.t('transfer_amount_note')))
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

        # account_selection
        account_box = toga.Box(style=Pack(direction=COLUMN, text_direction=self.dir))
        self.account_select = toga.Selection(
            items=self.accounts_selection_items(),
            on_change=self.account_select_on_change,
        )

        # account_input
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
        def toggle_form(widget):
            self.is_discount_switch.enabled = not widget.value
            self.account_select.enabled = not widget.value
            self.desc_input.enabled = not widget.value
            self.amount_input.enabled = not widget.value
            self.year_input.enabled = not widget.value
            self.month_input.enabled = not widget.value
            self.day_input.enabled = not widget.value
            self.hour_input.enabled = not widget.value
            self.minute_input.enabled = not widget.value
            self.second_input.enabled = not widget.value
            self.account_input.focus()
        self.is_new_account_switch = toga.Switch(
            self.i18n.t('is_new_account_switch_text'),
            style=Pack(flex=1, text_align='center', text_direction=self.dir),
            on_change=toggle_form,
        )
        self.is_discount_switch = toga.Switch(self.i18n.t('is_discount_switch_text'), style=Pack(flex=1, text_align='center', text_direction=self.dir))
        switch_box = toga.Box(
            children=[
                self.is_new_account_switch,
                self.is_discount_switch,
            ],
            style=Pack(direction=ROW, text_direction=self.dir),
        )

        # form order
        form.add(form_label)
        form.add(toga.Divider())
        form.add(switch_box)
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

    def goto_main_data_management_page(self, widget):
        self.main_window.content = self.main_data_management_page

    def goto_main_page(self, widget):
        print('cancel')
        self.title()
        self.main_window.content = self.main_box

    def update_history(self, widget):
        self.history_table.data = self.history_table_items()

    def update_accounts(self, widget):
        self.accounts_table.data = self.accounts_table_items()
    
    def update_exchanges(self, widget, account):
        self.exchanges_table.data = self.exchanges_table_items(account)

    def pay(self, widget):
        print('pay')
        def on_result(window, confirmed):
            try:
                if not confirmed:
                    print('cancelled')
                    return
                print('confirmed')
                ok = False
                if self.auto_pay_switch.value:
                    print('apply(auto)')
                    ok = self.db.zakat(self.zakat_plan, debug=True)
                else:
                    print('apply(parts)')
                    for account, widgets in self.payment_parts_widgets.items():
                        _, _, number_input, _ = widgets
                        self.payment_parts['account'][account]['part'] = number_input.value
                    print(self.payment_parts)
                    valid_payment_parts =  self.db.check_payment_parts(self.payment_parts, debug=True)
                    print('valid_payment_parts', valid_payment_parts)
                    if valid_payment_parts != 0:
                        self.main_window.error_dialog(
                            self.i18n.t('data_error'),
                            self.i18n.t('invalid_payment_parts'),
                        )
                        return
                    ok = self.db.zakat(self.zakat_plan, parts=self.payment_parts, debug=True)

                if not ok:
                    self.main_window.error_dialog(
                        self.i18n.t('message_status'),
                        self.i18n.t('operation_failed'),
                    )
                    return
                    
                self.db.save()
                self.refresh(widget)
                self.main_window.content = self.main_box
                self.main_window.info_dialog(
                    self.i18n.t('message_status'),
                    self.i18n.t('operation_accomplished_successfully'),
                )   
            except Exception as e:
                self.main_window.error_dialog(
                    self.i18n.t('unexpected_error'),
                    str(e),
                )
        self.main_window.confirm_dialog(
            self.i18n.t('recover_confirm_title'),
            self.i18n.t('recover_confirm_message'),
            on_result=on_result,
        )

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
        if not rate or not desc or not year or not month or not day:
            self.main_window.error_dialog(
                self.i18n.t('data_error'),
                self.i18n.t('all_fields_required_message'),
            )
            return
        try:
            self.db.exchange(account, created=ZakatTracker.time(datetime_value), rate=rate, description=desc, debug=True)
            self.update_exchanges(widget, account)
            self.db.save()
            self.main_window.content = self.account_tabs
            self.main_window.info_dialog(
                self.i18n.t('message_status'),
                self.i18n.t('operation_accomplished_successfully'),
            )
        except Exception as e:
            self.main_window.error_dialog(
                self.i18n.t('unexpected_error'),
                str(e),
            )

    def save(self, widget):
        print('save')
        new_account = self.is_new_account_switch.value
        discount = self.is_discount_switch.value
        account = self.account_input.value
        desc = self.desc_input.value
        amount = self.amount_input.value
        datetime_value, datetime_missing = self.datetime_value()
        print(f'new_account: {new_account}')
        print(f'discount: {discount}')
        print(f'account: {account}')
        print(f'desc: {desc}')
        print(f'amount: {amount}')
        print(f'datetime_missing: {datetime_missing}')
        print(f'datetime_value: {datetime_value}')
        if new_account:
            amount = 0
        elif not account or not desc or not amount or datetime_missing:
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
            self.db.save()
            self.refresh(widget)
            self.goto_main_page(widget)
            self.main_window.info_dialog(
                self.i18n.t('message_status'),
                self.i18n.t('operation_accomplished_successfully'),
            )
        except Exception as e:
            self.main_window.error_dialog(
                self.i18n.t('unexpected_error'),
                str(e),
            )

    def transfer(self, widget):
        print('transfer')
        from_account = self.from_account_input.value
        to_account = self.to_account_input.value
        desc = self.desc_input.value
        amount = self.amount_input.value
        datetime_value, datetime_missing = self.datetime_value()
        print(f'from_account: {from_account}')
        print(f'to_account: {to_account}')
        print(f'desc: {desc}')
        print(f'amount: {amount}')
        print(f'datetime_missing: {datetime_missing}')
        print(f'datetime_value: {datetime_value}')
        if not from_account or not to_account or not desc or not amount or datetime_missing:
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
            self.refresh(widget)
            self.goto_main_page(widget)
            self.main_window.info_dialog(
                self.i18n.t('message_status'),
                self.i18n.t('operation_accomplished_successfully'),
            )
        except Exception as e:
            self.main_window.error_dialog(
                self.i18n.t('unexpected_error'),
                str(e),
            )

    # values

    def datetime_value(self) -> tuple:
        missing = False
        if self.datetime_supported:
            date = self.date_input.value
            time = self.time_input.value
            year = date.year
            month = date.month
            day = date.day
            hour = time.hour
            minute = time.minute
            second = time.second
        else:
            year = int(self.year_input.value)
            month = int(self.month_input.value)
            day = int(self.day_input.value)
            hour = int(self.hour_input.value)
            minute = int(self.minute_input.value)
            second = int(self.second_input.value)
            missing = not year or not month or not day
        return datetime(year, month, day, hour, minute, second), missing

    # widgets

    def payment_part_row_widget(self, widget, account, balance, rate):
        row = toga.Box(style=Pack(direction=ROW, padding=15, text_direction=self.dir))
        formatted_balance = format_number(balance)
        def number_input_updated(widget):
            self.supply = 0
            for (switch, progress_bar, number_input, rate) in self.payment_parts_widgets.values():
                if not number_input.value:
                    continue
                progress_bar.value = number_input.value
                self.supply += ZakatTracker.exchange_calc(
                    x=float(number_input.value) * int(switch.value),
                    x_rate=float(rate),
                    y_rate=1,
                )
            self.demand_meter.text = f'{self.supply} / {self.demand}'
            self.apply_payment_parts_button.enabled = self.supply == self.demand
        number_input = toga.NumberInput(value=0, min=0, max=balance, step=0.01, on_change=number_input_updated, readonly=True, style=Pack(text_direction=self.dir))
        progress_bar = toga.ProgressBar(value=0, max=balance, style=Pack(flex=1, text_direction=self.dir))
        def update_progress_bar(widget):
            number_input.readonly = not widget.value
            number_input.value = 0
            if not widget.value:
                progress_bar.value = 0
        switch = toga.Switch(f'{account}({formatted_balance})', on_change=update_progress_bar, style=Pack(text_direction=self.dir))
        self.payment_parts_widgets[account] = (switch, progress_bar, number_input, rate)
        row.add(switch)
        row.add(progress_bar)
        row.add(number_input)
        return row

    def label_note_widget(self, note: str):
        return toga.Label(f'* {note} *', style=Pack(flex=1, text_align=self.text_align, text_direction=self.dir, font_size=9))

    def account_tab_page_label_widget(self, account):
        balance = self.db.balance(account, cached=self.config_load_from_cache_when_possible)
        account_label = self.i18n.t('account')
        unit = self.i18n.t('unit')
        page_label = toga.Label(f'{account_label}: {account} = {format_number(balance)} {unit}', style=Pack(flex=1, text_align='center', font_weight='bold', font_size=10, text_direction=self.dir))
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
        rate_label = toga.Label(self.i18n.t('rate'), style=Pack(padding=(0, 5), text_direction=self.dir))
        self.rate_input = toga.NumberInput(min=0.01, step=0.01, style=Pack(flex=1, text_direction=self.dir))
        rate_box = toga.Box(style=Pack(direction=ROW, padding=5, text_direction=self.dir))
        rate_box.add(rate_label)
        rate_box.add(self.rate_input)
        return rate_box
    
    def readonly_account_widget(self, account):
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

        if self.datetime_supported:
            self.date_input = toga.DateInput()
            self.time_input = toga.TimeInput()
            datetime_box.add(datetime_label)
            datetime_box.add(toga.Divider())
            datetime_box.add(self.date_input)
            datetime_box.add(self.time_input)
            return datetime_box
        
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

    # transformers

    def row_details_str(self, headings, row: toga.sources.list_source.Row):
        result = ''
        i = 0
        for x in headings:
            i += 1
            try:
                key = x.replace(' ', '_').lower().rstrip('?').rstrip('؟')
                value = getattr(row, key)
                value_str = str(value)
                if type(value) is bool:
                    value_str = self.i18n.t('yes') if value else self.i18n.t('no')
                result += f'{i}- {x} = {value_str}\n'
            except:
                print(f'Error(row_details_str): key({key}) not found in row')
        return result

def main():
    return ZakatLedger()
