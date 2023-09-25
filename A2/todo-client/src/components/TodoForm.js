import React, { useState } from 'react';

function TodoForm(props) {
    const [input, setInput] = useState('');

    const handleChange = (e) => {
        setInput(e.target.value);
    };

    // Prevent form submission from refreshing the page
    const handleSubmit = (e) => {
        e.preventDefault();

        // Call the onSubmit function passed as a prop
        props.onSubmit({
            id: Math.floor(Math.random() * 10000),
            text: input,
        });

        setInput('');
    };

    return (
        <form className='todo-form' onSubmit={handleSubmit}>
            <input
                type='text'
                placeholder='Add a todo'
                value={input}
                name='text'
                className='todo-input'
                onChange={handleChange}
            />
            <button className='todo-button'>Add todo</button>
        </form>
    );
}

export default TodoForm;
