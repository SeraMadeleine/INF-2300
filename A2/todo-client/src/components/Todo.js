import React, { useState } from 'react';
import TodoForm from './TodoForm';
import { RiCloseCircleLine } from 'react-icons/ri';
import { TiEdit } from 'react-icons/ti';

export default function Todo({ todos, completeToDo, removeTodo }) { // Changed 'completeTodo' to 'completeToDo'
    const [edit, setEdit] = useState({
    id: null,
    value: ''
    });

    return todos.map((todo, index) => (
    <div
        className={todo.isComplete ? 'todo-row complete' : 'todo-row'}
        key={index}
    >
    <div
        key={todo.id}
        onClick={() => completeToDo(todo.id)} // Changed 'completeTodo' to 'completeToDo'
    >
        {todo.text}
    </div>
    <div className='icons'>
        <RiCloseCircleLine 
            onClick={() => removeTodo(todo.id)}
            className='Delete-icon'
        />
        <TiEdit 
            onClick={() => setEdit({id: todo.id, value: todo.text})}
            className='edit-icon'
        />
    </div>
    </div>
  ));
}
