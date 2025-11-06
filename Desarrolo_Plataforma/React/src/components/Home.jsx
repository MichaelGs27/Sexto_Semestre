import React, { useState } from 'react';
import { Modal, Tab, Tabs, Form, Button, Alert, Container, Row, Col } from 'react-bootstrap';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { login, register } from '../services/auth.service';

const AuthModal = ({ show, handleClose }) => {
  const [key, setKey] = useState('login');
  const [error, setError] = useState('');

  const loginSchema = Yup.object().shape({
    email: Yup.string().email('Email inválido').required('Email es requerido'),
    password: Yup.string().required('Contraseña es requerida'),
  });

  const registerSchema = Yup.object().shape({
    username: Yup.string().required('Nombre de usuario es requerido'),
    email: Yup.string().email('Email inválido').required('Email es requerido'),
    password: Yup.string()
      .min(6, 'La contraseña debe tener al menos 6 caracteres')
      .required('Contraseña es requerida'),
  });

  const handleLogin = async (values, { setSubmitting }) => {
    try {
      await login(values.email, values.password);
      handleClose();
      window.location.reload();
    } catch (err) {
      setError(err.response?.data?.message || 'Error al iniciar sesión');
    }
    setSubmitting(false);
  };

  const handleRegister = async (values, { setSubmitting }) => {
    try {
      await register(values.username, values.email, values.password);
      setKey('login');
      setError('Registro exitoso! Por favor inicia sesión');
    } catch (err) {
      setError(err.response?.data?.message || 'Error al registrarse');
    }
    setSubmitting(false);
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>Acceder</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        <Tabs activeKey={key} onSelect={(k) => setKey(k)}>
          <Tab eventKey="login" title="Iniciar Sesión">
            <Formik
              initialValues={{ email: '', password: '' }}
              validationSchema={loginSchema}
              onSubmit={handleLogin}
            >
              {({ handleSubmit, handleChange, values, touched, errors }) => (
                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Label>Email</Form.Label>
                    <Form.Control
                      type="email"
                      name="email"
                      value={values.email}
                      onChange={handleChange}
                      isInvalid={touched.email && errors.email}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.email}
                    </Form.Control.Feedback>
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Contraseña</Form.Label>
                    <Form.Control
                      type="password"
                      name="password"
                      value={values.password}
                      onChange={handleChange}
                      isInvalid={touched.password && errors.password}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.password}
                    </Form.Control.Feedback>
                  </Form.Group>
                  <Button type="submit" variant="primary">
                    Iniciar Sesión
                  </Button>
                </Form>
              )}
            </Formik>
          </Tab>
          <Tab eventKey="register" title="Registrarse">
            <Formik
              initialValues={{ username: '', email: '', password: '' }}
              validationSchema={registerSchema}
              onSubmit={handleRegister}
            >
              {({ handleSubmit, handleChange, values, touched, errors }) => (
                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Label>Nombre de Usuario</Form.Label>
                    <Form.Control
                      type="text"
                      name="username"
                      value={values.username}
                      onChange={handleChange}
                      isInvalid={touched.username && errors.username}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.username}
                    </Form.Control.Feedback>
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Email</Form.Label>
                    <Form.Control
                      type="email"
                      name="email"
                      value={values.email}
                      onChange={handleChange}
                      isInvalid={touched.email && errors.email}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.email}
                    </Form.Control.Feedback>
                  </Form.Group>
                  <Form.Group className="mb-3">
                    <Form.Label>Contraseña</Form.Label>
                    <Form.Control
                      type="password"
                      name="password"
                      value={values.password}
                      onChange={handleChange}
                      isInvalid={touched.password && errors.password}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.password}
                    </Form.Control.Feedback>
                  </Form.Group>
                  <Button type="submit" variant="primary">
                    Registrarse
                  </Button>
                </Form>
              )}
            </Formik>
          </Tab>
        </Tabs>
      </Modal.Body>
    </Modal>
  );
};

const Home = ({ handleShowLogin }) => {
  return (
    <Container className="py-5">
      <Row className="justify-content-center text-center">
        <Col md={8}>
          <h1>Bienvenido a nuestra aplicación</h1>
          <p className="lead">
            Descubre todas las características increíbles que tenemos para ti
          </p>
          <Button 
            variant="primary" 
            size="lg" 
            onClick={handleShowLogin}
          >
            Comenzar ahora
          </Button>
        </Col>
      </Row>
    </Container>
  );
};

export default AuthModal;