import React, { useState, useRef } from 'react';
import axios from 'axios';

const RegisterForm = () => {
    const [formData, setFormData] = useState({
        name: '',
        employee_id: '',
        department: '',
        date_of_birth: '',
    });
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const fileInputRef = useRef(null);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.type.startsWith('image/')) {
            setFile(selectedFile);
            setError(''); // Clear previous file-related errors
        } else {
            setFile(null);
            setError('Please select a valid image file.');
            if (fileInputRef.current) {
                fileInputRef.current.value = ''; // Reset file input
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');
        setError('');

        // Basic validation
        if (!formData.name || !formData.employee_id || !formData.department || !formData.date_of_birth || !file) {
            setError('All fields and a face image are required.');
            return;
        }

        setIsSubmitting(true);

        const data = new FormData();
        data.append('name', formData.name);
        data.append('employee_id', formData.employee_id);
        data.append('department', formData.department);
        data.append('date_of_birth', formData.date_of_birth);
        data.append('file', file);

        try {
            const response = await axios.post('http://localhost:8000/api/register', data, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setMessage(`Registration successful! User ID: ${response.data.user_id}`);
            // Reset form
            setFormData({ name: '', employee_id: '', department: '', date_of_birth: '' });
            setFile(null);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        } catch (err) {
            const errorMessage = err.response?.data?.detail || 'An unexpected error occurred.';
            setError(`Registration failed: ${errorMessage}`);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div style={{ maxWidth: '500px', margin: 'auto', padding: '20px', border: '1px solid #ccc', borderRadius: '10px' }}>
            <h2>Register New User</h2>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '15px' }}>
                    <label>Name:</label>
                    <input type="text" name="name" value={formData.name} onChange={handleInputChange} required style={{ width: '100%', padding: '8px' }} />
                </div>
                <div style={{ marginBottom: '15px' }}>
                    <label>Employee ID:</label>
                    <input type="text" name="employee_id" value={formData.employee_id} onChange={handleInputChange} required style={{ width: '100%', padding: '8px' }} />
                </div>
                <div style={{ marginBottom: '15px' }}>
                    <label>Department:</label>
                    <input type="text" name="department" value={formData.department} onChange={handleInputChange} required style={{ width: '100%', padding: '8px' }} />
                </div>
                <div style={{ marginBottom: '15px' }}>
                    <label>Date of Birth:</label>
                    <input type="date" name="date_of_birth" value={formData.date_of_birth} onChange={handleInputChange} required style={{ width: '100%', padding: '8px' }} />
                </div>
                <div style={{ marginBottom: '15px' }}>
                    <label>Face Image:</label>
                    <input type="file" name="file" accept="image/*" onChange={handleFileChange} ref={fileInputRef} required style={{ width: '100%', padding: '8px' }} />
                </div>
                <button type="submit" disabled={isSubmitting} style={{ width: '100%', padding: '10px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px' }}>
                    {isSubmitting ? 'Registering...' : 'Register'}
                </button>
            </form>
            {message && <p style={{ color: 'green', marginTop: '15px' }}>{message}</p>}
            {error && <p style={{ color: 'red', marginTop: '15px' }}>{error}</p>}
        </div>
    );
};

export default RegisterForm;
