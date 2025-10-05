import { useState, useEffect, useCallback } from 'react'
// Restauramos las importaciones (si tu entorno local las puede resolver)
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [currentTime, setCurrentTime] = useState(0);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const [wordInput, setWordInput] = useState('');
  const [saveMessage, setSaveMessage] = useState('');
  const [wordList, setWordList] = useState([]);


  // --- FUNCIONES AUXILIARES (Lógica ya corregida) ---

  const fetchWords = useCallback(() => {
    if (token) {
      const WORDS_URL = 'http://localhost:5000/api/words';

      fetch(WORDS_URL, {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(response => response.ok ? response.json() : Promise.reject('Failed to fetch words'))
        .then(data => setWordList(data))
        .catch(error => console.error("Error fetching word list:", error));
    }
  }, [token]);


  const handleWordSubmit = (e) => {
    e.preventDefault();
    setSaveMessage('Saving...');
    if (!token) {
      setSaveMessage('Error: Not logged in (missing token).');
      return;
    }
    const SAVE_URL = 'http://localhost:5000/api/words';
    fetch(SAVE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ text: wordInput })
    })
      .then(response => response.json())
      .then(data => {
        if (data.message.includes('saved successfully')) {
          setSaveMessage(`Success: ${data.word} saved!`);
          setWordInput('');
          fetchWords();
        } else {
          setSaveMessage(`Error: ${data.message}`);
        }
      })
      .catch(error => {
        console.error("Error saving word:", error);
        setSaveMessage('Fatal error connecting to API.');
      });

  };
  const handleDeleteWord = (wordId) => {
    // NUEVA LÓGICA: Pedir confirmación antes de eliminar
    const isConfirmed = window.confirm("¿Estás seguro de que quieres eliminar esta palabra?");

    if (!isConfirmed) {
      // Si el usuario cancela, salimos de la función
      return;
    }

    if (!token) {
      console.error('Error: Not logged in (missing token).');
      return;
    }

    // El endpoint usa el ID de la palabra en la URL
    const DELETE_URL = `http://localhost:5000/api/words/${wordId}`;

    fetch(DELETE_URL, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(response => {
        // En una operación DELETE exitosa, el backend usualmente retorna 204 No Content
        if (response.status === 204) {
          console.log(`Word ID ${wordId} deleted successfully.`);
          fetchWords(); // Actualiza la lista
        } else if (!response.ok) {
          throw new Error('Failed to delete word, status: ' + response.status);
        }
      })
      .catch(error => {
        console.error("Error deleting word:", error);
      });

  };

  // --- EFECTOS (Hooks) ---

  useEffect(() => {
    const LOGIN_URL = 'http://localhost:5000/api/login';
    fetch(LOGIN_URL, { method: 'POST' })
      .then(response => response.json())
      .then(data => data.access_token ? setToken(data.access_token) : setLoading(false))
      .catch(error => setLoading(false));
  }, []);

  useEffect(() => {
    if (token) {
      const TIME_URL = 'http://localhost:5000/api/time';
      fetch(TIME_URL, { headers: { 'Authorization': `Bearer ${token}` } })
        .then(response => response.ok ? response.json() : Promise.reject('Time fetch failed'))
        .then(data => { setCurrentTime(data.time); setLoading(false); })
        .catch(error => setLoading(false));
    }
  }, [token]);

  useEffect(() => {
    fetchWords();
  }, [fetchWords]);


  // --- RENDERIZADO DE LA UI ---
  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Flask + React Full-Stack App</h1>

      {loading ? (
        <p>Loading API data (logging in...)</p>
      ) : (
        <h2>The server time is: {currentTime}</h2>
      )}

      {/* --- FORMULARIO --- */}
      <div className="card">
        <h3>Save a Word to PostgreSQL</h3>
        <form onSubmit={handleWordSubmit}>
          <input
            type="text"
            value={wordInput}
            onChange={(e) => setWordInput(e.target.value)}
            placeholder="Enter a word (e.g., 'Docker')"
            required
            disabled={loading}
          />
          <button type="submit" disabled={loading || !token}>
            Save Word
          </button>
        </form>
        {saveMessage && <p style={{ marginTop: '10px', color: saveMessage.includes('Error') ? 'red' : 'green' }}>{saveMessage}</p>}
      </div>

      {/* --- LISTA DE PALABRAS (TABLA) --- */}
      <div className="card word-list-container">
        <h3>Saved Words ({wordList.length})</h3>

        {token && wordList.length === 0 && loading ? (
          <p>Loading word list...</p>
        ) : wordList.length === 0 ? (
          <p>No words saved yet.</p>
        ) : (
          // Estructura de Tabla usando clases CSS
          <table className="word-table">
            <thead>
              <tr>
                <th>WORD</th>
                <th>SAVED AT</th>
                <th>ACTION</th>
              </tr>
            </thead>
            <tbody>
              {wordList.map((word, index) => (
                <tr key={word.id} className={index % 2 === 0 ? 'even-row' : 'odd-row'}>
                  <td className="word-text">{word.text}</td>
                  <td className="word-timestamp">{word.timestamp}</td>
                  <td className="word-action"> {/* <-- NUEVA CELDA */}
                    <button
                      className="delete-btn"
                      onClick={() => handleDeleteWord(word.id)}
                    >
                      🗑️ Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;