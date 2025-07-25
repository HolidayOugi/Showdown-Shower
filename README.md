# Showdown Shower

A Streamlit-based application to generate and visualize statistics from Pokémon Showdown user replays.
### A web demo is available [here](https://showdown-shower.streamlit.app/)!

## Features

- **Battle Page**: Displays statistics about each generation and see the most played Pokémon in each tier
- **Player Page**: Displays statistics on the most active players in each tier, along with a search bar to find specific players
- **Pokémon Page**: Displays statistics for the most played Pokémon in each tier, along with their most common moves and usage in battles

## How to run

Clone the repository:
   ```bash
   git clone https://github.com/HolidayOugi/Showdown-Shower
```

Navigate to the project directory:
   ```bash
   cd Showdown-Shower
   ```

Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

Run the Streamlit app:
   ```bash
    streamlit run main.py
   ```

## How to use the web application with local files

By default, the app looks for local files in the `output` folder. If none are found, it will download the latest available from this [Hugging Face repository](https://huggingface.co/datasets/HolidayOugi/showdown-shower-resources).

The formats to analyze can be set by editing the `formats.txt` file in the `input` folder. Each line should contain a format name in the form `[Gen X] FORMAT`.

## How to generate the local files

To generate your own local files, provide `.parquet` files (one per format) containing replays of Pokémon Showdown battles. Their names must match the format names listed in `formats.txt`.

The structure of these `.parquet` files should match that of downloaded replays from the Pokémon Showdown API. A collection of compatible datasets is available [here](https://huggingface.co/datasets/HolidayOugi/pokemon-showdown-replays).

If you are starting from scratch, place the `.parquet` files in the `input/parquet` folder and run the `initialize.py` script in the `code` folder:
   ```bash
   cd code
   python initialize.py
   ```
This will generate the necessary files in the `output` folder including:

- `tiers/`: Processed `.parquet` files for each tier  
- `players/`: Player statistics per tier in `.parquet` format  
- `matches/`: Monthly match statistics per generation  
- `graphs/`: Graphs per tier, displayed in the app  
- `replays/`: Replay files per Pokémon and format  
- `pokemon.parquet`: Overall Pokémon statistics by format  
- `invalid_pokemon.parquet`: List of invalid Pokémon based on the filters in `input/gen_filter/`

To add new replays to the existing files, you can place the new `.parquet` files in the `input/new_data` folder and run the `aggregate.py` script in the `code` folder:
   ```bash
   cd code
   python aggregate.py
   ```

This will merge the new data with the existing statistics in the `output` folder.


## Datasets used for this project

- [Metamon Replay Dataset by jakegrigsby](https://huggingface.co/datasets/jakegrigsby/metamon-raw-replays)
- [Pokemon with Stats by christofferms](https://www.kaggle.com/datasets/christofferms/pokemon-with-stats-and-image)
- [PokeAPI Sprites by PokeAPI](https://github.com/PokeAPI/sprites)

## Disclaimer

All Pokémon-related assets used in this project are the property of Nintendo, Game Freak, and The Pokémon Company. I do not claim ownership of these assets, which are used here for educational and non-commercial purposes only.


