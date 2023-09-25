import React, { useState } from 'react';
import TodoForm from './TodoForm';
import Todo from './Todo';

function TodoList() {
    const [todos, setTodos] = useState([]);

    const addToDo = (todo) => {
        if (!todo.text || /^\s*$/.test(todo.text)) {
            return;
        }

        const newTodos = [todo, ...todos];
        setTodos(newTodos);
    };

    const editToDo = (todoId, newValue) => {
        if (!newValue.text || /^\s*$/.test(newValue.text)) {
            return;
        }

        setTodos((prev) =>
            prev.map((item) => (item.id === todoId ? newValue : item))
        );
    };

    const deleteTodo = (id) => {
        const removeArr = todos.filter((todo) => todo.id !== id);
        setTodos(removeArr);
    };

    const completeToDo = (id) => {
        const updatedTodos = todos.map((todo) => {
            if (todo.id === id) {
                return { ...todo, isComplete: !todo.isComplete };
            }
            return todo;
        });
        setTodos(updatedTodos);
    };

    return (
        <div>
            <h1>What's today's plan</h1>
            <TodoForm onSubmit={addToDo} />
            <Todo
                todos={todos}
                completeToDo={completeToDo}
                deleteTodo={deleteTodo}
                editToDo={editToDo}
            />
        </div>
    );
}

export default TodoList;
