import React, { useState } from "react";
import axios from 'axios';
import "./styling/signup.css";

const SignUp = () => {

    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');

    const handleSignup = async () => {
        try {
        const response = await axios.post('http://localhost:5173/signup', { username, email, password });
        console.log(response.data);
        alert('Account created successfully!');
        window.location.href = '/'; // Redirect back to login
        } catch (error) {
        console.error(error.response.data.message);
        alert('Signup failed. Username might already be taken.');
        }
    };

    return (
        <div className="signup-container">
            <div className="signup-box">
                <h1>Sign Up</h1>
                <form>
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input type="text" placeholder="Username" className="input-field" value={username} onChange={(e) => setUsername(e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input type="email" placeholder="Email" className="input-field" value={email} onChange={(e) => setEmail(e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input type="password" placeholder="Password" className="input-field" value={password} onChange={(e) => setPassword(e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label htmlFor="confirm-password">Confirm Password</label>
                        <input type="password" id="confirm-password" placeholder="Re-enter your password" name="confirm-password" required />
                    </div>
                    <button className="signup-btn" onClick={handleSignup}>Sign Up</button>
                </form>
            </div>
        </div>
    );
}

export default SignUp;