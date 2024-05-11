# UFORadarSEA

## Description
The UFORadarSEA is a desktop GUI application built using Python's Tkinter library. It allows users to explore UFO sighting data in Southeast Asia, create custom graphs based on various attributes, and submit new UFO sighting reports.

## Main Features
- View UFO sighting reports on a map. (View Map Page)
- Filter reports based on various criteria. (View Map Page)
- Create custom graphs based on user-selected attributes. (Graphs Page)
- Summary statistics of UFO sightings data, such as counts, mean, median, standard deviation, minimum, and maximum values for different attributes. (Graphs Page)
- Users can file a report of a UFO sighting. (File a Report Page)

## Requirements
Requires Python 3.11 or newer. 
- pillow>=10.2.0
- numpy>=1.26.4
- pandas>=2.2.1
- matplotlib>=3.8.3
- seaborn>=0.13.2
- tkintermapview>=1.29

## Screenshots
| <img src="./screenshots/main_menu.png" alt="Map page" width="300"/>         |  **Home Page**              |
|:----------------------------------------------------------------------------|:----------------------------|
| <img src="./screenshots/map_view_page.png" alt="Map page" width="300"/>     | **Map Page**                |
| <img src="./screenshots/graphs_page.png" alt="Map page" width="300"/>       | **Graphs Page**             |
| <img src="./screenshots/create_graph_page.png" alt="Map page" width="300"/> | **Create Graph Page**       |
| <img src="./screenshots/stat_page.png" alt="Map page" width="300"/>         | **Summary Statistics Page** |
| <img src="./screenshots/report_page.png" alt="Map page" width="300"/>       | **Report Page**             |

## Installation
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/pannlnwza/UFORadarSEA.git
    ```
2. Navigate to the project directory
   ```bash
   cd UFORadarSEA
    ```

## How To Run
To run the application, follow these steps:

```shell
python -m venv env
```
Activate the virtual environment using one of the following commands, depending on your operating system:

- **Windows:**

    ```bash
    env\Scripts\activate
    ```

- **macOS/Linux:**

    ```bash
    source env/bin/activate
    ```
Once the virtual environment is activated, install the required packages using pip:
```bash
pip install -r requirements.txt
```

Run the application:
```bash
python main.py
```

## Project Documents
- [Project Proposal](https://docs.google.com/document/d/1GFq37PgfiIjOqS0eIJ-mXynBxVIFKtayDh9qsmJY22A/edit?usp=sharing)
- [Development Plan](../../wiki/Development%20Plan)
- [UML Diagrams](../../wiki/UML%20Diagrams)

## Data Sources
The UFO Radar Application uses UFO sighting data sourced from [NUFORC](https://www.nuforc.org/) (National UFO Reporting Center) and The Global Airport Database (GADB) data by [Arash Partow](https://www.partow.net/miscellaneous/airportdatabase/).
