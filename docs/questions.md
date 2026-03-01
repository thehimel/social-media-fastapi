# Questions and Answers

## I access FastAPI at `http://127.0.0.1:8000/`, but the log shows ports like `62304`, `62354`, etc. Why?

The port in the log is the **client port**, not the server port. When your browser (or any client) connects to the server on port 8000, the OS assigns an ephemeral port to the client side of the connection. The log format `127.0.0.1:62304` means "request from client at 127.0.0.1 using client port 62304." The server listens on 8000; the client uses a random high port for its end of the connection.
