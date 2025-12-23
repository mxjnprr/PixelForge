"""
Nano Banana (Gemini) API Client.
Provides a wrapper for the Gemini API for image editing and generation.
"""

from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import io
import time


class NanoBananaClient:
    """Client for interacting with Nano Banana (Gemini) API."""
    
    def __init__(self, api_key: str):
        """
        Initialize the client with an API key.
        
        Args:
            api_key: Gemini API key
        """
        self._api_key = api_key
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Gemini client."""
        try:
            from google import genai
            self._client = genai.Client(api_key=self._api_key)
        except ImportError:
            raise ImportError(
                "Le package google-genai n'est pas installé. "
                "Exécutez: pip install google-genai"
            )
        except Exception as e:
            raise RuntimeError(f"Erreur d'initialisation du client: {e}")
    
    def set_api_key(self, api_key: str) -> None:
        """
        Update the API key and reinitialize the client.
        
        Args:
            api_key: New API key
        """
        self._api_key = api_key
        self._initialize_client()
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test the API connection with the current key.
        
        Returns:
            Tuple of (success, message)
        """
        if not self._api_key:
            return False, "Clé API non configurée"
        
        if self._client is None:
            return False, "Client non initialisé"
        
        try:
            # Try a simple text generation to test the connection
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents="Say 'OK' if you can read this."
            )
            if response and response.text:
                return True, "Connexion réussie"
            return False, "Réponse vide de l'API"
        except Exception as e:
            error_msg = str(e)
            if "API_KEY" in error_msg.upper() or "INVALID" in error_msg.upper():
                return False, "Clé API invalide"
            return False, f"Erreur de connexion: {error_msg}"
    
    def edit_image(
        self,
        image_path: str,
        prompt: str,
        model: str = "gemini-2.5-flash-image",
        aspect_ratio: Optional[str] = None,
        output_quality: str = "standard",
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Edit an image using the specified prompt.
        
        Args:
            image_path: Path to the input image
            prompt: Editing prompt to apply
            model: Model to use for generation
            aspect_ratio: Output aspect ratio (e.g., "16:9", "1:1")
            output_quality: Output quality ("standard", "2K", "4K")
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        
        Returns:
            Tuple of (image_bytes, error_message)
            If successful, image_bytes contains PNG data and error_message is None
            If failed, image_bytes is None and error_message contains the error
        """
        if self._client is None:
            return None, "Client non initialisé"
        
        try:
            from google.genai import types
            from PIL import ExifTags
            
            # Load the input image and apply EXIF orientation
            input_image = Image.open(image_path)
            
            # Apply EXIF orientation to correct portrait/landscape rotation
            try:
                exif = input_image._getexif()
                if exif:
                    orientation_key = next(
                        (k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), 
                        None
                    )
                    if orientation_key and orientation_key in exif:
                        orientation = exif[orientation_key]
                        if orientation == 2:
                            input_image = input_image.transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation == 3:
                            input_image = input_image.rotate(180, expand=True)
                        elif orientation == 4:
                            input_image = input_image.transpose(Image.FLIP_TOP_BOTTOM)
                        elif orientation == 5:
                            input_image = input_image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation == 6:
                            input_image = input_image.rotate(-90, expand=True)
                        elif orientation == 7:
                            input_image = input_image.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation == 8:
                            input_image = input_image.rotate(90, expand=True)
            except Exception:
                pass  # If EXIF fails, continue with original image
            
            # Build configuration
            config_kwargs = {
                "response_modalities": ["Image", "Text"]
            }
            
            # Build image_config based on settings
            image_config_kwargs = {}
            
            # Only set aspect_ratio if it's not "original" (let API match input image)
            if aspect_ratio and aspect_ratio != "original":
                image_config_kwargs["aspect_ratio"] = aspect_ratio
            
            # Set image_size for 2K/4K quality (only works with Pro model)
            if output_quality in ("2K", "4K"):
                image_config_kwargs["image_size"] = output_quality
            
            if image_config_kwargs:
                config_kwargs["image_config"] = types.ImageConfig(**image_config_kwargs)
            
            config = types.GenerateContentConfig(**config_kwargs)
            
            # Attempt with retries
            last_error = None
            for attempt in range(max_retries):
                try:
                    response = self._client.models.generate_content(
                        model=model,
                        contents=[prompt, input_image],
                        config=config
                    )
                    
                    # Extract image from response
                    for part in response.parts:
                        if part.inline_data is not None:
                            # Get raw image bytes directly from inline_data
                            import base64
                            image_data = part.inline_data.data
                            # Data might be base64 encoded string or raw bytes
                            if isinstance(image_data, str):
                                image_bytes = base64.b64decode(image_data)
                            else:
                                image_bytes = image_data
                            return image_bytes, None
                    
                    # No image in response, check for text (might be an error or refusal)
                    for part in response.parts:
                        if part.text:
                            return None, f"L'API n'a pas généré d'image: {part.text[:200]}"
                    
                    return None, "L'API n'a pas retourné d'image"
                    
                except Exception as e:
                    last_error = str(e)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                        continue
                    break
            
            return None, f"Erreur après {max_retries} tentatives: {last_error}"
            
        except Exception as e:
            return None, f"Erreur de traitement: {e}"
    
    def generate_image(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash-image",
        aspect_ratio: str = "1:1",
        output_quality: str = "standard",
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Generation prompt
            model: Model to use for generation
            aspect_ratio: Output aspect ratio
            output_quality: Output quality ("standard", "2K", "4K")
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        
        Returns:
            Tuple of (image_bytes, error_message)
        """
        if self._client is None:
            return None, "Client non initialisé"
        
        try:
            from google.genai import types
            
            # Build image_config
            image_config_kwargs = {"aspect_ratio": aspect_ratio}
            
            # Set image_size for 2K/4K quality (only works with Pro model)
            if output_quality in ("2K", "4K"):
                image_config_kwargs["image_size"] = output_quality
            
            config = types.GenerateContentConfig(
                response_modalities=["Image", "Text"],
                image_config=types.ImageConfig(**image_config_kwargs)
            )
            
            last_error = None
            for attempt in range(max_retries):
                try:
                    response = self._client.models.generate_content(
                        model=model,
                        contents=[prompt],
                        config=config
                    )
                    
                    for part in response.parts:
                        if part.inline_data is not None:
                            import base64
                            image_data = part.inline_data.data
                            if isinstance(image_data, str):
                                image_bytes = base64.b64decode(image_data)
                            else:
                                image_bytes = image_data
                            return image_bytes, None
                    
                    for part in response.parts:
                        if part.text:
                            return None, f"L'API n'a pas généré d'image: {part.text[:200]}"
                    
                    return None, "L'API n'a pas retourné d'image"
                    
                except Exception as e:
                    last_error = str(e)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    break
            
            return None, f"Erreur après {max_retries} tentatives: {last_error}"
            
        except Exception as e:
            return None, f"Erreur de génération: {e}"
    
    def edit_image_with_sketch(
        self,
        original_image_path: str,
        sketch_image_path: str,
        prompt: str,
        model: str = "gemini-2.5-flash-image",
        aspect_ratio: Optional[str] = None,
        output_quality: str = "standard",
        max_retries: int = 3,
        retry_delay: float = 2.0
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Edit an image using a separate sketch/drawing to indicate the target area.
        
        This method sends BOTH the original image and a sketch showing where
        to apply changes, allowing the AI to understand the target zone
        without modifying the original image with overlays.
        
        Args:
            original_image_path: Path to the original image (unchanged)
            sketch_image_path: Path to the sketch/drawing showing the target zone
            prompt: Editing prompt to apply
            model: Model to use for generation
            aspect_ratio: Output aspect ratio
            output_quality: Output quality
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        
        Returns:
            Tuple of (image_bytes, error_message)
        """
        if self._client is None:
            return None, "Client non initialisé"
        
        try:
            from google.genai import types
            from PIL import ExifTags
            
            # Load the original image and apply EXIF orientation
            original_image = Image.open(original_image_path)
            
            # Apply EXIF orientation
            try:
                exif = original_image._getexif()
                if exif:
                    orientation_key = next(
                        (k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), 
                        None
                    )
                    if orientation_key and orientation_key in exif:
                        orientation = exif[orientation_key]
                        if orientation == 2:
                            original_image = original_image.transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation == 3:
                            original_image = original_image.rotate(180, expand=True)
                        elif orientation == 4:
                            original_image = original_image.transpose(Image.FLIP_TOP_BOTTOM)
                        elif orientation == 5:
                            original_image = original_image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation == 6:
                            original_image = original_image.rotate(-90, expand=True)
                        elif orientation == 7:
                            original_image = original_image.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
                        elif orientation == 8:
                            original_image = original_image.rotate(90, expand=True)
            except Exception:
                pass
            
            # Load the sketch image
            sketch_image = Image.open(sketch_image_path)
            
            # Build configuration
            config_kwargs = {
                "response_modalities": ["Image", "Text"]
            }
            
            image_config_kwargs = {}
            if aspect_ratio and aspect_ratio != "original":
                image_config_kwargs["aspect_ratio"] = aspect_ratio
            
            if output_quality in ("2K", "4K"):
                image_config_kwargs["image_size"] = output_quality
            
            if image_config_kwargs:
                config_kwargs["image_config"] = types.ImageConfig(**image_config_kwargs)
            
            config = types.GenerateContentConfig(**config_kwargs)
            
            # Build the prompt that explains the two images
            enhanced_prompt = (
                f"Je te fournis deux images:\n"
                f"1. L'IMAGE ORIGINALE que tu dois modifier\n"
                f"2. Un SCHÉMA/DESSIN montrant la zone à modifier (marquée avec des couleurs)\n\n"
                f"INSTRUCTION: {prompt}\n\n"
                f"IMPORTANT: Applique la modification UNIQUEMENT dans la zone indiquée par le dessin coloré. "
                f"Le reste de l'image originale doit rester identique et intact. "
                f"Ne reproduis PAS les traits de couleur du schéma dans l'image finale."
            )
            
            # Attempt with retries - send both images
            last_error = None
            for attempt in range(max_retries):
                try:
                    response = self._client.models.generate_content(
                        model=model,
                        contents=[enhanced_prompt, original_image, sketch_image],
                        config=config
                    )
                    
                    # Extract image from response
                    for part in response.parts:
                        if part.inline_data is not None:
                            import base64
                            image_data = part.inline_data.data
                            if isinstance(image_data, str):
                                image_bytes = base64.b64decode(image_data)
                            else:
                                image_bytes = image_data
                            return image_bytes, None
                    
                    for part in response.parts:
                        if part.text:
                            return None, f"L'API n'a pas généré d'image: {part.text[:200]}"
                    
                    return None, "L'API n'a pas retourné d'image"
                    
                except Exception as e:
                    last_error = str(e)
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay * (attempt + 1))
                        continue
                    break
            
            return None, f"Erreur après {max_retries} tentatives: {last_error}"
            
        except Exception as e:
            return None, f"Erreur de traitement: {e}"
