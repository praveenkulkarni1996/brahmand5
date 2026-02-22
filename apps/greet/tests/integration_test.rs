use std::time::Duration;
use tokio::process::{Command, Child};
use std::net::TcpListener;

use serde_json::json;

// Re-include the generated protobuf module for the client part of the test
pub mod greet {
    tonic::include_proto!("greet"); // "greet" is the package name from .proto
}

// Helper function to find a free port
fn find_free_port() -> Result<u16, Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let port = listener.local_addr()?.port();
    Ok(port)
}

// Helper to spawn the server and wait for it to be ready
async fn spawn_test_server() -> Result<(DropGuard, u16), Box<dyn std::error::Error>> {
    let grpc_port = find_free_port()?;
    let http_port = find_free_port()?;

    let server_process = Command::new(env!("CARGO_BIN_EXE_greet"))
        .arg("--ip")
        .arg("127.0.0.1")
        .arg("--port")
        .arg(grpc_port.to_string())
        .arg("--http-ip")
        .arg("127.0.0.1")
        .arg("--http-port")
        .arg(http_port.to_string())
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .spawn()?;

    let drop_guard = DropGuard {
        child: server_process,
    };

    // Wait for the HTTP server to be ready by polling the /health endpoint
    let client = reqwest::Client::new();
    let health_url = format!("http://127.0.0.1:{}/health", http_port);

    tokio::time::timeout(Duration::from_secs(10), async {
        loop {
            match client.get(&health_url).send().await {
                Ok(response) if response.status().is_success() => break,
                _ => tokio::time::sleep(Duration::from_millis(100)).await,
            }
        }
    }).await.map_err(|_| "HTTP server did not become ready in time")?;

    Ok((drop_guard, http_port))
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn test_health_endpoint_ok() -> Result<(), Box<dyn std::error::Error>> {
    let (_drop_guard, http_port) = spawn_test_server().await?;
    let client = reqwest::Client::new();
    let health_url = format!("http://127.0.0.1:{}/health", http_port);

    let response = client.get(&health_url).send().await?;
    assert_eq!(response.status(), reqwest::StatusCode::OK);

    let json_body: serde_json::Value = response.json().await?;
    assert_eq!(json_body, json!({"status": "UP"}));

    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn test_health_endpoint_not_found() -> Result<(), Box<dyn std::error::Error>> {
    let (_drop_guard, http_port) = spawn_test_server().await?;
    let client = reqwest::Client::new();
    let not_found_url = format!("http://127.0.0.1:{}/nonexistent_path", http_port);

    let response = client.get(&not_found_url).send().await?;
    assert_eq!(response.status(), reqwest::StatusCode::NOT_FOUND);

    let text_body = response.text().await?;
    assert_eq!(text_body, "404 Not Found");

    Ok(())
}

#[tokio::test(flavor = "multi_thread", worker_threads = 2)]
async fn test_say_hello() -> Result<(), Box<dyn std::error::Error>> {
    // Find an available port
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let port = listener.local_addr()?.port();
    drop(listener); // Release the port so the server can bind to it

    let server_address = format!("http://127.0.0.1:{}", port);

    // 1. Spawn server process
    let server_process = Command::new(env!("CARGO_BIN_EXE_greet"))
        .arg("--ip") // Pass the ip argument
        .arg("127.0.0.1") // Set ip to 127.0.0.1
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
        tokio::task::block_in_place(move || {
            tokio::runtime::Handle::current().block_on(async {
                if let Err(e) = self.child.kill().await {
                    eprintln!("Failed to kill child process: {}", e);
                }
                if let Err(e) = self.child.wait().await {
                    eprintln!("Failed to wait for child process: {}", e);
                }
            })
        });
    }
}
