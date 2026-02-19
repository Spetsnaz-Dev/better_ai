import React from 'react';

function TaskList({ tasks, loading }) {
  if (loading) {
    return <div className="loading">Loading tasks...</div>;
  }

  if (!tasks || tasks.length === 0) {
    return <div className="empty-state">No tasks yet. Create one above!</div>;
  }

  return (
    <div className="task-list">
      <h2>Tasks</h2>
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>Category</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr key={task.id}>
              <td>
                <strong>{task.title}</strong>
                <p className="task-description">{task.description}</p>
              </td>
              <td>
                <span className={`category-badge category-${(task.category || 'other').toLowerCase()}`}>
                  {task.category || 'N/A'}
                </span>
              </td>
              <td>
                <span className={`status-badge status-${(task.status || 'pending').toLowerCase()}`}>
                  {task.status}
                </span>
              </td>
              <td>{new Date(task.created_at).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TaskList;
