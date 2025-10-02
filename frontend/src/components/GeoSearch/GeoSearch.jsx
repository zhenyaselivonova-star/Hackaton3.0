import React, { useState } from 'react'
import { searchAPI, uploadAPI } from '../../services/api.js'  // исправлен путь
import './GeoSearch.css'

const GeoSearch = () => {
  const [searchType, setSearchType] = useState('coords')
  const [searchResults, setSearchResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Данные для поиска по координатам
  const [coordData, setCoordData] = useState({
    latitude: '',
    longitude: '',
    radius: '1000'
  })

  // Данные для загрузки файла
  const [fileData, setFileData] = useState({
    files: []
  })

  const handleCoordSearch = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await searchAPI.searchByCoords(
        coordData.latitude,
        coordData.longitude,
        coordData.radius
      )
      setSearchResults(response.data.results || [])
      setSuccess(`Найдено ${response.data.results?.length || 0} изображений`)
    } catch (err) {
      setError('Ошибка поиска. Проверьте координаты.')
      setSearchResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    e.preventDefault()
    if (fileData.files.length === 0) {
      setError('Выберите файл для загрузки')
      return
    }

    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const response = await uploadAPI.uploadFiles(fileData.files)
      setSuccess('Файлы успешно загружены!')

      // После загрузки ищем похожие изображения
      if (response.data && response.data.length > 0) {
        const searchResponse = await searchAPI.searchImages({
          uploaded_files: response.data.map(file => file.id)
        })
        setSearchResults(searchResponse.data.results || [])
      }
    } catch (err) {
      setError('Ошибка загрузки файлов')
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    setFileData({
      files: Array.from(e.target.files)
    })
  }

  const handleCoordChange = (e) => {
    setCoordData({
      ...coordData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="geo-search">
      <h2>🔍 Поиск изображений по геоданным</h2>

      <div className="search-type-selector">
        <button
          className={`type-btn ${searchType === 'coords' ? 'active' : ''}`}
          onClick={() => setSearchType('coords')}
        >
          📍 По координатам
        </button>
        <button
          className={`type-btn ${searchType === 'file' ? 'active' : ''}`}
          onClick={() => setSearchType('file')}
        >
          📁 По изображению
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <div className="search-forms">
        {searchType === 'coords' && (
          <form onSubmit={handleCoordSearch} className="search-form">
            <div className="form-row">
              <div className="form-group">
                <label>Широта (latitude):</label>
                <input
                  type="number"
                  step="any"
                  name="latitude"
                  value={coordData.latitude}
                  onChange={handleCoordChange}
                  placeholder="55.7558"
                  required
                />
              </div>

              <div className="form-group">
                <label>Долгота (longitude):</label>
                <input
                  type="number"
                  step="any"
                  name="longitude"
                  value={coordData.longitude}
                  onChange={handleCoordChange}
                  placeholder="37.6173"
                  required
                />
              </div>

              <div className="form-group">
                <label>Радиус поиска (метры):</label>
                <input
                  type="number"
                  name="radius"
                  value={coordData.radius}
                  onChange={handleCoordChange}
                  placeholder="1000"
                  min="100"
                  max="100000"
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="search-button">
              {loading ? 'Поиск...' : '🔍 Найти изображения'}
            </button>
          </form>
        )}

        {searchType === 'file' && (
          <form onSubmit={handleFileUpload} className="search-form">
            <div className="form-group">
              <label>Выберите изображение:</label>
              <input
                type="file"
                accept="image/*"
                multiple
                onChange={handleFileChange}
                required
              />
              <small>Можно выбрать несколько файлов</small>
            </div>

            <button type="submit" disabled={loading} className="search-button">
              {loading ? 'Загрузка...' : '📤 Загрузить и найти'}
            </button>
          </form>
        )}
      </div>

      {loading && <div className="loading">Загрузка...</div>}

      {searchResults.length > 0 && (
        <div className="search-results">
          <h3>Результаты поиска ({searchResults.length})</h3>
          <div className="images-grid">
            {searchResults.map((image, index) => (
              <div key={index} className="image-card">
                {image.download_url ? (
                  <img
                    src={image.download_url}
                    alt={image.filename || 'Изображение'}
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/250x200?text=No+Image'
                    }}
                  />
                ) : (
                  <div className="no-image">📷 Нет изображения</div>
                )}
                <div className="image-info">
                  <h4>{image.filename || 'Без названия'}</h4>
                  <div className="image-meta">
                    {image.latitude && image.longitude && (
                      <div>📍 {image.latitude}, {image.longitude}</div>
                    )}
                    {image.address && (
                      <div>🏠 {image.address}</div>
                    )}
                    {image.created_at && (
                      <div>📅 {new Date(image.created_at).toLocaleDateString()}</div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {searchResults.length === 0 && !loading && (
        <div className="no-results">
          <p>Результатов не найдено. Попробуйте изменить параметры поиска.</p>
        </div>
      )}
    </div>
  )
}

export default GeoSearch