import './App.css';

import React from 'react';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import LandingPage from './public/landingpage';
import SignUp from './public/signup';
import Main from './user/main';

import TestPage from './public/TestPage';

function App() {
  return (
    <div>
      <Router>
        <Routes>

          {/* Public Pages */}
          <Route path='/' element={<LandingPage />} />
          <Route path='/signup' element={<SignUp />} />
          {/* <Route path='/test' element={<TestPage />} /> */}
          
          {/* User Pages (Require Login) */}
          <Route path='/messages' element={<Main />} />
        
        </Routes>
      </Router>
    </div>
  );
}

export default App;
