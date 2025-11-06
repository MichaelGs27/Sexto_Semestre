import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card, ListGroup, Nav } from 'react-bootstrap';
import { Navigate, useNavigate } from 'react-router-dom';
import { getUserProfile } from '../services/user.service';
import { logout } from '../services/auth.service';
import './Dashboard.css';

const Dashboard = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const userData = await getUserProfile();
        console.log('User profile data:', userData); // Debug log
        setUser(userData);
      } catch (error) {
        console.error('Error fetching user profile:', error);
        setError(error.message || 'Error al cargar los datos del usuario');
      } finally {
        setLoading(false);
      }
    };

    fetchUserProfile();
  }, []);

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
      </div>
    );
  }

  if (error) return <div className="error-message">{error}</div>;
  if (!user) return <Navigate to="/" />;

  return (
    <div className="dashboard-container">
      <div className="dashboard-sidebar">
        <div className="sidebar-header">
          <div className="user-avatar">
            <i className="bi bi-person-circle"></i>
          </div>
          <h5 className="user-name">{user.name || 'Usuario'}</h5>
          <p className="user-email">{user.email}</p>
        </div>
        <Nav className="flex-column sidebar-nav">
          <Nav.Link 
            active={activeTab === 'profile'} 
            onClick={() => setActiveTab('profile')}
          >
            <i className="bi bi-person me-2"></i>
            Perfil
          </Nav.Link>
          <Nav.Link 
            active={activeTab === 'settings'} 
            onClick={() => setActiveTab('settings')}
          >
            <i className="bi bi-gear me-2"></i>
            Configuración
          </Nav.Link>
          <Nav.Link 
            active={activeTab === 'amazon'} 
            onClick={() => setActiveTab('amazon')}
          >
            <i className="bi bi-gear me-2"></i>
            nuevo link
          </Nav.Link>
          <Nav.Link onClick={handleLogout}>
            <i className="bi bi-box-arrow-right me-2"></i>
            Cerrar Sesión
          </Nav.Link>
        </Nav>
      </div>
      
      <div className="dashboard-main">
        <div className="dashboard-header">
          <h4>Panel de Control</h4>
        </div>
        
        <div className="dashboard-content">
          <Container fluid>
            <Row className="justify-content-center">
              <Col md={10} lg={10}>
                <Row>
                  <Col md={6}>
                    <Card className="info-card">
                      <Card.Header>
                        <h5 className="mb-0">Información Personal</h5>
                      </Card.Header>
                      <Card.Body>
                        <ListGroup variant="flush">
                          <ListGroup.Item>
                            <strong>Nombre:</strong>
                            <span className="float-end">{user.name || 'No disponible'}</span>
                          </ListGroup.Item>
                          <ListGroup.Item>
                            <strong>Email:</strong>
                            <span className="float-end">{user.email}</span>
                          </ListGroup.Item>
                        </ListGroup>
                      </Card.Body>
                    </Card>
                  </Col>
                  
                  <Col md={6}>
                    <Card className="info-card">
                      <Card.Header>
                        <h5 className="mb-0">Actividad Reciente</h5>
                      </Card.Header>
                      <Card.Body>
                        <p className="text-muted">
                          Último acceso: {new Date().toLocaleString('es-ES')}
                        </p>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>
              </Col>
            </Row>
          </Container>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;