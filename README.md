# UFORadarSEA
This is a preview release of the UFORadarSEA application.
## Overview
The UFO Radar Application is a Python GUI application that allows users to explore UFO sighting reports from South East Asia.

## Main Features
- View UFO sighting reports on a map. (View Map Page)
- Filter reports based on various criteria. (View Map Page)
- Create custom graphs based on user-selected attributes. (Graphs Page)
- Summary statistics of UFO sightings data, such as counts, mean, median, standard deviation, minimum, and maximum values for different attributes. (Graphs Page)
- Users can file a report of a UFO sighting. (File a Report Page)

## Installation
Clone this repository to your local machine:
   ```bash
   git clone https://github.com/pannlnwza/UFORadarSEA.git
   git checkout preview
```
## How To Run
To run the application, follow these steps:

```shell
python -m venv env
```
Activate the virtual environment using one of the following commands, depending on your operating system:

- **Windows:**

    ```bash
    .env\Scripts\activate
    ```

- **macOS/Linux:**

    ```bash
    source env/bin/activate
    ```
Once the virtual environment is activated, install the required packages using pip:
```bash
pip install -r requirements.txt
python main.py
```
