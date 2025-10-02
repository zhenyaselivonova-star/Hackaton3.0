import { useState, useRef } from 'react';
import { uploadAPI } from '../../services/api';

const UploadSection = ({ onAnalysisComplete }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      setSelectedFile(file);
    } else {
      alert('Пожалуйста, загрузите изображение');
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = '#f0f7ff';
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = '';
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.style.backgroundColor = '';

    if (e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      alert('Пожалуйста, выберите файл');
      return;
    }

    setLoading(true);

    try {
      const result = await uploadAPI.analyzeImage(selectedFile);
      onAnalysisComplete(result);
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      alert(error.message || 'Ошибка при анализе изображения');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-section">
      <h3>Загрузите фото для анализа</h3>
      <p>Наш ИИ найдет объекты на вашем изображении</p>

      <div
        className="upload-area"
        onClick={() => fileInputRef.current?.click()}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        {selectedFile ? (
          <>
            <div className="upload-icon">✅</div>
            <p>Файл "{selectedFile.name}" готов к анализу</p>
            <small>Нажмите "Проанализировать фото" для отправки</small>
          </>
        ) : (
          <>
            <div className="upload-icon">📷</div>
            <p>Перетащите сюда изображение или нажмите для выбора</p>
          </>
        )}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileInputChange}
          accept="image/*"
          style={{ display: 'none' }}
        />
      </div>

      <div className="profile-actions">
        <button
          className="btn"
          onClick={handleAnalyze}
          disabled={!selectedFile || loading}
        >
          {loading ? 'Анализ...' : 'Проанализировать фото'}
        </button>
      </div>
    </div>
  );
};

export default UploadSection;