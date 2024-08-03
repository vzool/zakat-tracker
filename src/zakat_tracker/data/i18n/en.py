translations = {
    # app
    'dir': 'ltr',
    'text_align': 'left',
    'text_end': 'right',
    'formal_name': 'Zakat Tracker',

    # time
    'spoken_time_separator': ',',
    'millennia': 'Millennia',
    'century': 'Century',
    'years': 'Years',
    'days': 'Days',
    'hours': 'Hours',
    'minutes': 'Minutes',
    'seconds': 'Seconds',
    'milliSeconds': 'MilliSeconds',
    'microSeconds': 'MicroSeconds',
    'nanoSeconds': 'NanoSeconds',

    # startup
    'on_exit_title': 'Exit Confirmation',
    'on_exit_message': 'Are you sure you want to exit the application?',

    # main_tabs_page
    'accounts': 'Accounts',
    'transactions': 'ُTransactions',
    'zakat': 'Zakat',
    'history': 'History',
    'settings': 'Settings',

    # history_details_page
    'history_details_page_label': 'Show Step {} Transactions',
    'history_details_page_title': 'Step on {}',
    'action': 'Action',
    'file': 'File',
    'key': 'Key',
    'value': 'Value',
    'math': 'Math Operation',

    # snapshot_table_on_select
    'snapshot_load_success': 'Database snapshot uploaded successfully',
    'snapshot_load_failed': 'Database snapshot upload failed',
    'snapshot_load_confirm_title': 'Database snapshot load',
    'snapshot_load_confirm_message': 'Would you like to upload a snapshot of a database file at {}?',

    # snapshot
    'snapshot_success': 'Snapshot created from database file successfully',
    'snapshot_failed': 'Snapshot created from database file failed',
    'snapshot_confirm_title': 'Database Snapshot Confirmation',
    'snapshot_confirm_message': 'Do you want to create a snapshot of the database file?',

    # snapshot_page
    'snapshot_button': 'Backup',
    'snapshot_note': 'Snapshots are not duplicated if they exist or the database never changed',
    'hash': 'Hash',
    'path': 'Path',
    'exists': 'Exists',

    # recover
    'recover_confirm_title': 'Be careful, No Rush',
    'recover_confirm_message': 'Do you want to perform this operation?',

    # history_page
    'history_button': 'One Step Recovery',
    'history_note_1': 'Data is stored chronologically like a blockchain',
    'history_note_2': 'Each step includes many operations. Click to view Details',
    'history_note_3': 'The is non-cancellable, check carefully before do the recovery',
    'ref': 'Reference',
    'recover_success': 'The recovery operation was successful',
    'recover_failed': 'The restore operation failed',

    # pay
    'invalid_payment_parts': 'Distribution of Deductions is Invalid',
    'operation_failed': 'Operation Failed',

    # payment_parts_form
    'payment_parts_form_label': 'Form for Deducting Zakat from Specific Accounts',
    'apply_payment_parts': 'Apply Zakat Deductions',
    'auto_pay_switch': 'Paying Zakat for each box from itself - Automated Mode',

    # zakat_page
    'zakat_page_label': 'Total wealth {} and total that reached one Haul or more {}',
    'refresh': 'Refresh',
    'pay': 'Pay',
    'below_nisab_note': 'Zakat due {} but the total {} is less than the Nisab {}',
    'table_show_row_details_note': 'Double tap or long press to view row details',
    'zakat_on_boxes_note': 'Zakat is done on the boxes within each account, so the name is repeated',
    'due': 'Due',
    'row_details': 'Row Details',
    'exchange_rate': 'Exchange Rate',
    'exchange_time': 'Exchange Time',
    'exchange_desc': 'Exchange Description',

    # file_server_page
    'open_in_web_browser': 'Open in Web Browser',

    # loading_page
    'loading': 'Loading',

    # csv_bad_records_report_page
    'csv_bad_records_report_page_title': '{} records failed to import, {} created & {} already imported',
    'csv_bad_records_report_note_1': 'Records are arranged from oldest to newest, if an error occurs the process stops immediately',
    'csv_bad_records_report_note_2': 'All data before the error has been entered, because the present depends on the past',
    'details': 'Details',

    # import_csv_file_scale_selection_page
    'import': 'Import',
    'import_csv_file_scale_selection_page_label': 'Numbers Scale Form',
    'import_csv_file_scale_selection_page_note': 'Zero means that the imported values ​​are normal and not scaled',
    'import_csv_file_scale_description': 'Computers face challenges in accurately handling the decimal point in storage and retrieval because their architecture is not fully compatible with it, so some software stores numbers in an enlarged way to try to solve this problem, for example, 1.23 when enlarged twice becomes 123 or enlarged to a million or enlarged 6 times and 1.23 becomes stored as 1230000',
    'scale_factor_for_values': 'The scale factor for financial values',
    'on_import_csv_with_selected_scale_title': 'Import Confirmation',
    'on_import_csv_with_selected_scale_message': 'Would you like to import data from a source with a scale of {}?',
    'on_cancel_import_csv_title': 'Cancel Import Process',
    'on_cancel_import_csv_message': 'Would you like to cancel the data import process?',

    # data_management_page
    'reset_data': 'Reset Database',
    'on_reset_database_message': 'Do you really want to clear the database?',
    'create_database_file_snapshot_before_any_recovery': 'Create a snapshot for database file before each recovery process',
    'data_history': 'Data History',
    'data_snapshot': 'Data Backup',
    'show_data': 'Show Data',
    'show_raw_data': 'Show Raw Data',
    'open_database_file': 'Open Database File',
    'import_csv_file': 'Import CSV File',
    'import_database_file': 'ّImport Database File',
    'save_database_file': 'Save Database File',
    'export_database_file': 'Export Database File',
    'file_server': 'Run File Server',
    'calculating_database_stats_on_startup': 'Calculate database statistics upon initial load',
    'ram_size': 'RAM Size',
    'database_file_size': 'Database File Size',
    'load_time': 'Time taken for initial startup',
    'refresh_time': 'The time it took for the data to be last updated',
    
    # settings_page
    'language': 'Language',
    'lang_note': 'After changing the language please close the application and open it again',
    'load_from_cache_when_possible': 'Load from cache memory if available',
    'show_hidden_accounts': 'View hidden accounts on the Accounts page',
    'data_management': 'Data Management',
    'silver_gram_price_in_local_currency': 'The price of a gram of silver in local currency',
    'silver_nisab_gram_quantity': 'The number of grams needed to reach the Nisab',
    'haul_time_cycle_in_days': 'Number of days in a year',
    'zakat_library_version': 'Zakat Library Version',
    'gui_version': 'Graphical User Interface (GUI) Library Version',
    'app_version': 'Application Version',
    
    # accounts_page
    'add': 'Add',
    'accounts_table_note': 'One-click to view details of boxes or logs in the account',
    'table_pagination_label': 'Number of records {} each page has {} element - Page {} of {}',
    'sn': 'no.',
    'transfer': 'Transfer',
    'account': 'Account',
    'balance': 'Balance',
    'box': 'Box',
    'log': 'Log',
    'yes': 'Yes',
    'no': 'No',

    # transactions_page
    'saturday': 'Saturday',
    'sunday': 'Sunday',
    'monday': 'Monday',
    'tuesday': 'Tuesday',
    'wednesday': 'Wednesday',
    'thursday': 'Thursday',
    'friday': 'Friday',
    'no_data': 'No Data',

    # account_tabs_page
    'boxes': 'Boxes',
    'logs': 'Logs',
    'exchanges': 'Exchanges',
    'hide_account': 'Hide account?',
    'zakatable': 'Is Zakat Activated?',
    'back': 'Back',
    'hide': 'Hide',

    # boxes_page
    'date': 'Date',
    'rest': 'Rest',
    'capital': 'Capital',
    'count': 'Count',
    'last': 'Last',
    'total': 'Total',

    # logs_page
    'value': 'Value',
    'desc': 'Description',

    # exchanges_page
    'exchanges_note': 'Exchange rates only affect Zakat calculations and transfers from one account to another',
    'rate': 'Rate',

    # account_table_on_activate
    'table_account_access_key': 'account',

    # exchange_form
    'exchange_form_label': 'Add exchange rate form',

    # transfer_form
    'financial_transfer_form': 'Financial Transfer Form',
    'from_account': 'From Account',
    'form_account_input_placeholder': 'Enter the name of the account transferring from...',
    'to_account': 'To Account',
    'to_account_input_placeholder': 'Enter the name of the account transferring to...',
    'transfer_amount_note': 'The exchange rates from the first account to the second account will be applied automatically, based on the last available exchange rate for them',

    # form
    'financial_transaction_form': 'Financial Transaction Form',
    'account_input_placeholder': 'Enter the account name...',
    'is_new_account_switch_text': 'Is this a new account?',
    'is_discount_switch_text': 'Is this a discount process?',
    'save': 'Save',

    # save
    'data_error': 'Data error',
    'all_fields_required_message': 'Please fill out all required fields',
    'operation_accomplished_successfully': 'Operation Accomplished Successfully',
    'message_status': 'Message Status',
    'unexpected_error': 'Unexpected Error',

    # transfer
    'transfer_to_the_same_account_error_message': 'It is not possible to transfer to the same account',

    # account_tab_page_label_widget
    'unit': 'Unit',

    # desc_widget
    'desc_input_placeholder': 'Write a description of the accounting process...',

    # amount_widget
    'amount': 'Amount',

    # rate_widget
    'rate': 'Rate',

    # datetime_widget
    'datetime_widget_label': 'Date and timing of the operation',
    'year': 'Year',
    'month': 'Month',
    'day': 'Day',
    'hour': 'Hour',
    'minute': 'Minute',
    'second': 'Second',

    # footer_widget
    'cancel': 'Cancel',
}