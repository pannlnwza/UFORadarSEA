import os
from data_processor import UFODataProcessor
from uforadar_ui import UFOApp
from buttons import CreateButton


def main():
    """
    Main function to run the UFO Radar application.
    """
    current_dir = os.getcwd()
    ufo_data = os.path.join(current_dir, 'data', 'nuforc_data.csv')
    airport_data = os.path.join(current_dir, 'data', 'gadb_country_declatlon.csv')
    data_processor = UFODataProcessor(ufo_data, airport_data)
    app = UFOApp(data_processor)
    app.run()


if __name__ == "__main__":
    main()
