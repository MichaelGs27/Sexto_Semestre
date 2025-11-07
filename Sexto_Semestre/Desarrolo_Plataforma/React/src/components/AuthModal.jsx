import React, { useState } from 'react';
import { Modal, Tab, Tabs, Form, Button, Alert } from 'react-bootstrap';
import { Formik } from 'formik';
import * as Yup from 'yup';
import { login, register } from '../services/auth.service';

const AuthModal = ({ show, handleClose, onLoginSuccess }) => {
  const [key, setKey] = useState('login');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loginSchema = Yup.object().shape({
    email: Yup.string().email('Email inválido').required('Email es requerido'),
    password: Yup.string().required('Contraseña es requerida'),
  });

  const registerSchema = Yup.object().shape({
    name: Yup.string()
      .min(3, 'El nombre debe tener al menos 3 caracteres')
      .required('El nombre es requerido'),
    email: Yup.string()
      .email('Email inválido')
      .required('El email es requerido'),
    password: Yup.string()
      .min(6, 'La contraseña debe tener al menos 6 caracteres')
      .required('La contraseña es requerida')
  });

  const handleLogin = async (values, { setSubmitting }) => {
    try {
      const userData = await login(values.email, values.password);
      setError('');
      onLoginSuccess(userData);
    } catch (err) {
      setError(err.message || 'Error al iniciar sesión');
    }
    setSubmitting(false);
  };

  const handleRegister = async (values, { setSubmitting, resetForm }) => {
    try {
      setError('');
      setSuccess('');
      const result = await register(values.name, values.email, values.password);
      setSuccess(result.message || 'Registro exitoso! Por favor inicia sesión');
      resetForm();
      setTimeout(() => {
        setKey('login');
        setSuccess('');
      }, 2000);
    } catch (err) {
      setError(err.message || 'Error en el registro');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal show={show} onHide={handleClose}>
      <Modal.Header closeButton>
        <Modal.Title>{key === 'login' ? 'Iniciar Sesión' : 'Registrarse'}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}
        <Tabs activeKey={key} onSelect={(k) => setKey(k)}>
          <Tab eventKey="login" title="Iniciar Sesión">
            <Formik
              initialValues={{ email: '', password: '' }}
              validationSchema={loginSchema}
              onSubmit={handleLogin}
            >
              {({ handleSubmit, handleChange, values, touched, errors }) => (
                <Form noValidate onSubmit={handleSubmit}>
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
              initialValues={{
                name: '',
                email: '',
                password: ''
              }}
              validationSchema={registerSchema}
              onSubmit={handleRegister}
            >
              {({ handleSubmit, handleChange, values, touched, errors, isSubmitting }) => (
                <Form noValidate onSubmit={handleSubmit} className="mt-3">
                  <Form.Group className="mb-3">
                    <Form.Label>Nombre</Form.Label>
                    <Form.Control
                      type="text"
                      name="name"
                      value={values.name}
                      onChange={handleChange}
                      isInvalid={touched.name && errors.name}
                    />
                    <Form.Control.Feedback type="invalid">
                      {errors.name}
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

                  <Button 
                    type="submit" 
                    variant="primary" 
                    disabled={isSubmitting}
                    className="w-100"
                  >
                    {isSubmitting ? 'Registrando...' : 'Registrarse'}
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

export default AuthModal;