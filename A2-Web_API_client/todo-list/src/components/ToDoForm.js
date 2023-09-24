import React, {useState} from 'react'

function ToDoForm() {
const [input, setInputs] = useState('')


  return (
    <form className='ToDo-form'> 
        <input 
            type='text'     
            placeholder='Add a ToDo' 
            value={input} 
            name='text' 
            className='ToDo-input'
        />
        <button 
            className='ToDo-button'>
            Add ToDo
        </button>
    </form>
  )
}

export default ToDoForm