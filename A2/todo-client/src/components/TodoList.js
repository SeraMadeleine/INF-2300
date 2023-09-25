import React, {useState} from 'react'
import TodoForm from './TodoForm'
import Todo from './Todo'

function TodoList() {
    const [todos, setTodos] = useState([])

    const addToDo = todo =>{
        if(!todo.text || /^\s*$/.test(todo.text)){
            return
        }

        // logging it in real time 
        const newTodos = [todo, ...todos]

        setTodos(newTodos)
    }

    const deleteTodo = id => {
        const removeArr = [...todos].filter(todo => todo.id !== id)

        setTodos(removeArr)
    }

    const completeToDo = id => {
        let updatedToDos = todos.map(todo => {
            if (todo.id === id){
                todo.isComplete = !todo.isComplete
            }
            return todo
        })
        setTodos(updatedToDos)
    }

    return (
        <div>
            <h1>Whats todays plan</h1>
            <TodoForm onSubmit={addToDo} />
            <Todo 
                todos={todos}
                completeToDo={completeToDo}
                removeTodo={deleteTodo}
            /> 
        </div>
    )
}

export default TodoList