import os
from django.apps import AppConfig
# Import the singleton instance of your MlServiceConfig
from .config import ml_config

class MlServiceConfig(AppConfig):
    name = 'ml_service'
    # No need for classifier_model, sentence_transformer, models_loaded here
    # as the ml_config singleton manages the model state.

    def ready(self):
        # This check ensures the model loading logic runs only once in the
        # main Django process, not in the reloader process during development.
        # The os.environ.get('RUN_MAIN', None) == 'true' is for Gunicorn/production.
        # The 'not os.environ.get('RUN_MAIN', None)' is for initial Django dev server run.
        if os.environ.get('RUN_MAIN', None) == 'true' or not os.environ.get('RUN_MAIN', None):
            # Call the load method on the singleton instance
            ml_config.load_models_on_startup()