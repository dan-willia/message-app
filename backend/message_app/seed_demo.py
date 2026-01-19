"""
Demo data seeding using Faker for realistic test data.

Usage:
    flask seed-demo          # Add demo data to existing DB
    flask seed-demo --reset  # Reset DB and add demo data
"""
import logging
import random
from datetime import datetime, timedelta, timezone

import click
from faker import Faker
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from . import db_
from .data_classes import User, Message, Contact
from .db import init_db

# Suppress faker's verbose logging
logging.getLogger('faker').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
fake = Faker()

# Demo user configurations
DEMO_USERS = [
    {'username': 'alice', 'password': 'demo123', 'role': 'primary'},
    {'username': 'bob', 'password': 'demo123', 'role': 'friend'},
    {'username': 'carol', 'password': 'demo123', 'role': 'colleague'},
    {'username': 'david', 'password': 'demo123', 'role': 'family'},
    {'username': 'emma', 'password': 'demo123', 'role': 'new_contact'},
    {'username': 'frank', 'password': 'demo123', 'role': 'one_way'},
]

# Conversation templates for different relationship types
CONVERSATION_TEMPLATES = {
    'friend': {
        'message_count': (15, 25),
        'timespan_days': 14,
        'topics': [
            "Hey! How's it going?",
            "Did you see the game last night?",
            "Want to grab coffee this weekend?",
            "That's hilarious 😂",
            "I was thinking about what you said...",
            "Are you free tomorrow?",
            "Just saw this and thought of you",
            "Remember when we...",
            "I can't believe it's already {month}!",
            "What are you up to this weekend?",
            "That restaurant you recommended was amazing!",
            "I need your advice on something",
            "Guess what happened today!",
            "Sorry for the late reply, been so busy",
            "Let's plan something fun soon",
        ]
    },
    'colleague': {
        'message_count': (8, 12),
        'timespan_days': 7,
        'topics': [
            "Hi, do you have a minute to chat about the project?",
            "Can you review my PR when you get a chance?",
            "The meeting has been moved to 3pm",
            "Good catch on that bug!",
            "I'll send over the docs shortly",
            "Let me know if you need any help",
            "Thanks for your help earlier",
            "Quick question about the API...",
            "The deployment went smoothly",
            "I'll be out tomorrow, FYI",
        ]
    },
    'family': {
        'message_count': (5, 8),
        'timespan_days': 5,
        'topics': [
            "Hey, how are you doing?",
            "Mom says hi!",
            "Don't forget about Sunday dinner",
            "Did you get my email about the trip?",
            "Call me when you get a chance",
            "Love you!",
            "Safe travels!",
            "Happy to hear that!",
        ]
    },
    'new_contact': {
        'message_count': (2, 4),
        'timespan_days': 1,
        'topics': [
            "Hey! Nice to meet you at the event",
            "Great chatting with you!",
            "Let's stay in touch",
            "Looking forward to connecting more",
        ]
    },
}


def create_demo_users():
    """Create demo users and return a dict mapping username to User object."""
    users = {}
    for user_config in DEMO_USERS:
        user = User(
            user_name=user_config['username'],
            user_pwd=generate_password_hash(user_config['password'])
        )
        db_.session.add(user)
        users[user_config['username']] = user
        
    db_.session.flush()  # Get IDs assigned
    logger.info(f"Created {len(users)} demo users")
    return users


def create_contacts(users):
    """Create contact relationships between users."""
    contacts_to_add = [
        # Mutual contacts
        ('alice', 'bob'),
        ('bob', 'alice'),
        ('alice', 'carol'),
        ('carol', 'alice'),
        ('alice', 'david'),
        ('david', 'alice'),
        ('bob', 'carol'),
        ('carol', 'bob'),
        # One-way contacts (alice added them, they haven't added back)
        ('alice', 'emma'),
        ('alice', 'frank'),
    ]

    for user_name, contact_name in contacts_to_add:
        contact = Contact(
            user=users[user_name].id,
            contact=users[contact_name].id
        )
        db_.session.add(contact)

    logger.info(f"Created {len(contacts_to_add)} contact relationships")


def generate_conversation(user1, user2, relationship_type):
    """Generate a realistic conversation between two users."""
    template = CONVERSATION_TEMPLATES.get(relationship_type, CONVERSATION_TEMPLATES['friend'])

    min_msgs, max_msgs = template['message_count']
    message_count = random.randint(min_msgs, max_msgs)
    timespan = timedelta(days=template['timespan_days'])

    # Start time is timespan days ago
    start_time = datetime.now(timezone.utc) - timespan

    messages = []
    current_time = start_time

    # Alternate between users with some randomness
    current_sender = user1
    current_receiver = user2

    for _ in range(message_count):
        # Pick a message from templates or generate with Faker
        if random.random() < 0.7 and template['topics']:
            text = random.choice(template['topics'])
            # Replace placeholders
            text = text.format(month=fake.month_name())
        else:
            # Use Faker for variety
            text = random.choice([
                fake.sentence(),
                fake.text(max_nb_chars=100),
                "👍",
                "Sounds good!",
                "Ok",
                "Sure thing",
                "Thanks!",
                "Got it",
            ])

        msg = Message(
            user_from=current_sender.id,
            user_to=current_receiver.id,
            text=text,
            created_at=current_time
        )
        messages.append(msg)

        # Advance time randomly (5 minutes to 8 hours between messages)
        time_gap = timedelta(
            minutes=random.randint(5, 60),
            hours=random.randint(0, 8)
        )
        current_time += time_gap

        # Switch sender with 60% probability (creates natural back-and-forth)
        if random.random() < 0.6:
            current_sender, current_receiver = current_receiver, current_sender

    return messages


def create_messages(users):
    """Create message history between users."""
    conversations = [
        ('alice', 'bob', 'friend'),
        ('alice', 'carol', 'colleague'),
        ('alice', 'david', 'family'),
        ('alice', 'emma', 'new_contact'),
        ('bob', 'carol', 'colleague'),
    ]

    total_messages = 0
    for user1_name, user2_name, relationship in conversations:
        messages = generate_conversation(
            users[user1_name],
            users[user2_name],
            relationship
        )
        for msg in messages:
            db_.session.add(msg)
        total_messages += len(messages)
        logger.debug(f"Created {len(messages)} messages between {user1_name} and {user2_name}")

    logger.info(f"Created {total_messages} total messages")


@click.command('seed-demo')
@click.option('--reset', is_flag=True, help='Reset database before seeding')
@with_appcontext
def seed_demo_command(reset):
    """Seed the database with demo data using Faker."""
    if reset:
        click.echo('Resetting database...')
        init_db()

    click.echo('Creating demo users...')
    users = create_demo_users()

    click.echo('Creating contact relationships...')
    create_contacts(users)

    click.echo('Generating message history...')
    create_messages(users)

    db_.session.commit()

    click.echo('')
    click.echo('✓ Demo data created successfully!')
    click.echo('')
    click.echo('Demo accounts (all passwords are "demo123"):')
    click.echo('  • alice  - Primary account with full message history')
    click.echo('  • bob    - Friend with lots of messages')
    click.echo('  • carol  - Work colleague')
    click.echo('  • david  - Family member')
    click.echo('  • emma   - New contact (few messages)')
    click.echo('  • frank  - One-way contact (no messages)')


def init_app(app):
    """Register the seed-demo command with the Flask app."""
    app.cli.add_command(seed_demo_command)
