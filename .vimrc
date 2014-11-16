set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'gmarik/Vundle.vim'
Plugin 'tpope/vim-fugitive' " Git
Plugin 'rstacruz/sparkup', {'rtp': 'vim/'} " super fast HTML tags
Plugin 'Valloric/YouCompleteMe'
Plugin 'bling/vim-airline'
Plugin 'SirVer/ultisnips'
Plugin 'honza/vim-snippets'
Plugin 'tpope/vim-surround'
Plugin 'wincent/command-t'
Plugin 'scrooloose/syntastic'
Plugin 'altercation/vim-colors-solarized'
Plugin 'tpope/vim-commentary'
Plugin 'tpope/vim-endwise'
Plugin 'tpope/vim-eunuch'
Plugin 'godlygeek/tabular'
Plugin 'plasticboy/vim-markdown'
Plugin 'vim-ruby/vim-ruby'
Plugin 'tpope/vim-rails'
Plugin 'mileszs/ack.vim'
Plugin 'jelera/vim-javascript-syntax'
Plugin 'Raimondi/delimitMate'
Plugin 'marijnh/tern_for_vim'
Plugin 'kchmck/vim-coffee-script'
Plugin 'mattn/emmet-vim'


" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line

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

let g:ctrlp_custom_ignore = '\.git$\|\.hg$\|\.svn$\|public/system'

" Bubble single lines
nmap <C-Up> ddkP
nmap <C-Down> ddp
" Bubble multiple lines
vmap <C-Up> xkP`[V`]
vmap <C-Down> xp`[V`]


" Directories for swp files
set backupdir=~/.vim/backup
set directory=~/.vim/backup

colorscheme codeschool

" Cursor type setup
let &t_SI = "\<Esc>]50;CursorShape=1\x7"    " Insert mode
let &t_EI = "\<Esc>]50;CursorShape=0\x7"    " Command mode
autocmd InsertEnter,InsertLeave * set cul!  " Highlight current line in insert mode 

set ttimeoutlen=10                         " Set ESC lag to 100ms

" User system clipboard
set clipboard=unnamed

" Use comma as a leader key
let mapleader=","

" Command-T
let g:CommandTMaxFiles=20000
let g:CommandTMaxHeight=12

" Couldn't find any electroshocking API docs
" using echo instead
map <Left> :echo "ugh!"<cr>
map <Right> :echo "ugh!"<cr>
map <Up> :echo "ugh!"<cr>
map <Down> :echo "ugh!"<cr>

" easier navigation between split windows
nnoremap <c-j> <c-w>j
nnoremap <c-k> <c-w>k
nnoremap <c-h> <c-w>h
nnoremap <c-l> <c-w>l

" Return unhighlights current search
nnoremap <CR> :nohlsearch<cr>
" Insert a hash rocket with <c-l>
imap <c-l> <space>=><space>
" Can't be bothered to understand ESC vs <c-c> in insert mode
imap <c-c> <esc>

" double percentage sign in command mode is expanded
" to directory of current file - http://vimcasts.org/e/14
cnoremap %% <C-R>=expand('%:h').'/'<cr>

" Prevent Vim from clobbering the scrollback buffer. See
" http://www.shallowsky.com/linux/noaltscreen.html
set t_ti= t_te=
" keep more context when scrolling off the end of a buffer
set scrolloff=3

" I like solarized color scheme, let's setup it
" in case I have a need to switch
let g:solarized_termcolors = 256 
let g:solarized_visibility = "high" 
let g:solarized_contrast = "high" 


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


""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
" PROMOTE VARIABLE TO RSPEC LET
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
function! PromoteToLet()
  :normal! dd
  " :exec '?^\s*it\>'
  :normal! P
  :.s/\(\w\+\) = \(.*\)$/let(:\1) { \2 }/
  :normal ==
endfunction
:command! PromoteToLet :call PromoteToLet()
:map <leader>p :PromoteToLet<cr>


" big thanks to @garybernhardt, @mislav for their inspirational .vimrc

" C/C++/Objective-C

let g:clang_library_path = '/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib'
let g:syntastic_ruby_checkers = ['mri', 'ruby-lint']
let g:syntastic_c_checkers = ['gcc', 'oclint']
let g:syntastic_javascript_checkers = ['jshint']

let g:ackprg = 'ag --nogroup --nocolor --column'

set fillchars+=vert:\ 

let g:ycm_collect_identifiers_from_tags_files = 1 " use ctags

let g:UltiSnipsExpandTrigger="<c-j>"
let g:UltiSnipsJumpForwardTrigger="<c-j>"
let g:UltiSnipsJumpBackwardTrigger="<c-k>"

let g:vim_markdown_folding_disabled=1
