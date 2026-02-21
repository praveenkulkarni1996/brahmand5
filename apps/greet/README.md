# Greet gRPC Proof of Concept Server

This project is a proof of concept RPC server implemented in Rust using the `tonic` gRPC framework and `prost` for Protocol Buffers. It provides a simple `Greeter` service with a `SayHello` RPC.

## Project Structure

-   `Cargo.toml`: Defines project dependencies and build configuration.
-   `build.rs`: Custom build script to compile the `.proto` files into Rust code.
-   `proto/greet.proto`: The Protocol Buffers definition for the `Greeter` service.
-   `src/main.rs`: The main application logic, implementing the `Greeter` service and starting the gRPC server.

## Building and Running

To build and run the server:

1.  Navigate to the project directory:
    ```bash
    cd apps/greet
    ```
2.  Build the project:
    ```bash
    cargo build
    ```
3.  Run the server:
    ```bash
    cargo run
    ```
    The server will start and listen on `[::1]:50051`.

## Testing

You can test the server using `grpcurl`, a command-line tool for interacting with gRPC servers.

Assuming `grpcurl` is installed, open a new terminal and run the following command while the server is running:

```bash
grpcurl -plaintext -proto proto/greet.proto -d '{}' "[::1]:50051" greet.Greeter/SayHello
```

### Expected Output

```json
{
  "message": "hello"
}
```
