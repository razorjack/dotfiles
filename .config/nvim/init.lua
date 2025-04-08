local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.loop.fs_stat(lazypath) then
  vim.fn.system({
    "git",
    "clone",
    "--filter=blob:none",
    "https://github.com/folke/lazy.nvim.git",
    "--branch=stable", -- latest stable release
    lazypath,
  })
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  -- UI
  "kyazdani42/nvim-web-devicons",
  "nvim-lua/plenary.nvim",
  "catppuccin/nvim",

  -- Snippets
  "hrsh7th/vim-vsnip",
  "hrsh7th/vim-vsnip-integ",

  -- Themes
  "navarasu/onedark.nvim",
  "projekt0n/github-nvim-theme",
  "marko-cerovac/material.nvim",

  -- Git
  "lewis6991/gitsigns.nvim",
  "tpope/vim-fugitive",
  "f-person/git-blame.nvim",

  -- Syntax and Language
  {
    "nvim-treesitter/nvim-treesitter",
    build = ":TSUpdate"
  },
  "RRethy/nvim-treesitter-textsubjects",
  "RRethy/nvim-treesitter-endwise",
  "b3nj5m1n/kommentary",

  -- Telescope and FZF
  "nvim-telescope/telescope.nvim",
  {
    "nvim-telescope/telescope-fzf-native.nvim",
    build = "cmake -S. -Bbuild -DCMAKE_BUILD_TYPE=Release && cmake --build build --config Release && cmake --install build --prefix build" 
  },

  -- LSP and Completion
  "neovim/nvim-lspconfig",
  "nvim-lua/lsp-status.nvim",
  { 
    "williamboman/mason.nvim",
    build = ":MasonUpdate"
  },
  "williamboman/mason-lspconfig.nvim",
  "jose-elias-alvarez/null-ls.nvim",
  "hrsh7th/cmp-nvim-lsp",
  "hrsh7th/cmp-buffer",
  "hrsh7th/nvim-cmp",
  "hrsh7th/cmp-vsnip",
  "glepnir/lspsaga.nvim",
  "weilbith/nvim-code-action-menu",
  "ray-x/lsp_signature.nvim",
  "lukas-reineke/indent-blankline.nvim",

  -- UI Components
  "hoob3rt/lualine.nvim",
  "kyazdani42/nvim-tree.lua",


  -- Markdown and Text
  { "plasticboy/vim-markdown", ft = "markdown" },
  "junegunn/goyo.vim",
  "junegunn/limelight.vim",
  "jxnblk/vim-mdx-js",

  -- Ruby
  "vim-ruby/vim-ruby",
  "tpope/vim-rails",

  -- Misc
  "tpope/vim-surround",
  "tpope/vim-eunuch",
  "mileszs/ack.vim",
  "christoomey/vim-tmux-navigator",
  "bronson/vim-trailing-whitespace",
  "rust-lang/rust.vim",
  "slim-template/vim-slim",

  -- Deprecated but keeping for now (to be migrated later)
  {
    "Shougo/deoplete.nvim",
    build = ":UpdateRemotePlugins"
  },
  "deoplete-plugins/deoplete-tag",

  -- Navigation
  "SmiteshP/nvim-navic",
  "utilyre/barbecue.nvim",
})

vim.cmd('syntax enable')

vim.opt.encoding = 'utf-8'
vim.opt.showcmd = true

vim.opt.wrap = false
vim.opt.tabstop = 2
vim.opt.shiftwidth = 2
vim.opt.expandtab = true
vim.opt.backspace = 'indent,eol,start'

vim.opt.hlsearch = true
vim.opt.incsearch = true
vim.opt.ignorecase = true
vim.opt.smartcase = true

vim.opt.number = true
vim.opt.wildignore:append({
  '*.o', '*.obj', '.git', '*.rbc', '*.class', '.svn', 'vendor/gems/*',
  'tmp/**', 'public/system/**', 'public/uploads/**', 'public/assets/**',
  'site_media/m/**', 'build/**'
})
vim.opt.laststatus = 2

vim.opt.scrolloff = 3

vim.opt.ttimeoutlen = 10

vim.opt.clipboard = 'unnamed'
vim.opt.showmode = false
vim.opt.lazyredraw = true
vim.opt.hidden = true

vim.opt.errorbells = false

vim.opt.swapfile = false
vim.opt.backup = false
vim.opt.writebackup = false

vim.opt.fillchars:append('vert:|')

vim.g.ackprg = 'ag --vimgrep --smart-case --hidden'
vim.cmd('cnoreabbrev ag Ack')

-- Bubble single lines
vim.keymap.set('n', '<C-Up>', 'ddkP', { silent = true })
vim.keymap.set('n', '<C-Down>', 'ddp', { silent = true })

-- Bubble multiple lines
vim.keymap.set('v', '<C-Up>', 'xkP`[V`]', { silent = true })
vim.keymap.set('v', '<C-Down>', 'xp`[V`]', { silent = true })

vim.opt.background = 'dark'

vim.opt.guicursor = 'n-v-c:block,i-ci-ve:ver25,r-cr:hor20,o:hor50'
vim.api.nvim_create_autocmd({'InsertEnter', 'InsertLeave'}, {
  callback = function() vim.opt.cursorline = not vim.opt.cursorline:get() end
})

vim.g.mapleader = ','

-- Window navigation
vim.keymap.set('n', '<c-j>', '<c-w>j', { silent = true })
vim.keymap.set('n', '<c-k>', '<c-w>k', { silent = true })
vim.keymap.set('n', '<c-h>', '<c-w>h', { silent = true })
vim.keymap.set('n', '<c-l>', '<c-w>l', { silent = true })

-- Window resizing
vim.keymap.set('n', '<left>', '<c-w>5<', { silent = true })
vim.keymap.set('n', '<down>', '<c-w>5-', { silent = true })
vim.keymap.set('n', '<up>', '<c-w>5+', { silent = true })
vim.keymap.set('n', '<right>', '<c-w>5>', { silent = true })

-- Return unhighlights current search
vim.keymap.set('n', '<CR>', ':nohlsearch<cr>', { silent = true })

-- Map <c-c> to <esc> in insert mode
vim.keymap.set('i', '<c-c>', '<esc>', { silent = true })

vim.keymap.set('c', '%%', function()
  return vim.fn.expand('%:h') .. '/'
end, { expr = true })

local text_group = vim.api.nvim_create_augroup('vimrcEx', { clear = true })
vim.api.nvim_create_autocmd('FileType', {
  group = text_group,
  pattern = 'text',
  callback = function()
    vim.opt_local.textwidth = 100
  end
})

vim.api.nvim_create_autocmd('FileType', {
  pattern = 'markdown',
  callback = function()
    vim.opt_local.wrap = true
    vim.opt_local.linebreak = true
    vim.opt_local.list = false
  end
})

local function goyo_enter()
  if vim.fn.executable('tmux') == 1 and string.len(vim.env.TMUX or '') > 0 then
    vim.fn.system('tmux set status off')
    vim.fn.system('tmux list-panes -F \'\\#F\' | grep -q Z || tmux resize-pane -Z')
  end
  vim.opt.showmode = false
  vim.opt.showcmd = false
  vim.opt.wrap = true
  vim.opt.linebreak = true
  vim.opt.list = false
end

local function goyo_leave()
  if vim.fn.executable('tmux') == 1 and string.len(vim.env.TMUX or '') > 0 then
    vim.fn.system('tmux set status on')
    vim.fn.system('tmux list-panes -F \'\\#F\' | grep -q Z && tmux resize-pane -Z')
  end
  vim.opt.showmode = true
  vim.opt.showcmd = true
end

vim.api.nvim_create_autocmd('User', {
  pattern = 'GoyoEnter',
  callback = function()
    goyo_enter()
  end
})

vim.api.nvim_create_autocmd('User', {
  pattern = 'GoyoLeave',
  callback = function()
    goyo_leave()
  end
})

vim.g.limelight_conceal_ctermfg = 240
vim.g.goyo_width = 100
vim.g.vim_markdown_folding_disabled = 1

-- Resize panes when terminal resizes
vim.api.nvim_create_autocmd('VimResized', {
  callback = function()
    vim.cmd('wincmd =')
  end
})

-- Return to last edit position when opening files
vim.api.nvim_create_autocmd('BufReadPost', {
  callback = function()
    local line = vim.fn.line("'\"")
    if line > 1 and line <= vim.fn.line('$') then
      vim.cmd('normal! g`"')
    end
  end
})

vim.g.ruby_path = vim.fn.system('echo $HOME/.rbenv/shims')
vim.g.NVIM_TUI_ENABLE_CURSOR_SHAPE = 1

-- Copy full line with Y
vim.keymap.set('n', 'Y', 'yy', { silent = true })

vim.g.rustfmt_autosave = 1

require("mason").setup()

require('telescope').setup {
  extensions = {
    fzf = {
      fuzzy = true,
      override_generic_sorter = true,
      override_file_sorter = true,
      case_mode = "smart_case",
    }
  }
}
require('telescope').load_extension('fzf')

vim.keymap.set('n', '<leader>t', '<cmd>Telescope find_files<cr>', { silent = true })
vim.keymap.set('n', '<leader>f', '<cmd>Telescope live_grep<cr>', { silent = true })
vim.keymap.set('n', '<leader>p', '<cmd>NvimTreeToggle<cr>', { silent = true })
vim.keymap.set('n', '-', '<cmd>NvimTreeToggle<cr>', { silent = true })

vim.opt.termguicolors = true

require'nvim-tree'.setup {
  diagnostics = {
    enable = true,
  },
  filters = {
    exclude = { "config/application.yml", "config/database.yml" },
  }
}

require('lualine').setup {
  options = {
    theme = 'onedark'
  }
}
require'nvim-treesitter.configs'.setup {
  ensure_installed = "all",
  highlight = {
    enable = true,
    additional_vim_regex_highlighting = false,
  },
  indent = {
    enable = true,
  },
  endwise = {
    enable = true,
  },
}
require('gitsigns').setup()
require('material').setup({
  disable = {
    background = true,
  },
})

require'nvim-treesitter.configs'.setup {
  textsubjects = {
    enable = true,
    keymaps = {
      ['\\'] = 'textsubjects-smart',
      [';'] = 'textsubjects-container-outer',
    }
  },
}

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

require'nvim-web-devicons'.setup {
  override = {
  };
  default = true;
}

require "lsp_signature".setup()

local nvim_lsp = require('lspconfig')
local protocol = require'vim.lsp.protocol'

local on_attach = function(client, bufnr)
  local function buf_set_keymap(...) vim.api.nvim_buf_set_keymap(bufnr, ...) end
  local function buf_set_option(...) vim.api.nvim_buf_set_option(bufnr, ...) end

  buf_set_option('omnifunc', 'v:lua.vim.lsp.omnifunc')

  local opts = { noremap=true, silent=true }

  buf_set_keymap('n', 'gD', '<Cmd>lua vim.lsp.buf.declaration()<CR>', opts)
  buf_set_keymap('n', 'gd', '<Cmd>lua vim.lsp.buf.definition()<CR>', opts)
  buf_set_keymap('n', 'gi', '<cmd>lua vim.lsp.buf.implementation()<CR>', opts)
  buf_set_keymap('n', 'gf', '<cmd>lua vim.lsp.buf.implementation()<CR>', opts)
  buf_set_keymap('n', '<space>wa', '<cmd>lua vim.lsp.buf.add_workspace_folder()<CR>', opts)
  buf_set_keymap('n', '<space>wr', '<cmd>lua vim.lsp.buf.remove_workspace_folder()<CR>', opts)
  buf_set_keymap('n', '<space>wl', '<cmd>lua print(vim.inspect(vim.lsp.buf.list_workspace_folders()))<CR>', opts)
  buf_set_keymap('n', '<space>D', '<cmd>lua vim.lsp.buf.type_definition()<CR>', opts)
  buf_set_keymap('n', '<space>rn', '<cmd>lua vim.lsp.buf.rename()<CR>', opts)
  buf_set_keymap('n', '<space>ca', '<cmd>lua vim.lsp.buf.code_action()<CR>', opts)
  buf_set_keymap('n', '<space>e', '<cmd>lua vim.lsp.diagnostic.show_line_diagnostics()<CR>', opts)
  buf_set_keymap('n', '<S-C-j>', '<cmd>lua vim.lsp.diagnostic.goto_next()<CR>', opts)
  buf_set_keymap('n', '<space>q', '<cmd>lua vim.lsp.diagnostic.set_loclist()<CR>', opts)
  buf_set_keymap("n", "<space>f", "<cmd>lua vim.lsp.buf.formatting()<CR>", opts)
end

require('lspconfig')['ts_ls'].setup {
  on_attach = on_attach,
  capabilities = require('cmp_nvim_lsp').default_capabilities(vim.lsp.protocol.make_client_capabilities())
}

require'lspconfig'.solargraph.setup{
  on_attach = on_attach,
  init_options = {
    formatting = true
  },
  settings = {
    solargraph = {
      diagnostics = false
    }
  }
}

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

require("barbecue").setup();

require('onedark').setup {
    style = 'warmer',
    transparent = true,
}
require('onedark').load()

vim.opt.completeopt = 'menu,menuone,noselect'
vim.g.material_style = 'darker'
vim.g.gitblame_enabled = 0

vim.keymap.set('n', '<M-CR>', '<cmd>lua vim.lsp.buf.code_action()<CR>', { silent = true, buffer = true })
vim.keymap.set('n', '<F2>', '<cmd>lua require("lspsaga.rename").rename()<CR>', { silent = true })
vim.opt.updatetime = 1000
