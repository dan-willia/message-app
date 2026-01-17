import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './register-page.css'

function RegisterPage() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const navigate = useNavigate()

    const handleRegister = async () => {
    const requestBody = JSON.stringify({username, password})
    console.log(requestBody)                                    // for testing
    try {
        const response = await fetch('http://127.0.0.1:5000/auth/register',           // placeholder - should be our file structure or a proxy if we are testing
        {
            method: 'POST',                                     
            headers: { 'Content-Type': 'application/json' },    // this is for Flask to understand that the request is a json
            body: requestBody,                                   // converts the provided username, password into a json
            credentials: 'include'
        }
        );

        const data = await response.json();                     // Flask's response will be saved in data
        console.log(data)                                       // for testing

        if (data.status == 'success') {                                     
            alert("Registration success!");
            navigate('/login')                                  // if successful, return to login page
        } else {            
            setError(`${data.error}`)// Flask should tell us here that the credentials are invalid and why
        }
    } catch (err) {
        setError('Server Error: no response from Flask')
    }

    };

    return (
        <div className="register-container">
            <h1>Register Here</h1>
            <form className="form-container" onSubmit={(e) => {e.preventDefault(); handleRegister(); }}>
                <label>username</label>
                <br />
                <input id="username-input" className="login-input" value={username} onChange={(e) => setUsername(e.target.value)} />
                <br />
                <label>password</label>
                <br />
                <input id="password-input" className="login-input" value={password} onChange={(e) => setPassword(e.target.value)} type="password"/>
                <br />
                <button className="register-button" type ="submit" onClick={handleRegister}>register</button>
                <br />
                <p className='error-message'>{error}</p>
            </form>
        </div>
    )
}

export default RegisterPage