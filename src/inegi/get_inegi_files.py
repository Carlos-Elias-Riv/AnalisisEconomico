import os
import sys
import yaml
import pandas as pd
from pathlib import Path
from INEGIpy import Indicadores

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def load_config():
    """Load configuration from config.yaml"""
    config_path = project_root / 'config' / 'config.yaml'
    try:
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)

def get_inflacion(inegi_client, start_date, end_date):
    """
    Get the general inflation rate series
    """
    try:
        df_inflacion = inegi_client.obtener_df(
            indicadores="628229",  # ID del indicador de inflación general
            nombres="Inflación General",
            inicio=start_date,
            fin=end_date
        )
        
        # Convert date to datetime
        df_inflacion['date'] = pd.to_datetime(df_inflacion.index, format='%Y-%m-%d')
        df_inflacion['inflacion'] = df_inflacion['Inflación General']
        df_inflacion = df_inflacion[['date', 'inflacion']]
        
        return df_inflacion
    except Exception as e:
        print(f"Error getting inflation data: {e}")
        return None

def save_data(df, filename):
    """Save DataFrame to CSV in the data directory"""
    data_dir = project_root / 'data' / 'inegi'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = data_dir / filename
    try:
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error saving data to {output_path}: {e}")

def main():
    # Load configuration
    config = load_config()
    inegi_token = config['inegi_token']
    start_date = config['start_date'].replace('-', '')
    end_date = config['end_date'].replace('-', '')
    
    # Initialize INEGI client
    inegi_client = Indicadores(token=inegi_token)
    
    # Get data
    df_inflacion = get_inflacion(inegi_client, start_date, end_date)
    
    # Save data
    if df_inflacion is not None:
        save_data(df_inflacion, 'inflacion.csv')

if __name__ == "__main__":
    main() 