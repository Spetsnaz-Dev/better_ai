import React, { useState, useEffect } from 'react';
import TaskForm from './components/TaskForm.jsx';
import TaskList from './components/TaskList.jsx';
import { createTask, getTasks } from './api.js';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const data = await getTasks();
      setTasks(data);
      setError(null);
    } catch (err) {
      setError('Failed to load tasks.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleTaskCreated = async (taskData) => {
    await createTask(taskData);
    await fetchTasks();
  };

  return (
    <div className="app-container">
      <header>
        <h1>InfraTask</h1>
        <p>AI-Assisted Task Classification</p>
      </header>
      <main>
        {error && <div className="error-message">{error}</div>}
        <TaskForm onTaskCreated={handleTaskCreated} />
        <TaskList tasks={tasks} loading={loading} />
      </main>
    </div>
  );
}

export default App;
