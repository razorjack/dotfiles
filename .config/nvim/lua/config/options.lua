-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here
vim.g.snacks_animate = false

-- Tools in ~/.local/bin have no extension; detect Python from the uv shebang.
-- (Not keyed ".*": LazyVim registers that key for bigfile and would replace this.)
vim.filetype.add({
  pattern = {
    [".*/%.local/bin/[^/]+"] = {
      function(_, bufnr)
        local line = vim.api.nvim_buf_get_lines(bufnr, 0, 1, false)[1] or ""
        if line:match("^#!.*uv run") then
          return "python"
        end
      end,
      { priority = math.huge },
    },
  },
})
