import os
import logging
import joblib
from pathlib import Path
from django.conf import settings
from sentence_transformers import SentenceTransformer

BASE_DIR = settings.BASE_DIR

logger = logging.getLogger(__name__)

class MlServiceConfig:
    # Will hold the loaded classifier (e.g., SVC or GBDT)
    classifier_model = None
    # Will hold the loaded SentenceTransformer
    sentence_transformer = None

    def __init__(self):
        pass

    def load_models_on_startup(self) -> bool:
        models_dir = os.path.join(BASE_DIR, 'ml_service', 'models')
        
        logger.info(f"Attempting to load ML models from directory: {models_dir}")

        if not os.path.exists(models_dir):
            logger.critical(f"ML models directory not found at: {models_dir}. Cannot load models.")
            return False

        try:
            model_files = [f for f in os.listdir(models_dir) if f.startswith('best_model_') and f.endswith('.pkl')]
            if not model_files:
                logger.critical(f"No 'best_model_*.pkl' files found in {models_dir}.")
                return False

            latest_model_file = max(model_files, key=lambda f: os.path.getmtime(os.path.join(models_dir, f)))
            model_filepath = os.path.join(models_dir, latest_model_file)
            logger.info(f"Identified latest best model: {model_filepath}")

            # Load the pickled data, which is likely a dictionary
            with open(model_filepath, 'rb') as f:
                saved_data = joblib.load(f)
            
            # Check if the pickled data has the keys we expect
            if isinstance(saved_data, dict) and 'model' in saved_data and 'transformer' in saved_data:
                self.classifier_model = saved_data['model']
                self.sentence_transformer = SentenceTransformer(saved_data['transformer'])
                logger.info(f"Successfully loaded classifier model and SentenceTransformer.")
                return True
            else:
                logger.critical("Pickled data is not a dictionary with 'model' and 'transformer' keys.")
                return False

        except Exception as e:
            logger.critical(f"An error occurred during ML model loading: {e}", exc_info=True)
            self.classifier_model = None
            self.sentence_transformer = None
            return False
    
    def get_classifier(self):
        return self.classifier_model
    
    def get_transformer(self):
        return self.sentence_transformer

ml_config = MlServiceConfig()