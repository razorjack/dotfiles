set runtimepath^=~/.vim runtimepath+=~/.vim/after
let &packpath = &runtimepath

set nocompatible              " be iMproved, required
filetype off                  " required

" vim-plug autoconfig if not already installed
if empty(glob('~/.config/nvim/autoload/plug.vim'))
  silent !curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs
    \ https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
  autocmd VimEnter * PlugInstall | nested source $MYVIMRC
endif

call plug#begin('~/.vim/plugged')

Plug 'kyazdani42/nvim-web-devicons'
Plug 'nvim-lua/plenary.nvim'

Plug 'hrsh7th/vim-vsnip'
Plug 'hrsh7th/vim-vsnip-integ'

Plug 'lewis6991/gitsigns.nvim'
Plug 'nvim-treesitter/nvim-treesitter', {'do': ':TSUpdate'}
Plug 'nvim-telescope/telescope.nvim'
Plug 'projekt0n/github-nvim-theme'
Plug 'marko-cerovac/material.nvim'
Plug 'b3nj5m1n/kommentary'
Plug 'RRethy/nvim-treesitter-textsubjects'

Plug 'neovim/nvim-lspconfig'
Plug 'nvim-lua/lsp-status.nvim'
Plug 'williamboman/nvim-lsp-installer'
Plug 'hrsh7th/cmp-nvim-lsp'
Plug 'hrsh7th/cmp-buffer'
Plug 'hrsh7th/nvim-cmp'
Plug 'hrsh7th/cmp-vsnip'
Plug 'f-person/git-blame.nvim'
Plug 'glepnir/lspsaga.nvim'
Plug 'weilbith/nvim-code-action-menu'
Plug 'ray-x/lsp_signature.nvim'

Plug 'hoob3rt/lualine.nvim'
Plug 'kyazdani42/nvim-tree.lua'
Plug 'olimorris/onedark.nvim'

Plug 'tpope/vim-fugitive' " Git
Plug 'tpope/vim-surround'
Plug 'tpope/vim-vinegar'
Plug 'tpope/vim-endwise'
Plug 'tpope/vim-eunuch'
Plug 'plasticboy/vim-markdown', { 'for': 'markdown' }
Plug 'vim-ruby/vim-ruby'
Plug 'tpope/vim-rails'
Plug 'mileszs/ack.vim'
Plug 'christoomey/vim-tmux-navigator'
Plug 'bronson/vim-trailing-whitespace'
Plug 'rust-lang/rust.vim'
Plug 'junegunn/goyo.vim'
Plug 'junegunn/limelight.vim'
Plug 'jxnblk/vim-mdx-js'

Plug 'Shougo/deoplete.nvim', { 'do': ':UpdateRemotePlugins' }
Plug 'deoplete-plugins/deoplete-tag'
Plug 'bfredl/nvim-miniyank'


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

set fillchars+=vert:\|

let g:ackprg = 'ag --vimgrep --smart-case --hidden'
cnoreabbrev ag Ack

" Bubble single lines
nmap <C-Up> ddkP
nmap <C-Down> ddp
" Bubble multiple lines
vmap <C-Up> xkP`[V`]
vmap <C-Down> xp`[V`]

set background=dark

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
  autocmd FileType text setlocal textwidth=100
augroup END

autocmd FileType markdown :set wrap linebreak nolist
function! s:goyo_enter()
  if executable('tmux') && strlen($TMUX)
    silent !tmux set status off
    silent !tmux list-panes -F '\#F' | grep -q Z || tmux resize-pane -Z
  endif
  set noshowmode
  set noshowcmd
  set wrap linebreak nolist
  " Limelight
endfunction

function! s:goyo_leave()
  if executable('tmux') && strlen($TMUX)
    silent !tmux set status on
    silent !tmux list-panes -F '\#F' | grep -q Z && tmux resize-pane -Z
  endif
  set showmode
  set showcmd
  " Limelight!
endfunction

autocmd! User GoyoEnter nested call <SID>goyo_enter()
autocmd! User GoyoLeave nested call <SID>goyo_leave()
let g:limelight_conceal_ctermfg = 240

let g:goyo_width = 100

let g:vim_markdown_folding_disabled=1

au VimResized * :wincmd = " Resize panes when terminal resizes
au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g`\"" | endif " Split panes proportionally

let g:ruby_path = system('echo $HOME/.rbenv/shims')

:let $NVIM_TUI_ENABLE_CURSOR_SHAPE=1

map p <Plug>(miniyank-autoput)
map P <Plug>(miniyank-autoPut)

let g:rustfmt_autosave = 1

nnoremap <leader>t <cmd>Telescope find_files<cr>
nnoremap <leader>f <cmd>Telescope live_grep<cr>
nnoremap <leader>p <cmd>NvimTreeToggle<cr>

let g:nvim_tree_ignore = [ '.git', 'node_modules', '.cache' ]
let g:nvim_tree_gitignore = 1
let g:nvim_tree_git_hl = 1
let g:nvim_tree_highlight_opened_files = 1

set termguicolors

lua << EOF
require('lualine').setup()
require'nvim-treesitter.configs'.setup {
  ensure_installed = "maintained",
  highlight = {
    enable = true,
    additional_vim_regex_highlighting = false,
  },
  indent = {
    enable = true,
  },
}
require('nvim-tree').setup()
require('gitsigns').setup()
require('material').setup({
	contrast = true,
	popup_menu = "dark",

	contrast_windows = {
		"terminal",
	},

	text_contrast = {
		darker = true
	},

	disable = {
		background = false,
	},
})

local saga = require 'lspsaga'
saga.init_lsp_saga {
}
require'nvim-treesitter.configs'.setup {
  textsubjects = {
  enable = true,
  keymaps = {
    ['\\'] = 'textsubjects-smart',
    [';'] = 'textsubjects-container-outer',
    }
  },
}

-- Setup nvim-cmp.
local cmp = require'cmp'

cmp.setup({
  snippet = {
    expand = function(args)
      vim.fn["vsnip#anonymous"](args.body)
    end,
  },
  mapping = {
    ['<C-d>'] = cmp.mapping.scroll_docs(-4),
    ['<C-f>'] = cmp.mapping.scroll_docs(4),
    ['<C-Space>'] = cmp.mapping.complete(),
    ['<C-e>'] = cmp.mapping.close(),
    ['<CR>'] = cmp.mapping.confirm({ select = true }),
  },
  sources = {
    { name = 'nvim_lsp' },
    { name = 'vsnip' },
    { name = 'buffer' },
  }
})

-- Setup lspconfig.
require('lspconfig')['tsserver'].setup {
  capabilities = require('cmp_nvim_lsp').update_capabilities(vim.lsp.protocol.make_client_capabilities())
}

require'lspconfig'.solargraph.setup{
  init_options = {
    formatting = true
  },
  settings = {
    solargraph = {
      diagnostics = false
    }
  }
}

require'nvim-web-devicons'.setup {
  override = {
  };
  default = true;
}

require "lsp_signature".setup()

require('vim.lsp.protocol').CompletionItemKind = {
    '', -- Text
    '', -- Method
    '', -- Function
    '', -- Constructor
    '', -- Field
    '', -- Variable
    '', -- Class
    'ﰮ', -- Interface
    '', -- Module
    '', -- Property
    '', -- Unit
    '', -- Value
    '了', -- Enum
    '', -- Keyword
    '﬌', -- Snippet
    '', -- Color
    '', -- File
    '', -- Reference
    '', -- Folder
    '', -- EnumMember
    '', -- Constant
    '', -- Struct
    '', -- Event
    'ﬦ', -- Operator
    '', -- TypeParameter
}
EOF

set completeopt=menu,menuone,noselect
let g:material_style = 'darker'
colorscheme material
" nnoremap <buffer> <M-CR> :lua vim.lsp.buf.code_action()<CR>
nnoremap <buffer> <M-CR> :CodeAction<CR>
let g:gitblame_enabled = 0

" nnoremap <silent><M-CR> :lua require('lspsaga.codeaction').code_action()<CR>
" vnoremap <silent><M-CR> :<C-U>lua require('lspsaga.codeaction').range_code_action()<CR>
set updatetime=1000