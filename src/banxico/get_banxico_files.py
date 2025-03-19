import os
import sys
import yaml
import pandas as pd
from pathlib import Path
from sie_banxico import SIEBanxico

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

def get_tipo_cambio(banxico_token, init_date, end_date):
    """
    Get the peso/USD exchange rate series (FIX daily exchange rate)
    """
    try:
        banxico_client = SIEBanxico(token=banxico_token, id_series=["SF43718"])
        raw_data = banxico_client.get_timeseries_range(
            init_date=init_date,
            end_date=end_date
        )
        
        df_tipo_cambio = pd.DataFrame(raw_data['bmx']['series'][0]['datos'])
        df_tipo_cambio['date'] = pd.to_datetime(df_tipo_cambio['fecha'], format='%d/%m/%Y')
        df_tipo_cambio['tipo_de_cambio'] = df_tipo_cambio['dato']
        df_tipo_cambio = df_tipo_cambio[['date', 'tipo_de_cambio']]
        
        return df_tipo_cambio
    except Exception as e:
        print(f"Error getting tipo de cambio data: {e}")
        return None

def get_tasa_interes(banxico_token, init_date, end_date):
    """
    Get the interbank equilibrium interest rate series
    """
    try:
        banxico_client = SIEBanxico(token=banxico_token, id_series=["SF61745"])
        raw_data = banxico_client.get_timeseries_range(
            init_date=init_date,
            end_date=end_date
        )
        
        df_tasa_interes = pd.DataFrame(raw_data['bmx']['series'][0]['datos'])
        df_tasa_interes['date'] = pd.to_datetime(df_tasa_interes['fecha'], format='%d/%m/%Y')
        df_tasa_interes['tasa_de_interes'] = df_tasa_interes['dato']
        df_tasa_interes = df_tasa_interes[['date', 'tasa_de_interes']]
        
        return df_tasa_interes
    except Exception as e:
        print(f"Error getting tasa de interés data: {e}")
        return None

def save_data(df, filename):
    """Save DataFrame to CSV in the data directory"""
    data_dir = project_root / 'data' / 'banxico'
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
    banxico_token = config['banxico_token']
    start_date = config['start_date']
    end_date = config['end_date']
    
    # Get data
    df_tipo_cambio = get_tipo_cambio(banxico_token, start_date, end_date)
    df_tasa_interes = get_tasa_interes(banxico_token,start_date, end_date)
    
    # Save data
    if df_tipo_cambio is not None:
        save_data(df_tipo_cambio, 'tipo_cambio.csv')
    if df_tasa_interes is not None:
        save_data(df_tasa_interes, 'tasa_interes.csv')

if __name__ == "__main__":
    main() 