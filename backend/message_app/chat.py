import logging

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from message_app import db_
from message_app.data_classes import User, Contact, Message
from message_app import socketio
from sqlalchemy import insert, select, func, or_
from flask_socketio import join_room, emit, send
from .decorators import contact_required

logger = logging.getLogger(__name__)

bp = Blueprint('chat', __name__)

@bp.route('/chat/<room_id>', methods=['GET'])
@login_required
@contact_required
def chat(room_id, contact):
    """
        Endpoint for conversation page between the client and their contact.
        The @contact_required decorator ensures that the contact exists and has 
        been added to the client's contacts. Moreover it retrieves the contact 
        (as a Contact object) from the database, making it available to this 
        function. 
        
        Returns message history between client and contact.
    """
    resp = get_chat_messages(contact)
    return resp

def get_chat_messages(contact):
    """
        Retrieves message history between current_user and provided contact. 
        The messages are in order of creation time (earliest first)
        
        Notes on JSON fields:
        The 'is_own_message' subfield of 'messages' indicates if the message 
        originated from the client. 
        The 'is_mutual' field is true when both the client and contact have
        the added other as a contact. 
    
    Parameters
        contact: Contact object
    Returns JSON object:
        {
         'messages':
            [
                {
                    'id': Message.id,
                    'text': Message.text,
                    'sender': {
                        'uuid': User.uuid,
                        'username': User.user_name
                        },
                    'recipient': {
                        'uuid': User.uuid,
                        'username': User.user_name
                    },
                    'timestamp': Message.created_at.isoformat(),
                },
                ...
            ]
         'is_mutual': bool
        }
    """
    messages = db_.session.execute(
        select(
            Message,
            User.user_name.label('sender_name'),
            User.uuid.label('sender_uuid')
            )
            .join(User, Message.user_from == User.id)
            .where(
                or_(
                    (Message.user_from == current_user.id) & (Message.user_to == contact.id),
                    (Message.user_from == contact.id) & (Message.user_to == current_user.id)
                    )
                )
                .order_by(Message.created_at)
    ).all()
    
    formatted_messages = []
    for message, sender_name, sender_uuid in messages:
        recipient = db_.session.scalar(select(User).where(User.id == message.user_to))
        
        formatted_messages.append({
            "id": message.id,
            "text": message.text,
            "sender": {
                "uuid": sender_uuid,
                "username": sender_name
            },
            "recipient": {
                "uuid": recipient.uuid,
                "username": recipient.user_name
            },
            "timestamp": message.created_at.isoformat()
        })

    # Check whether each has added the other
    is_mutual = db_.session.execute(
        select(func.count())
        .select_from(Contact)
        .where(
            or_(
                (Contact.user == current_user.id) & (Contact.contact == contact.id),
                (Contact.user == contact.id) & (Contact.contact == current_user.id)
            )
        )
    ).scalar() == 2

    # If no message history, make sure to still send user info
    if not messages:
        formatted_messages.append({
            "id": None,
            "text": None,
            "sender": {
                "uuid": current_user.uuid,
                "username": current_user.user_name
            },
            "recipient": {
                "uuid": contact.uuid,
                "username": contact.user_name
            },
            "timestamp": None
        })

    return jsonify({'messages': formatted_messages, 'is_mutual': is_mutual})

#------------------------------------------------------------------------------
# Socket.IO handlers are defined in this section.
# These functions handle events ('connect', 'join', 'json') received from React.
#------------------------------------------------------------------------------
@socketio.on('connect', namespace='/chat')
def handle_chat_connect():
    """
        Allow real-time connections for logged-in users only.
    """
    if not current_user.is_authenticated:
        logger.warning("Rejected unauthenticated WebSocket connection")
        return False
    logger.info(f"User '{current_user.user_name}' connected to chat namespace")
    return True

@socketio.on('join', namespace='/chat')
def on_join(data):
    """
        data is expected to be a JSON:
            {'room': room_name}
        where room_name is calculated in the agreed way. 
        
        Puts user into the room.
        The user is obtained from the request context. 
        A confirmation message is emitted after room is joined. 
    """
    # TO DO:
    # - should authenticate that user has permission to access the room
    room = data['room']
    join_room(room)
    logger.info(f"User '{current_user.user_name}' joined room {room}")
    emit('room_joined', {'room': room})

# Handler for send events
@socketio.on('message', namespace='/chat')
def on_message(json):
    """
        Handler for receiving messages in JSON form.
        The receiveced JSON is expected to have the following form: 
            {
             'recipient_user_name': ...,
             'message': ...
            }
            
        The message is stored in the database and a JSON is broadcast to all
        clients in the room:
            {
                'id': Message.id,
                'text': Message.text,
                'sender': {
                    'uuid': User.uuid,
                    'username': User.user_name
                    },
                'recipient': {
                    'uuid': User.uuid,
                    'username': User.user_name
                },
                'timestamp': Message.created_at.isoformat(),
            }
            
        An error message is emitted if the db write fails. 
    """
    # TO DO: Validate message content (non-empty, length limits)
    json = json[0]
    msg = json['message']
    recipient_user_name = json['recipient_user_name']
    
    try:
        recipient = db_.session.scalar(select(User).where(User.user_name==recipient_user_name))
        msg = db_.session.scalar(insert(Message)
                         .returning(Message)
                         .values(user_from=current_user.id,
                                 user_to=recipient.id,
                                 text=msg)
        )
        db_.session.commit()
        room_id = min(current_user.uuid+recipient.uuid, recipient.uuid+current_user.uuid)
        data = {
            'id': msg.id,
            'text': msg.text,
            'sender': {
                    'uuid': current_user.uuid,
                    'username': current_user.user_name
                },
            'recipient': {
                'uuid': recipient.uuid,
                'username': recipient.user_name
            },
            'timestamp': msg.created_at.isoformat(),
            'room_id': room_id
        }
        send(data, broadcast=True, to=room_id)
        
    except Exception as e:
        logger.error(f"Database error when saving message: {e}")
        db_.session.rollback()
        emit('error', {'message': 'Failed to send message. Please try again.'}, broadcast=False)
        
@socketio.on('disconnect', namespace='/chat')
def handle_disconnect():
    """
        When a user navigates away, closes the tab, or loses internet connection,
        the WebSocket connection will automatically close.
        We log the disconnect event for debugging and potential "last seen" features.
    """
    if current_user.is_authenticated:
        logger.info(f"User '{current_user.user_name}' disconnected from chat")
    else:
        logger.debug("Anonymous user disconnected from chat")