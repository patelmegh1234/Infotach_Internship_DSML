import { useRef, useState, useCallback, type DragEvent, type ChangeEvent } from 'react';
import { Upload, FileAudio, X } from 'lucide-react';

interface AudioUploaderProps {
  onFileSelected: (file: File) => void;
  currentFile: File | null;
}

const ALLOWED_TYPES = ['audio/wav', 'audio/wave', 'audio/x-wav'];
const MAX_SIZE_BYTES = 50 * 1024 * 1024; // 50 MB

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export default function AudioUploader({ onFileSelected, currentFile }: AudioUploaderProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validateFile = useCallback((file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type) && !file.name.endsWith('.wav')) {
      return 'Only WAV audio files are supported.';
    }
    if (file.size > MAX_SIZE_BYTES) {
      return `File is too large. Maximum size is ${formatSize(MAX_SIZE_BYTES)}.`;
    }
    if (file.size === 0) {
      return 'The selected file is empty.';
    }
    return null;
  }, []);

  const handleFile = useCallback(
    (file: File) => {
      setError(null);
      const validationError = validateFile(file);
      if (validationError) {
        setError(validationError);
        return;
      }
      onFileSelected(file);
    },
    [onFileSelected, validateFile],
  );

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setDragOver(false);
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleFile(files[0] as File);
      }
    },
    [handleFile],
  );

  const handleBrowse = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const handleInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        handleFile(files[0] as File);
      }
      // Reset so same file can be re-selected
      e.target.value = '';
    },
    [handleFile],
  );

  const handleRemove = useCallback(() => {
    setError(null);
    onFileSelected(null as unknown as File);
  }, [onFileSelected]);

  if (currentFile) {
    return (
      <div className="uploader uploader--selected fade-in">
        <div className="uploader__selected-info">
          <FileAudio size={24} aria-hidden="true" />
          <div className="uploader__file-details">
            <span className="uploader__filename">{currentFile.name}</span>
            <span className="uploader__filesize">{formatSize(currentFile.size)}</span>
          </div>
        </div>
        <button
          type="button"
          className="uploader__remove"
          onClick={handleRemove}
          aria-label="Remove selected audio file"
        >
          <X size={20} />
        </button>
      </div>
    );
  }

  return (
    <div className="uploader-container">
      <div
        role="button"
        tabIndex={0}
        aria-label="Upload audio file. Drag and drop or click to browse."
        className={`uploader ${dragOver ? 'uploader--drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleBrowse}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            handleBrowse();
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".wav,audio/wav,audio/x-wav"
          className="uploader__input"
          onChange={handleInputChange}
          aria-hidden="true"
        />

        <Upload size={40} className="uploader__icon" aria-hidden="true" />
        <h3 className="uploader__title">Upload Audio for Analysis</h3>
        <p className="uploader__hint">Drag & Drop WAV file here</p>
        <div className="uploader__divider">
          <span>or</span>
        </div>
        <button type="button" className="btn btn-secondary uploader__browse-btn">
          Browse Files
        </button>
        <p className="uploader__limitation">WAV format, up to 50 MB</p>
      </div>

      {error && (
        <div className="uploader__error fade-in" role="alert">
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}

