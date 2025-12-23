"""
Batch processor for Nano Banana image processing.
Handles queue management and background processing with progress signals.
"""

from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum
import traceback

from PyQt6.QtCore import QObject, QThread, pyqtSignal

from api_client import NanoBananaClient
from utils.image_utils import generate_output_filename


class ImageStatus(Enum):
    """Status of an image in the processing queue."""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class ImageItem:
    """Represents an image in the processing queue."""
    path: str
    status: ImageStatus = ImageStatus.PENDING
    error_message: str = ""
    output_path: str = ""
    
    @property
    def filename(self) -> str:
        return Path(self.path).name


@dataclass
class BatchJob:
    """Represents a batch processing job."""
    images: List[ImageItem] = field(default_factory=list)
    prompt: str = ""
    model: str = "gemini-2.5-flash-image"
    aspect_ratio: str = "original"
    output_quality: str = "standard"
    rename_pattern: str = "{original}_processed"
    output_folder: str = ""
    
    @property
    def total_count(self) -> int:
        return len(self.images)
    
    @property
    def completed_count(self) -> int:
        return sum(1 for img in self.images 
                   if img.status in (ImageStatus.SUCCESS, ImageStatus.ERROR, ImageStatus.CANCELLED))
    
    @property
    def success_count(self) -> int:
        return sum(1 for img in self.images if img.status == ImageStatus.SUCCESS)
    
    @property
    def error_count(self) -> int:
        return sum(1 for img in self.images if img.status == ImageStatus.ERROR)


class BatchWorker(QThread):
    """Worker thread for batch image processing."""
    
    # Signals
    progress = pyqtSignal(int, int)  # current, total
    image_started = pyqtSignal(str)  # image path
    image_completed = pyqtSignal(str, bool, str)  # image path, success, message/output_path
    batch_completed = pyqtSignal(int, int)  # success count, error count
    error = pyqtSignal(str)  # error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._job: Optional[BatchJob] = None
        self._client: Optional[NanoBananaClient] = None
        self._cancelled = False
    
    def setup(self, job: BatchJob, client: NanoBananaClient) -> None:
        """
        Set up the worker with a job and client.
        
        Args:
            job: BatchJob to process
            client: NanoBananaClient to use for API calls
        """
        self._job = job
        self._client = client
        self._cancelled = False
    
    def cancel(self) -> None:
        """Cancel the current batch processing."""
        self._cancelled = True
    
    def run(self) -> None:
        """Execute the batch processing."""
        if self._job is None or self._client is None:
            self.error.emit("Job ou client non configuré")
            return
        
        job = self._job
        output_folder = Path(job.output_folder) if job.output_folder else None
        
        # Create output folder if needed
        if output_folder:
            try:
                output_folder.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.error.emit(f"Impossible de créer le dossier de sortie: {e}")
                return
        
        # Get current date/time for rename pattern
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")
        
        success_count = 0
        error_count = 0
        
        for i, image_item in enumerate(job.images):
            if self._cancelled:
                image_item.status = ImageStatus.CANCELLED
                continue
            
            # Emit progress
            self.progress.emit(i + 1, job.total_count)
            self.image_started.emit(image_item.path)
            
            # Update status
            image_item.status = ImageStatus.PROCESSING
            
            try:
                # Process the image
                result_bytes, error_msg = self._client.edit_image(
                    image_path=image_item.path,
                    prompt=job.prompt,
                    model=job.model,
                    aspect_ratio=job.aspect_ratio,
                    output_quality=job.output_quality
                )
                
                if result_bytes and not error_msg:
                    # Generate output filename from pattern
                    original_stem = Path(image_item.path).stem
                    output_name = job.rename_pattern
                    output_name = output_name.replace("{original}", original_stem)
                    output_name = output_name.replace("{num}", f"{i+1:03d}")
                    output_name = output_name.replace("{date}", date_str)
                    output_name = output_name.replace("{time}", time_str)
                    output_filename = f"{output_name}.png"
                    
                    if output_folder:
                        output_path = output_folder / output_filename
                    else:
                        # Save next to original
                        output_path = Path(image_item.path).parent / output_filename
                    
                    # Ensure unique filename
                    counter = 1
                    base_output_name = output_name
                    while output_path.exists():
                        output_name = f"{base_output_name}_{counter}"
                        output_filename = f"{output_name}.png"
                        if output_folder:
                            output_path = output_folder / output_filename
                        else:
                            output_path = Path(image_item.path).parent / output_filename
                        counter += 1
                    
                    # Save the result
                    with open(output_path, 'wb') as f:
                        f.write(result_bytes)
                    
                    image_item.status = ImageStatus.SUCCESS
                    image_item.output_path = str(output_path)
                    success_count += 1
                    self.image_completed.emit(image_item.path, True, str(output_path))
                else:
                    image_item.status = ImageStatus.ERROR
                    image_item.error_message = error_msg or "Erreur inconnue"
                    error_count += 1
                    self.image_completed.emit(image_item.path, False, image_item.error_message)
                    
            except Exception as e:
                image_item.status = ImageStatus.ERROR
                image_item.error_message = f"Exception: {e}"
                error_count += 1
                self.image_completed.emit(image_item.path, False, image_item.error_message)
                traceback.print_exc()
        
        self.batch_completed.emit(success_count, error_count)


class BatchProcessor(QObject):
    """Manages batch image processing jobs."""
    
    # Signals (forwarded from worker)
    progress = pyqtSignal(int, int)
    image_started = pyqtSignal(str)
    image_completed = pyqtSignal(str, bool, str)
    batch_completed = pyqtSignal(int, int)
    error = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: Optional[BatchWorker] = None
        self._client: Optional[NanoBananaClient] = None
        self._current_job: Optional[BatchJob] = None
    
    def set_client(self, client: NanoBananaClient) -> None:
        """Set the API client to use."""
        self._client = client
    
    def is_running(self) -> bool:
        """Check if a batch is currently being processed."""
        return self._worker is not None and self._worker.isRunning()
    
    def start_batch(self, job: BatchJob) -> bool:
        """
        Start processing a batch job.
        
        Args:
            job: BatchJob to process
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running():
            self.error.emit("Un traitement est déjà en cours")
            return False
        
        if self._client is None:
            self.error.emit("Client API non configuré")
            return False
        
        if not job.images:
            self.error.emit("Aucune image à traiter")
            return False
        
        if not job.prompt.strip():
            self.error.emit("Le prompt est vide")
            return False
        
        self._current_job = job
        
        # Create and setup worker
        self._worker = BatchWorker()
        self._worker.setup(job, self._client)
        
        # Connect signals
        self._worker.progress.connect(self.progress)
        self._worker.image_started.connect(self.image_started)
        self._worker.image_completed.connect(self.image_completed)
        self._worker.batch_completed.connect(self._on_batch_completed)
        self._worker.error.connect(self.error)
        
        # Start processing
        self._worker.start()
        return True
    
    def cancel(self) -> None:
        """Cancel the current batch processing."""
        if self._worker:
            self._worker.cancel()
    
    def _on_batch_completed(self, success_count: int, error_count: int) -> None:
        """Handle batch completion."""
        self.batch_completed.emit(success_count, error_count)
        self._worker = None
    
    @property
    def current_job(self) -> Optional[BatchJob]:
        """Get the current job."""
        return self._current_job
