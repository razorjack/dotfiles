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
Plug 'AndrewRadev/splitjoin.vim' " switch between single-line and multi-line statements
Plug 'gorkunov/smartpairs.vim'
Plug 'sheerun/vim-polyglot'
Plug 'tpope/vim-bundler'
Plug 'benmills/vimux'
Plug 'SirVer/ultisnips' | Plug 'honza/vim-snippets'
Plug 'tpope/vim-surround'
Plug 'tpope/vim-vinegar'
Plug 'vim-scripts/gitignore'

" Plug 'altercation/vim-colors-solarized'
Plug 'tpope/vim-commentary'
Plug 'tpope/vim-endwise'
Plug 'tpope/vim-eunuch'
Plug 'junegunn/vim-easy-align'
Plug 'plasticboy/vim-markdown'
Plug 'vim-ruby/vim-ruby'
Plug 'tpope/vim-rails'
Plug 'tpope/vim-rake'
Plug 'rking/ag.vim'
Plug 'jelera/vim-javascript-syntax'
Plug 'Raimondi/delimitMate'
Plug 'marijnh/tern_for_vim'
Plug 'kchmck/vim-coffee-script'
Plug 'nanotech/jellybeans.vim'
Plug 'christoomey/vim-tmux-navigator'
Plug 'bronson/vim-trailing-whitespace'
Plug 'rust-lang/rust.vim', { 'for': 'rust' }
Plug 'elixir-lang/vim-elixir', { 'for': 'clojure' }

if has('nvim')
  Plug 'junegunn/fzf'
  Plug 'benekastah/neomake'
  Plug 'kassio/neoterm'
  Plug 'Shougo/deoplete.nvim'
else
  Plug 'JazzCore/ctrlp-cmatcher'
  Plug 'scrooloose/syntastic'
  Plug 'kien/ctrlp.vim'
  Plug 'Valloric/YouCompleteMe'
endif

call plug#end()

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


" Bubble single lines
nmap <C-Up> ddkP
nmap <C-Down> ddp
" Bubble multiple lines
vmap <C-Up> xkP`[V`]
vmap <C-Down> xp`[V`]


" Directories for swp files
set backupdir=~/.vim/backup
set directory=~/.vim/backup

colorscheme jellybeans

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
" map <Left> :echo "ugh!"<cr>
" map <Right> :echo "ugh!"<cr>
" map <Up> :echo "ugh!"<cr>
" map <Down> :echo "ugh!"<cr>
nnoremap <c-j> <c-w>j
nnoremap <c-k> <c-w>k
nnoremap <c-h> <c-w>h
nnoremap <c-l> <c-w>l

nnoremap <left> <c-w>5<
nnoremap <down> <c-w>5-
nnoremap <up> <c-w>5+
nnoremap <right> <c-w>5>
" easier navigation between split windows
" nnoremap <c-j> <c-w>j
" nnoremap <c-k> <c-w>k
" nnoremap <c-h> <c-w>h
" nnoremap <c-l> <c-w>l

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

if has('nvim')
  " let g:neomake_javascript_enabled_makers = ['eslint']
  " let g:neomake_ruby_enabled_makers = ['mri', 'ruby-lint']
  " let g:neomake_c_enabled_makers = ['gcc']
  autocmd! BufWritePost * Neomake

  " Use deoplete.
  let g:deoplete#enable_at_startup = 1
  let g:deoplete#sources = {}
  let g:deoplete#sources._ = ['buffer', 'tag']
  let g:deoplete#tag#cache_limit_size = 10000000
else
  :highlight SyntasticErrorSign ctermbg=234
  :highlight SyntasticWarningSign ctermbg=234
  :highlight SyntasticStyleErrorSign ctermbg=234
  :highlight SyntasticStyleWarningSign ctermbg=234

  let g:syntastic_ruby_checkers = ['mri', 'ruby-lint']
  let g:syntastic_c_checkers = ['gcc']
  let g:syntastic_javascript_checkers = ['eslint']
endif

set fillchars+=vert:\ 

let g:ycm_collect_identifiers_from_tags_files = 1 " use ctags

let g:UltiSnipsExpandTrigger="<c-j>"
let g:UltiSnipsJumpForwardTrigger="<c-j>"
let g:UltiSnipsJumpBackwardTrigger="<c-k>"

let g:vim_markdown_folding_disabled=1

au VimResized * :wincmd = " Resize panes when terminal resizes
au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g`\"" | endif " Split panes proportionally

" set ttyfast
" set lazyredraw


if has('nvim')
  map <Leader>t :FZF<CR>
else
  let g:path_to_matcher = "/usr/local/bin/matcher"
  let g:ctrlp_custom_ignore = '\.git$\|\.hg$\|\.svn$\|public/system'
  map <Leader>t :CtrlP<CR>

  let g:ctrlp_match_func = {'match' : 'matcher#cmatch' }

  let g:ctrlp_user_command = ['.git/', 'cd %s && git ls-files . -co --exclude-standard']

  " let g:ctrlp_match_func = { 'match': 'GoodMatch' }

  function! GoodMatch(items, str, limit, mmode, ispath, crfile, regex)

    " Create a cache file if not yet exists
    let cachefile = ctrlp#utils#cachedir().'/matcher.cache'
    if !( filereadable(cachefile) && a:items == readfile(cachefile) )
      call writefile(a:items, cachefile)
    endif
    if !filereadable(cachefile)
      return []
    endif

    " a:mmode is currently ignored. In the future, we should probably do
    " something about that. the matcher behaves like "full-line".
    let cmd = g:path_to_matcher.' --limit '.a:limit.' --manifest '.cachefile.' '
    if !( exists('g:ctrlp_dotfiles') && g:ctrlp_dotfiles )
      let cmd = cmd.'--no-dotfiles '
    endif
    let cmd = cmd.a:str

    return split(system(cmd), "\n")

  endfunction
  let g:ctrlp_use_caching = 0
endif

:highlight SignColumn ctermbg=NONE
:highlight SpellBad ctermbg=234
:highlight SpellCap ctermbg=234
:highlight SpellRare ctermbg=234
:highlight SpellLocal ctermbg=234
:highlight CursorLine ctermbg=234

let g:vroom_use_vimux = 1

set statusline=
set statusline +=%4*\ %<%f%*            "full path
set statusline +=%3*\ %y%*                "file type
" set statusline +=%5*\ %{fugitive#statusline()}
set statusline +=%2*%m%*                "modified flag
set statusline +=%1*%=%5l%*             "current line
set statusline +=%2*/%L%*               "total lines
set statusline +=%1*%4v\ %*             "virtual column number

hi User1 ctermfg=2 ctermbg=234
hi User2 ctermfg=2 ctermbg=234
hi User3 ctermfg=4 ctermbg=234
hi User4 ctermfg=2 ctermbg=234
hi User5 ctermfg=5 ctermbg=234

let g:ruby_path = system('echo $HOME/.rbenv/shims')


let g:vimrubocop_keymap = 0
nmap <Leader>a :RuboCop<CR>

:let $NVIM_TUI_ENABLE_CURSOR_SHAPE=1

" Start interactive EasyAlign in visual mode (e.g. vipga)
xmap ga <Plug>(EasyAlign)

" Start interactive EasyAlign for a motion/text object (e.g. gaip)
nmap ga <Plug>(EasyAlign)


let g:neomake_javascript_enabled_makers = ['eslint']
let g:neomake_ruby_enabled_makers = ['mri', 'rubocop']
