use std::time::Duration;
use tokio::process::{Command, Child}; // Import Child
use std::net::TcpListener; // Import TcpListener

// Re-include the generated protobuf module for the client part of the test
pub mod greet {
    tonic::include_proto!("greet"); // "greet" is the package name from .proto
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn test_say_hello() -> Result<(), Box<dyn std::error::Error>> {
    // Find an available port
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let port = listener.local_addr()?.port();
    drop(listener); // Release the port so the server can bind to it

    let server_address = format!("http://[::1]:{}", port);

    // 1. Spawn server process
    let server_process = Command::new(env!("CARGO_BIN_EXE_greet"))
        .arg("--port") // Pass the port argument
        .arg(port.to_string()) // Convert port to string
        .stdout(std::process::Stdio::null()) // Suppress server output
        .stderr(std::process::Stdio::null()) // Suppress server errors in test output
        .spawn()?;

    // Ensure the server process is killed when the test finishes, even if it panics
    let _drop_guard = DropGuard {
        child: server_process,
    };

    // 2. Use tokio::time::timeout for cleaner polling
    let mut client = tokio::time::timeout(Duration::from_secs(10), async {
        loop {
            if let Ok(c) = greet::greeter_client::GreeterClient::connect(server_address.clone()).await {
                return c;
            }
            tokio::time::sleep(Duration::from_millis(50)).await;
        }
    }).await.map_err(|_| "Server handshake timed out after 10s")?;


    // 3. Execute RPC and Assert Result
    let request = tonic::Request::new(greet::GreetRequest {});
    let response = client.say_hello(request).await?.into_inner();
    assert_eq!(response.message, "hello");

    Ok(())
}

// Helper struct to ensure the child process is killed on test completion/panic
struct DropGuard {
    child: Child, // Use tokio::process::Child
}

impl Drop for DropGuard {
    fn drop(&mut self) {
        // Use a blocking kill here as drop is not async
        std::mem::drop(self.child.kill());
    }
}
