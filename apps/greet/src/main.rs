use tonic::{transport::Server, Request, Response, Status};
use clap::Parser;

use greet::{greeter_server::{Greeter, GreeterServer}, GreetRequest, GreetResponse};

pub mod greet {
    tonic::include_proto!("greet"); // The string "greet" here should match the package name in your .proto file
}

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[arg(long, default_value_t = 50051)]
    port: u16,
    #[arg(long, default_value_t = String::from("0.0.0.0"))]
    ip: String,
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
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    let addr = format!("{}:{}", cli.ip, cli.port).parse()?;
    let greeter = MyGreeter::default();

    println!("GreeterServer listening on {}", addr);

    Server::builder()
        .add_service(GreeterServer::new(greeter))
        .serve(addr)
        .await?;

    Ok(())
}