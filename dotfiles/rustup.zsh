# brew install rustup

# ==> Caveats
# To initialize `rustup`, set a default toolchain:
#   rustup default stable

# If you have `rust` installed, ensure you have "$(brew --prefix rustup)/bin"
# before "$(brew --prefix)/bin" in your $PATH:
#   https://rust-lang.github.io/rustup/installation/already-installed-rust.html

# rustup is keg-only, which means it was not symlinked into /home/linuxbrew/.linuxbrew,
# because it conflicts with rust.

# If you need to have rustup first in your PATH, run:
#   echo 'export PATH="/home/linuxbrew/.linuxbrew/opt/rustup/bin:$PATH"' >> ~/.zshrc
export PATH="/home/linuxbrew/.linuxbrew/opt/rustup/bin:$PATH"