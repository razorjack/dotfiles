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
Plug 'SirVer/ultisnips' | Plug 'honza/vim-snippets'
Plug 'tpope/vim-surround'
Plug 'tpope/vim-ragtag'
Plug 'tpope/vim-vinegar'
Plug 'vim-scripts/gitignore'
Plug 'janko-m/vim-test'

Plug 'tpope/vim-commentary'
Plug 'tpope/vim-endwise'
Plug 'tpope/vim-eunuch'
Plug 'junegunn/vim-easy-align'
Plug 'plasticboy/vim-markdown', { 'for': 'markdown' }
Plug 'vim-ruby/vim-ruby'
Plug 'tpope/vim-rails'
Plug 'tpope/vim-rake'
Plug 'mileszs/ack.vim'
Plug 'jelera/vim-javascript-syntax'
Plug 'Raimondi/delimitMate'
Plug 'marijnh/tern_for_vim', { 'for': 'coffeescript' }
Plug 'kchmck/vim-coffee-script', { 'for': 'coffeescript' }
Plug 'christoomey/vim-tmux-navigator'
Plug 'bronson/vim-trailing-whitespace'
Plug 'rust-lang/rust.vim', { 'for': 'rust' }
Plug 'elixir-lang/vim-elixir', { 'for': 'elixir' }
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'
Plug 'rakr/vim-one'
Plug 'altercation/vim-colors-solarized'

Plug 'Shougo/vimfiler.vim', { 'on': 'VimFiler' }
Plug 'majutsushi/tagbar', { 'on': 'Tagbar' }

Plug 'benekastah/neomake'

if has('nvim')
  Plug 'junegunn/fzf'
  Plug 'kassio/neoterm'
  Plug 'Shougo/deoplete.nvim', { 'do': ':UpdateRemotePlugins' }
  Plug 'bfredl/nvim-miniyank'
else
  Plug 'JazzCore/ctrlp-cmatcher'
  " Plug 'scrooloose/syntastic'
  Plug 'kien/ctrlp.vim'
  Plug 'Valloric/YouCompleteMe', { 'do': './install.py' }
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

"Credit joshdick
"Use 24-bit (true-color) mode in Vim/Neovim when outside tmux.
"If you're using tmux version 2.2 or later, you can remove the outermost $TMUX check and use tmux's 24-bit color support
"(see < http://sunaku.github.io/tmux-24bit-color.html#usage > for more information.)
"if (empty($TMUX))
"  if (has("nvim"))
"  "For Neovim 0.1.3 and 0.1.4 < https://github.com/neovim/neovim/pull/2198 >
"  let $NVIM_TUI_ENABLE_TRUE_COLOR=1
"  endif
"  "For Neovim > 0.1.5 and Vim > patch 7.4.1799 < https://github.com/vim/vim/commit/61be73bb0f965a895bfb064ea3e55476ac175162 >
"  "Based on Vim patch 7.4.1770 (`guicolors` option) < https://github.com/vim/vim/commit/8a633e3427b47286869aa4b96f2bfc1fe65b25cd >
"  " < https://github.com/neovim/neovim/wiki/Following-HEAD#20160511 >
"  if (has("termguicolors"))
"    set termguicolors
"  endif
"endif

let g:solarized_termcolors = 256
let g:solarized_visibility = "high"
let g:solarized_contrast = "high"

set background=light
colorscheme one
let g:airline_theme='one'

" Cursor type setup
let &t_SI = "\<Esc>]50;CursorShape=1\x7"    " Insert mode
let &t_EI = "\<Esc>]50;CursorShape=0\x7"    " Command mode
autocmd InsertEnter,InsertLeave * set cul!  " Highlight current line in insert mode 

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

let g:ycm_collect_identifiers_from_tags_files = 1 " use ctags

let g:UltiSnipsExpandTrigger="<c-j>"
let g:UltiSnipsJumpForwardTrigger="<c-j>"
let g:UltiSnipsJumpBackwardTrigger="<c-k>"

let g:vim_markdown_folding_disabled=1

au VimResized * :wincmd = " Resize panes when terminal resizes
au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g`\"" | endif " Split panes proportionally

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

" :highlight SignColumn ctermbg=NONE
" :highlight SpellBad ctermbg=234
" :highlight SpellCap ctermbg=234
" :highlight SpellRare ctermbg=234
" :highlight SpellLocal ctermbg=234
" :highlight CursorLine ctermbg=234

set statusline=
set statusline +=%4*\ %<%f%*            "full path
set statusline +=%3*\ %y%*                "file type
" set statusline +=%5*\ %{fugitive#statusline()}
set statusline +=%2*%m%*                "modified flag
set statusline +=%1*%=%5l%*             "current line
set statusline +=%2*/%L%*               "total lines
set statusline +=%1*%4v\ %*             "virtual column number

" hi User1 ctermfg=2 ctermbg=234
" hi User2 ctermfg=2 ctermbg=234
" hi User3 ctermfg=4 ctermbg=234
" hi User4 ctermfg=2 ctermbg=234
" hi User5 ctermfg=5 ctermbg=234

let g:ruby_path = system('echo $HOME/.rbenv/shims')


let g:vimrubocop_keymap = 0
nmap <Leader>a :RuboCop<CR>

:let $NVIM_TUI_ENABLE_CURSOR_SHAPE=1

" Start interactive EasyAlign in visual mode (e.g. vipga)
xmap ga <Plug>(EasyAlign)

" Start interactive EasyAlign for a motion/text object (e.g. gaip)
nmap ga <Plug>(EasyAlign)


autocmd! BufWritePost * Neomake
let g:neomake_javascript_enabled_makers = ['eslint']
let g:neomake_ruby_enabled_makers = ['mri', 'rubocop']
let g:neomake_javascript_eslint_exe = system('PATH=$(npm bin):$PATH && which eslint | tr -d "\n"')

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

let g:fzf_colors =
\ { 'fg':      ['fg', 'Normal'],
  \ 'bg':      ['bg', 'Normal'],
  \ 'hl':      ['fg', 'Comment'],
  \ 'fg+':     ['fg', 'CursorLine', 'CursorColumn', 'Normal'],
  \ 'bg+':     ['bg', 'CursorLine', 'CursorColumn'],
  \ 'hl+':     ['fg', 'Statement'],
  \ 'info':    ['fg', 'PreProc'],
  \ 'border':  ['fg', 'Ignore'],
  \ 'prompt':  ['fg', 'Conditional'],
  \ 'pointer': ['fg', 'Exception'],
  \ 'marker':  ['fg', 'Keyword'],
  \ 'spinner': ['fg', 'Label'],
  \ 'header':  ['fg', 'Comment'] }
