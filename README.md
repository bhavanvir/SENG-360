# SENG 360: Security Engineering
The objective of this course is to introduce students to a broad range of topics related to this discipline, including an overview of computer security, protection, disaster planning, and recovery. Risk analysis and security plans. Basics of cryptography. Public key cryptography and protocols. Security models, kernel design and systems testing. Database, network and Web security. The course discusses applications which need various combinations of confidentiality, availability, integrity and covertness properties; mechanisms to incorporate these properties in systems.

## Project Objective 
The objective is to design and implement a secure messaging application.

## Requirements
- SM must support 1:1 messaging and may support group chats (that’s optional)
- Text messages must be supported. Multi-media (such as pictures) are optional
- Message history is kept in encrypted form (at-rest encryption)
- Message history (for a particular conversation) can be deleted by a user. (This will not delete the message history on the other user's side.)
- Message transport uses end-to-end encryption with perfect forward secrecy (https://en.wikipedia.org/wiki/Forward_secrecy)
- Users are authenticated (i.e.,they should be guaranteed to talk to the right person)
- Message integrity must be assured
- Users can plausibly deny having sent a message (see https://signal.org/blog/simplifying-otr-deniability/)
- Users can sign up for an account and also delete their account
- SM must be implemented in Python

## Installation
Clone the repository.
```bash
git clone https://github.com/bhavanvir/SENG-360
```

Change your directory to the root of the project.
```bash
cd SENG-360
```

Install the dependencies.
```bash
pip install -r requirements.txt
```

Run the server.
```bash
python server.py
```

Run the client.
```bash
python client.py
```
