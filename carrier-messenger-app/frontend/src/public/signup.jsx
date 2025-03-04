import React from "react";
import "./styling/signup.css";

const SignUp = () => {
    return (
        <div className="signup-container">
            <div className="signup-box">
                <h1>Sign Up</h1>
                <form>
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input type="text" id="username" name="username" required />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input type="password" id="password" name="password" required />
                    </div>
                    <button type="submit" className="signup-button">Sign Up</button>
                </form>
            </div>
        </div>
    );
}

export default SignUp;