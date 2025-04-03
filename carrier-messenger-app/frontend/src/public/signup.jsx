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
                        <input type="text" id="username" placeholder="Enter a custom Username" name="username" required />
                    </div>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input type="email" id="email" placeholder="Enter your email" name="email" required />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input type="password" id="password" placeholder="Enter your password" name="password" required />
                    </div>
                    <div className="form-group">
                        <label htmlFor="confirm-password">Confirm Password</label>
                        <input type="password" id="confirm-password" placeholder="Re-enter your password" name="confirm-password" required />
                    </div>
                    <button type="submit" className="signup-button">Sign Up</button>
                </form>
            </div>
        </div>
    );
}

export default SignUp;