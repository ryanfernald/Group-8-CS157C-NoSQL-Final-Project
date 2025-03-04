import './App.css';

import React from 'react';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import LandingPage from './public/landingpage';
import SignUp from './public/signup';
import MessageDisplay from './user/MessageDisplay';
import Sidebar from './user/Sidebar';
import Main from './user/main';

function App() {
  return (
    <div>
      <Router>
        <Routes>

          {/* Public Pages */}
          <Route path='/' element={<LandingPage />} />
          <Route path='/signup' element={<SignUp />} />
          
          {/* User Pages (Require Login) */}
          <Route path='/messages' element={<Main />} />
          <Route path='/sidebar' element={<Sidebar />} />
          <Route path='/message-display' element={<MessageDisplay />} />
        
        </Routes>
      </Router>
    </div>
  );
}

export default App;
