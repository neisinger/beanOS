from show_impressum import show_impressum
from change_date import change_date
from reset_daily_stats import reset_daily_stats
from reset_total_stats import reset_total_stats
from reset_factory_settings import reset_factory_settings
from maintenance_menu import maintenance_menu
from beancounter import show_beancounter

def handle_menu_selection(selected_option):
    if selected_option == "Impressum":
        show_impressum()
    elif selected_option == "Datum ändern":
        change_date()
    elif selected_option == "Tagessatistik zurücksetzen":
        reset_daily_stats()
    elif selected_option == "Gesamtstatistik zurücksetzen":
        reset_total_stats()
    elif selected_option == "Werkseinstellungen":
        reset_factory_settings()
    elif selected_option == "Wartung":
        maintenance_menu()
    elif selected_option == "BeanCounter":
        show_beancounter()