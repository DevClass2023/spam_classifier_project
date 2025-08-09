from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny # Import AllowAny
from django.views.decorators.csrf import csrf_exempt # Import csrf_exempt
from django.utils.decorators import method_decorator # Import method_decorator for class-based views

from .config import ml_config
from core.models import EmailClassification
import logging

logger = logging.getLogger(__name__)

# Apply csrf_exempt decorator to the dispatch method of the APIView
@method_decorator(csrf_exempt, name='dispatch')
class PredictSpamAPIView(APIView): # Removed LoginRequiredMixin
    permission_classes = [AllowAny] # Explicitly allow any user (authenticated or not)

    def post(self, request, *args, **kwargs):
        # Note: request.user will be an AnonymousUser if not logged in.
        # Adjust logging if you only want to log authenticated users.
        logger.info(f"Predict request received. User: {request.user.username if request.user.is_authenticated else 'Anonymous'}")

        data = request.data
        email_text = data.get('email_text')

        if not email_text:
            logger.warning(f"Predict: Missing 'email_text' in request data from user {request.user.username if request.user.is_authenticated else 'Anonymous'}.")
            return Response({"error": "Email text ('email_text') is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        classifier_model = ml_config.get_classifier()
        sentence_transformer = ml_config.get_transformer()

        if not classifier_model or not sentence_transformer:
            logger.critical("ML models are not loaded. This indicates a startup failure. Check server logs.")
            return Response({"error": "ML models are not ready. Please try again or contact support."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            email_embedding = sentence_transformer.encode([email_text], convert_to_tensor=False)
            logger.debug(f"Predict: Email text vectorized for user {request.user.username if request.user.is_authenticated else 'Anonymous'}.")

            if not hasattr(classifier_model, 'predict_proba'):
                logger.error(f"Predict: Loaded classifier model does not have 'predict_proba' method. Model type: {type(classifier_model)}")
                return Response({"error": "Classifier model is not configured for probability prediction."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Get the numerical prediction (e.g., 0 or 1)
            prediction_numeric = classifier_model.predict(email_embedding)[0]

            # Get the probabilities for each class
            prediction_proba = classifier_model.predict_proba(email_embedding)[0]

            # Get the class labels from the model itself
            classes = classifier_model.classes_

            # Map the numerical prediction to the correct string label
            prediction_label = classes[prediction_numeric]
            
            # Find the probabilities for 'ham' and 'spam' based on their labels in the model
            try:
                spam_probability_index = list(classes).index('spam')
                ham_probability_index = list(classes).index('ham')
            except ValueError:
                logger.warning("Model classes are numeric. Assuming 1=spam and 0=ham.")
                spam_probability = prediction_proba[1]
                ham_probability = prediction_proba[0]
                
                prediction_label = 'spam' if prediction_numeric == 1 else 'ham'
                confidence = spam_probability if prediction_label == 'spam' else ham_probability
                
            else:
                spam_probability = prediction_proba[spam_probability_index]
                ham_probability = prediction_proba[ham_probability_index]
                confidence = spam_probability if prediction_label == 'spam' else ham_probability

            # Save classification to database
            # For unauthenticated requests from Postfix, we'll assign to a default user or handle differently.
            # For thesis purposes, you might want to create a dedicated 'system' user for these classifications.
            # For now, if request.user is AnonymousUser, it won't save a user.
            # If you want to save these, you might need to fetch a specific user or allow null=True on the user field in your model.
            
            # Temporary solution for unauthenticated requests:
            # If you want to save these classifications, you'll need to decide how to link them to a user.
            # For a system like this, you might create a dedicated 'system' user in Django and assign these to it.
            # For now, let's assume you're okay with them not being linked to a specific user if the request is anonymous.
            # Or, if you want them saved, ensure your EmailClassification.user field allows null=True or a default.
            
            user_instance = request.user if request.user.is_authenticated else None # Assign None for anonymous users

            classification_instance = EmailClassification.objects.create(
                user=user_instance, # This will be None if not authenticated
                email_text=email_text,
                classified_as=prediction_label,
                prediction_confidence=confidence
            )
            logger.info(f"Predict: Email (ID: {classification_instance.id}) classified as {prediction_label} with confidence {confidence:.4f} by {'Authenticated User' if request.user.is_authenticated else 'System/Anonymous'}.")

            return Response({
                "prediction": prediction_label,
                "confidence": round(confidence, 4),
                "email_text": email_text,
                "classification_id": classification_instance.id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Predict: An unhandled exception occurred during prediction for user {request.user.username if request.user.is_authenticated else 'Anonymous'}: {e}")
            return Response({"error": "An internal server error occurred during prediction. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)