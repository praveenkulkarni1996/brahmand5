# Configuration about editors.
# I generally prefer vim style editors.

if (( $+commands[nvim] )); then
    export EDITOR='nvim'
    export VISUAL='nvim'
    export PAGER='less' 
else
    export EDITOR='vim'
fi
