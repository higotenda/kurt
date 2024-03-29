import imaplib
import email
from email.header import decode_header
from collections import defaultdict
import logging
import getpass
from os import link
from abcs import Link, TextEnv, regex_url

logger = logging.getLogger(__name__);

class InboxReader(TextEnv):
    """
    A TextEnv to connect to an imap server and retrieve mails.
    """

    def __init__(self, imap_host: str, username: str, password: str, limit=50, mailbox='inbox', oauth2=False):
        """
        Connect to server `imap_host`, login as `username` with password, and initialize mailbox.
        Set the maximum number of emails to be fetched per query to be `limit`. If -1, fetches all mails.
        """
        self.mail = imaplib.IMAP4_SSL(imap_host);
        logger.info("Attempting to login..");
        self.limit = limit;
        try:
            if oauth2:
                self.mail.authenticate('XOAUTH2', lambda _: bytes(password, 'utf-8'));
            else:
                self.mail.login(username, password);
        except imaplib.IMAP4.error as e:
            logger.error(f"Failed to login to {imap_host} as {username}.\n\tcause: {e}");
        else:
            logger.info(f"Logged into {imap_host} as {username}.");
        self.mail.select(mailbox);

    def hist(self) -> tuple[list[str], list[Link]]:
        status, messages = self.mail.search(None, 'UNSEEN')
        if status != 'OK':
            logger.info("No unread emails found.")
            return ([], []);

        # Convert messages to a list of email IDs
        messages: list[str] = str(messages[0]).split();

        # Create a dictionary to group emails by sender
        # emails_by_sender = defaultdict(listt)

        emails = [];
        links = [];

        for mail_id in messages:
            # Fetch the email's bytes
            status, data = self.mail.fetch(mail_id, '(RFC822)')
            if status != 'OK':
                logger.info(f"Failed to fetch email with ID {mail_id}.");
                continue;

            if data is None:
                logger.info(f"Email data for ID {mail_id} is None.");
                continue;

            # Parse the email bytes to get a message object
            try:
                msg = email.message_from_bytes(data[0][1], policy=email.policy.default); # type: ignore
            except IndexError:
                logger.info(f"Failed to extract message from email data for {mail_id}");
                continue

            # Decode the email subject
            subject, encoding = decode_header(msg.get('Subject', failobj='Unspecified'))[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8')

            # Decode the email sender
            sender, encoding = decode_header(msg.get('From', 'unknown'))[0]
            if isinstance(sender, bytes):
                sender = sender.decode(encoding or 'utf-8')

            body = msg.get_body(('plain',)) # Hopefully, this works.
            if body is not None:
                body = body.get_content();
            else:
                body = "Empty.";

            links.extend(regex_url(body));
            emails.append(f"From: {sender}\nSubject: {subject}\n{body}");

            if len(emails) > self.limit:
                break

            # Group emails by sender
            # emails_by_sender[sender].append(subject)

        return (emails, links);

    def __enter__(self):
        return self

    def __exit__(self, *kwargs):
        self.close();

    def close(self):
        """
        Close the current mailbox and logout 
        """
        self.mail.close();
        self.mail.logout();