import './contacts.css'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUser } from '../UserContext.jsx'

/*
Pattern
    1. Component loads (ContactsList renders)
    2. useEffect runs and calls getContacts
    3. getContacts fetches data from Flask
    4. Store the fetched data in component state using useState
    5. Component re-renders with the new data
*/

function VisualContactsList({ contacts, clickHandler, idProperty, displayProperty }) {
    return (
            <>
                {
                    contacts.map(contact => (
                        <button onClick={(event) => clickHandler(contact)} className="contact-card" 
                            key={contact[idProperty]}>{contact[displayProperty]}</button>
                    ))
                }
            </>
    )
}

function ContactsList() {
    const [contactsData, setContacts] = useState([]);
    const [error, setError] = useState('');
    const { user, isLoading } = useUser();
    const navigate = useNavigate();

    useEffect(() => {
        getContacts();
    }, []);

    const getContacts = async () => {
        try {
            const response = await fetch('http://127.0.0.1:5000/contacts', { 
                method: 'GET', 
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include'  // send cookies with the request so Flask knows User is logged-in
            });
            const data = await response.json();
            const contactsData = data.contacts_data;
            setContacts(contactsData);
        }
        catch (err) {
            setError('Failed to retrieve contacts');
        }
    }

    const clickHandler = (contact) => {
        const s1 = user.uuid+contact.contact_uuid;
        const s2 = contact.contact_uuid+user.uuid;
        const roomId = s1 < s2 ? s1 : s2;
        navigate(`/chat/${roomId}`);
    }

    // Show loading while checking user session
    if (isLoading) {
        return <div>Loading...</div>;
    }

    // Show error if no user after loading completes
    if (!user.username) {
        return <div>Please log in to view contacts</div>;
    }

    return (
        <div className="contacts-container" id="outer-box">
            <h1>Starting chatting, {user.username}!</h1>
            <h1>Contacts</h1>
            <VisualContactsList contacts={contactsData} 
                                clickHandler={clickHandler}
                                idProperty="contact_uuid"
                                displayProperty="contact_name"
            />
        </div>
    )
}

export default ContactsList
export { VisualContactsList }