IRB.conf[:BACK_TRACE_LIMIT] = 100

class Object

  def local_methods(obj = self)
    (obj.methods - obj.class.superclass.instance_methods).sort
  end

  def me!
    User.find_by(email: `git config user.email`.strip)
  end
end

begin
  require 'ap' # gem "awesome_print"
rescue LoadError
end

IRB.conf[:SAVE_HISTORY] = 200000
IRB.conf[:HISTORY_FILE] = "#{ENV['HOME']}/.irb-history"

app_name = defined?(Rails) ? Rails.application.class.to_s.split("::").first : File.basename(Dir.pwd)

IRB.conf[:PROMPT][:MY_PROMPT] = {
  :PROMPT_I => "#{app_name} (%m):%03n:%i> ",
  :PROMPT_S => "#{app_name} (%m):%03n:%i%l ",
  :PROMPT_C => "#{app_name} (%m):%03n:%i* ",
  :RETURN => "%s\n"
}

IRB.conf[:PROMPT_MODE] = :MY_PROMPT
IRB.conf[:EVAL_HISTORY] = 5
