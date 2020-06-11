set nocompatible              " be iMproved, required
filetype off                  " required

" vim-plug autoconfig if not already installed
if empty(glob('~/.config/nvim/autoload/plug.vim'))
  silent !curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall | nested source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')

Plug 'tpope/vim-fugitive' " Git
Plug 'gorkunov/smartpairs.vim'
Plug 'sheerun/vim-polyglot'
Plug 'tpope/vim-surround'
Plug 'tpope/vim-vinegar'
Plug 'vim-scripts/gitignore'
Plug 'tpope/vim-commentary'
Plug 'tpope/vim-endwise'
Plug 'tpope/vim-eunuch'
Plug 'plasticboy/vim-markdown', { 'for': 'markdown' }
Plug 'vim-ruby/vim-ruby'
Plug 'tpope/vim-rails'
Plug 'mileszs/ack.vim'
Plug 'christoomey/vim-tmux-navigator'
Plug 'bronson/vim-trailing-whitespace'
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'rakr/vim-one'
Plug 'junegunn/fzf'
Plug 'rust-lang/rust.vim'
Plug 'dense-analysis/ale'

if has('nvim')
  Plug 'Shougo/deoplete.nvim', { 'do': ':UpdateRemotePlugins' }
else
  Plug 'Shougo/deoplete.nvim'
  Plug 'roxma/nvim-yarp' " deoplete dependency
  Plug 'roxma/vim-hug-neovim-rpc' " deoplete dependency
endif

Plug 'deoplete-plugins/deoplete-tag'

if has('nvim')
  Plug 'bfredl/nvim-miniyank'
endif

call plug#end()

let g:python_host_prog = '/usr/local/bin/python'
let g:python2_host_prog = '/usr/local/bin/python2'
let g:python3_host_prog = '/usr/local/bin/python3'

syntax enable

set encoding=utf-8
set showcmd                     " display incomplete commands

"" Whitespace
set nowrap                      " don't wrap lines
set tabstop=2 shiftwidth=2      " a tab is two spaces (or set this to 4)
set expandtab                   " use spaces, not tabs (optional)
set backspace=indent,eol,start  " backspace through everything in insert mode

"" Searching
set hlsearch                    " highlight matches
set incsearch                   " incremental searching
set ignorecase                  " searches are case insensitive...
set smartcase                   " ... unless they contain at least one capital letter

"" Misc
set number                      " show line numbers
set wildignore+=*.o,*.obj,.git,*.rbc,*.class,.svn,vendor/gems/*,tmp/**,public/system/**,public/uploads/**,public/assets/**,site_media/m/**,build/**
set ls=2                        " always display filename

" Prevent Vim from clobbering the scrollback buffer. See
" http://www.shallowsky.com/linux/noaltscreen.html
set t_ti= t_te=
set scrolloff=3                 " keep more context when scrolling off the end of a buffer

set ttimeoutlen=10              " Set ESC lag to 100ms

set clipboard=unnamed           " User system clipboard
set noshowmode                  " Don't show -- INSERT --
set lazyredraw                  " Buffer screen updates
set hidden                      " Disable No write since last change messages

set noerrorbells                " STFU

" Don't create backups
set noswapfile
set nobackup
set nowb

set fillchars+=vert:\

let g:ackprg = 'ag --vimgrep --smart-case'
cnoreabbrev ag Ack

" Bubble single lines
nmap <C-Up> ddkP
nmap <C-Down> ddp
" Bubble multiple lines
vmap <C-Up> xkP`[V`]
vmap <C-Down> xp`[V`]

let g:solarized_termcolors = 256
let g:solarized_visibility = "high"
let g:solarized_contrast = "high"

set background=dark
colorscheme codeschool
let g:airline_theme='serene'

" Cursor type setup
let &t_SI = "\<Esc>]50;CursorShape=1\x7"    " Insert mode
let &t_EI = "\<Esc>]50;CursorShape=0\x7"    " Command mode
autocmd InsertEnter,InsertLeave * set cul!  " Highlight current line in insert mode

" Use comma as a leader key
let mapleader=","

nnoremap <c-j> <c-w>j
nnoremap <c-k> <c-w>k
nnoremap <c-h> <c-w>h
nnoremap <c-l> <c-w>l

nnoremap <left> <c-w>5<
nnoremap <down> <c-w>5-
nnoremap <up> <c-w>5+
nnoremap <right> <c-w>5>

" Return unhighlights current search
nnoremap <CR> :nohlsearch<cr>
" Insert a hash rocket with <c-l>
imap <c-l> <space>=><space>
" Can't be bothered to understand ESC vs <c-c> in insert mode
imap <c-c> <esc>

" double percentage sign in command mode is expanded
" to directory of current file - http://vimcasts.org/e/14
cnoremap %% <C-R>=expand('%:h').'/'<cr>

augroup vimrcEx
  " Clear all autocmds in the group
  autocmd!
  " Vim is an awesome notepad!
  autocmd FileType text setlocal textwidth=78
  " Jump to last cursor position unless it's invalid or in an event handler
  autocmd BufReadPost *
    \ if line("'\"") > 0 && line("'\"") <= line("$") |
    \   exe "normal g`\"" |
    \ endif
augroup END

let g:deoplete#enable_at_startup = 1
let g:deoplete#tag#cache_limit_size = 10000000

let g:UltiSnipsExpandTrigger="<c-j>"
let g:UltiSnipsJumpForwardTrigger="<c-j>"
let g:UltiSnipsJumpBackwardTrigger="<c-k>"

let g:vim_markdown_folding_disabled=1


let g:ale_lint_on_text_changed = 0

au VimResized * :wincmd = " Resize panes when terminal resizes
au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g`\"" | endif " Split panes proportionally

map <Leader>t :FZF<CR>

set statusline=
set statusline +=%4*\ %<%f%*            "full path
set statusline +=%3*\ %y%*                "file type
set statusline +=%2*%m%*                "modified flag
set statusline +=%1*%=%5l%*             "current line
set statusline +=%2*/%L%*               "total lines
set statusline +=%1*%4v\ %*             "virtual column number

let g:ruby_path = system('echo $HOME/.rbenv/shims')

:let $NVIM_TUI_ENABLE_CURSOR_SHAPE=1

" Start interactive EasyAlign in visual mode (e.g. vipga)
xmap ga <Plug>(EasyAlign)

" Start interactive EasyAlign for a motion/text object (e.g. gaip)
nmap ga <Plug>(EasyAlign)

" Neoterm
nnoremap <silent> <leader><esc> :call neoterm#close()<cr>
nnoremap <silent> <esc><esc> :call neoterm#close()<cr>
let g:neoterm_size = 15

" vim-test
nmap <silent> <leader>r :TestNearest<CR>
nmap <silent> <leader>R :TestFile<CR>
let test#strategy = "neoterm"

if has('nvim')
  map p <Plug>(miniyank-autoput)
  map P <Plug>(miniyank-autoPut)
endif
let g:airline#extensions#disable_rtp_load = 1

let g:rustfmt_autosave = 1
