use tonic::{transport::Server, Request, Response, Status};

use greet::{greeter_server::{Greeter, GreeterServer}, GreetRequest, GreetResponse};

pub mod greet {
    tonic::include_proto!("greet"); // The string "greet" here should match the package name in your .proto file
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
    let addr = "[::1]:50051".parse()?;
    let greeter = MyGreeter::default();

    println!("GreeterServer listening on {}", addr);

    Server::builder()
        .add_service(GreeterServer::new(greeter))
        .serve(addr)
        .await?;

    Ok(())
}