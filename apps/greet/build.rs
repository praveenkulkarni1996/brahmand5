fn main() -> Result<(), Box<dyn std::error::Error>> {
    tonic_build::configure()
        .compile(
            &["proto/greet.proto"],
            &["proto"], // The path to the directory where proto files are located
        )?;
    Ok(())
}
