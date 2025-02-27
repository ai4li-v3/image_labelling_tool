from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging
import os
import torch
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for handling English to Vietnamese translations"""
    
    def __init__(self):
        self.model_name = "Helsinki-NLP/opus-mt-en-vi"
        self.cache_dir = Path("models/helsinki-en-vi")
        self.tokenizer = None
        self.model = None
        self._initialize_logging()
        self._setup_cache_dir()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    def _setup_cache_dir(self):
        """Setup local cache directory for models"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_local_paths(self):
        """Get paths for local model files"""
        return {
            'tokenizer': self.cache_dir / 'tokenizer',
            'model': self.cache_dir / 'model'
        }
    
    def _initialize_logging(self):
        """Initialize logging for the translation service"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _ensure_model_loaded(self):
        """Ensure the model and tokenizer are loaded, using local cache if available"""
        try:
            paths = self._get_local_paths()
            
            if self.tokenizer is None:
                if paths['tokenizer'].exists():
                    logger.info("Loading tokenizer from local cache...")
                    self.tokenizer = AutoTokenizer.from_pretrained(str(paths['tokenizer']))
                else:
                    logger.info("Downloading tokenizer...")
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                    logger.info("Saving tokenizer to local cache...")
                    self.tokenizer.save_pretrained(str(paths['tokenizer']))
                
            if self.model is None:
                if paths['model'].exists():
                    logger.info("Loading model from local cache...")
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(str(paths['model']))
                else:
                    logger.info("Downloading model...")
                    self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                    logger.info("Saving model to local cache...")
                    self.model.save_pretrained(str(paths['model']))
                
                # Move model to appropriate device and set to evaluation mode
                self.model = self.model.to(self.device)
                self.model.eval()
                torch.set_grad_enabled(False)  # Globally disable gradients
                
        except Exception as e:
            logger.error(f"Error loading translation model: {str(e)}")
            raise RuntimeError(f"Failed to load translation model: {str(e)}")
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess input text for better translation quality"""
        # Remove extra whitespace and normalize
        text = ' '.join(text.split())
        
        # Handle empty or invalid input
        if not text:
            return text
            
        # Ensure proper sentence structure
        if not text[-1] in '.!?':
            text += '.'
            
        return text
    
    def _prepare_input(self, text: str) -> Dict[str, torch.Tensor]:
        """Prepare input text for translation"""
        try:
            # Clean and validate input
            cleaned_text = self._preprocess_text(text.strip())
            if not cleaned_text:
                raise ValueError("Empty input text")
                
            # Tokenize with proper error handling
            tokens = self.tokenizer(
                cleaned_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )
            
            # Move tokens to the same device as the model
            tokens = {k: v.to(self.device) for k, v in tokens.items()}
            
            logger.debug(f"Tokenized input: {tokens}")
            return tokens
            
        except Exception as e:
            logger.error(f"Error preparing input: {str(e)}")
            raise
    
    def get_suggestion(self, text: str) -> Optional[str]:
        """
        Get translation suggestion for English text
        
        Args:
            text (str): The English text to translate
            
        Returns:
            Optional[str]: The Vietnamese translation suggestion or None if error
            
        Note:
            This is a suggestion only - the user should review and accept/modify as needed
        """
        if not text or not isinstance(text, str):
            logger.warning("Invalid input type or empty text")
            return None
            
        try:
            # Ensure model is loaded
            self._ensure_model_loaded()
            
            # Prepare input with error handling
            inputs = self._prepare_input(text)
            
            # Generate translation with settings optimized for accuracy
            outputs = self.model.generate(
                **inputs,
                max_length=512,
                num_beams=8,  # Increased beam search for better accuracy
                length_penalty=1.0,  # Balanced length penalty
                early_stopping=True,
                no_repeat_ngram_size=3,
                do_sample=False,  # Disable sampling for deterministic output
                temperature=1.0,  # No temperature scaling
                top_k=1,  # Take only the best prediction
                repetition_penalty=1.0  # No repetition penalty
            )
            
            # Decode the translation
            suggestion = self.tokenizer.decode(
                outputs[0],
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            
            # Clean up the suggestion
            suggestion = suggestion.strip()
            
            logger.info(f"Successfully translated: '{text}' -> '{suggestion}'")
            return suggestion
            
        except ValueError as e:
            logger.warning(f"Invalid input: {str(e)}")
            return None
        except RuntimeError as e:
            logger.error(f"Model error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in translation: {str(e)}")
            return None
    
    def __del__(self):
        """Cleanup when the service is destroyed"""
        try:
            # Clear CUDA cache if available
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # Clear model and tokenizer
            self.model = None
            self.tokenizer = None
            
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}") 