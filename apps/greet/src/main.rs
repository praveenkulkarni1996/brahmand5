use tonic::{transport::Server, Request, Response, Status};
use clap::Parser;
use http::{StatusCode, Response as HttpResponse};
use hyper::{
    body::Bytes,
    service::service_fn,
    Request as HttpRequest, // Alias hyper's Request
    Body, // Use hyper::Body directly
};
use hyper::service::make_service_fn;
use std::convert::Infallible;
use std::net::SocketAddr;
use serde::Serialize;

use greet::{greeter_server::{Greeter, GreeterServer}, GreetRequest, GreetResponse};

pub mod greet {
    tonic::include_proto!("greet"); // The string "greet" here should match the package name in your .proto file
}

// Define the HealthStatus struct for JSON serialization
#[derive(Serialize)]
pub struct HealthStatus {
    pub status: String,
}

// Health check handler
async fn health_check_handler(_req: HttpRequest<Body>) -> Result<HttpResponse<Body>, Infallible> {
    let health_status = HealthStatus {
        status: "UP".to_string(),
    };
    let json_response = serde_json::to_string(&health_status).unwrap();

    Ok(HttpResponse::builder()
        .status(StatusCode::OK)
        .header(http::header::CONTENT_TYPE, "application/json")
        .body(Body::from(Bytes::from(json_response)))
        .unwrap())
}

// HTTP service router
async fn http_service_router(
    req: HttpRequest<Body>,
) -> Result<HttpResponse<Body>, Infallible> {
    match (req.method(), req.uri().path()) {
        (&http::Method::GET, "/health") => health_check_handler(req).await,
        _ => {
            Ok(HttpResponse::builder()
                .status(StatusCode::NOT_FOUND)
                .body(Body::from("404 Not Found"))
                .unwrap())
        }
    }
}

// Function to serve HTTP requests
async fn serve_http(http_addr: SocketAddr) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    println!("HTTP Server listening on {}", http_addr);

    let make_svc = make_service_fn(|_conn| async {
        Ok::<_, Infallible>(service_fn(http_service_router))
    });

    let server = hyper::Server::bind(&http_addr)
        .serve(make_svc);

    server.await?;

    Ok(())
}

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[arg(long, default_value_t = 50051)]
    port: u16,
    #[arg(long, default_value_t = String::from("0.0.0.0"))]
    ip: String,
    #[arg(long, default_value_t = 8080)]
    http_port: u16,
    #[arg(long, default_value_t = String::from("0.0.0.0"))]
    http_ip: String,
}

#[derive(Debug, Default)]
pub struct MyGreeter {}

#[tonic::async_trait]
impl Greeter for MyGreeter {
    async fn say_hello(
        &self,
        request: Request<GreetRequest>,
    ) -> Result<Response<GreetResponse>, Status> {
        println!("Got a request: {:?}", request);

        let reply = GreetResponse {
            message: "hello".into(),
        };

        Ok(Response::new(reply))
    }
}

#[tokio::main]
#[allow(unused_must_use)] // Allow unused Result for tokio::try_join!
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let grpc_addr = format!("{}:{}", cli.ip, cli.port).parse()?;
    let http_addr = format!("{}:{}", cli.http_ip, cli.http_port).parse()?;
    let greeter = MyGreeter::default();

    println!("GreeterServer listening on {}", grpc_addr);
    println!("HTTP Health/Metrics Server listening on {}", http_addr);

    let grpc_server_handle = tokio::spawn(async move {
        Server::builder()
            .add_service(GreeterServer::new(greeter))
            .serve(grpc_addr)
            .await
    });

    let http_server_handle = tokio::spawn(serve_http(http_addr));

    tokio::try_join!(grpc_server_handle, http_server_handle)?;

    Ok(())
}