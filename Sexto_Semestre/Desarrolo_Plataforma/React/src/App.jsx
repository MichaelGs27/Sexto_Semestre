import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import Home from './components/Home';
import Dashboard from './components/Dashboard';
import AuthModal from './components/AuthModal';
import ProtectedRoute from './components/ProtectedRoute';
import { Container, Navbar, Button } from 'react-bootstrap';
import { logout } from './services/auth.service';

function App() {
  const [showAuth, setShowAuth] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const userData = JSON.parse(localStorage.getItem('user'));
    if (userData && userData.token) {
      setUser(userData);
    }
  }, []);

  const handleLogout = () => {
    logout();
    setUser(null);
    return <Navigate to="/" />;
  };

  return (
    <Router>
      <Navbar bg="light" expand="lg">
        <Container>
          <Navbar.Brand href="#home">Mi Aplicación</Navbar.Brand>
          <Navbar.Toggle />
          <Navbar.Collapse className="justify-content-end">
            {user ? (
              <>
                <Navbar.Text className="me-2">
                  Hola, {user.name || user.email}
                </Navbar.Text>
                <Button variant="outline-primary" onClick={handleLogout}>
                  Cerrar Sesión
                </Button>
              </>
            ) : (
              <Button variant="primary" onClick={() => setShowAuth(true)}>
                Iniciar Sesión
              </Button>
            )}
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <Routes>
        <Route path="/" element={
          user ? <Navigate to="/dashboard" /> : <Home handleShowLogin={() => setShowAuth(true)} />
        } />
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
      </Routes>

      <AuthModal 
        show={showAuth} 
        handleClose={() => setShowAuth(false)}
        onLoginSuccess={(userData) => {
          setUser(userData);
          setShowAuth(false);
        }}
      />
    </Router>
  );
}

export default App;