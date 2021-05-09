Pry.config.prompt_name = defined?(Rails) ? Rails.application.class.to_s.split("::").first : File.basename(Dir.pwd)
