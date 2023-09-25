import React, { useState } from 'react';
import TodoForm from './TodoForm';
import { RiCloseCircleLine } from 'react-icons/ri';
import { TiEdit } from 'react-icons/ti';

export default function Todo({ todos, completeToDo, deleteTodo, editToDo }) {
    const [edit, setEdit] = useState({
        id: null,
        value: '',
    });

    const submitUpdate = (text) => {
        editToDo(edit.id, text); // Pass the edited text as a parameter
        setEdit({
            id: null,
            value: '',
        });
    };

    if (edit.id) {
        return (
            <TodoForm
                edit={edit}
                onSubmit={(editedText) => submitUpdate(editedText)} // Pass the edited text to submitUpdate
            />
        );
    }

    return todos.map((todo, index) => (
        <div
            className={todo.isComplete ? 'todo-row complete' : 'todo-row'}
            key={index}
        >
            <div
                key={todo.id}
                onClick={() => completeToDo(todo.id)}
            >
                {todo.text}
            </div>
            <div className='icons'>
                <RiCloseCircleLine
                    onClick={() => deleteTodo(todo.id)}
                    className='Delete-icon'
                />
                <TiEdit
                    onClick={() => setEdit({ id: todo.id, value: todo.text })}
                    className='edit-icon'
                />
            </div>
        </div>
    ));
}
