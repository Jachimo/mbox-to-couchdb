# Notes on mbox-to-couchdb

Moved here from the README file, because there's really no reason for most people to read this just to use the program.


## Edge Cases

One of the nice things about the `sample.mbox` dataset, is that it contains some *interesting* edge cases, including a message without a Subject header, messages with non-ASCII names in the From fields, a few non-ASCII Subject lines, and a mix of plain text, quoted-printable, and multipart MIME messages.

The non-ASCII headers are (properly) encoded according to RFC 1342 (or possibly RFC 2047 which supercedes it), also known as "MIME Encoded-Word".  
See <https://en.wikipedia.org/wiki/MIME#Encoded-Word>.

A discussion of various approaches to parsing such headers with Python 3 can be found on StackOverflow:
<https://stackoverflow.com/questions/7331351/python-email-header-decoding-utf-8>

Since CouchDB can handle Unicode natively, the MIME Encoded-Word headers are converted to their proper glyph representations via the `email.header` module before being stuffed into the database as a document.
(Refer to <https://docs.python.org/3.3/library/email.header.html>)
This also has the pleasant side-effect of cleaning up other weirdnesses that can appear in email headers, such as newlines.

Another intriguing case is on l.413 in `sample.mbox`, which is a message that lacks a Subject header completely.
This is uncommon in my experience (generally a MUA or MTA will insert the Subject header but leave it blank), but it certainly can occur, particularly in old archives that have been corrupted or otherwise mangled.


## Attachment MIME Type

When adding attachments to a document in CouchDB, it is necessary to specify the MIME type.
Since what's being stored alongside the message headers is the original email message taken from the mbox file, in its entirety, I use the somewhat-obscure MIME type "message/rfc822", as suggested in RFC 1341: <https://www.w3.org/Protocols/rfc1341/7_3_Message.html>

You might ask, "why not use the Content-Type header value?", which is a reasonable option.
However, in my view, that's not technically correct (the best kind of correct!), because the Content-Type header specifies the MIME type of the message *payload*.
What we are specifying, when we supply CouchDB with a MIME type alongside an uploaded attachment, is the type *of the attachment itself*.
Since we're attaching an entire message, including all headers, which may or may not contain MIME sub-parts, "message/rfc822" seems like a better choice.

That all said, I don't think this really has much effect on anything at all at present; the file extension (".eml") is probably the greater determinant of how the attachment will behave when downloaded, so this is really just academic.
