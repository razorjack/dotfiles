Pry.config.prompt_name ||= defined?(Rails) ? Rails.application.class.to_s.split("::").first : File.basename(Dir.pwd)

class Object
  def local_methods(obj = self)
    (obj.methods - obj.class.superclass.instance_methods).sort
  end

  def me!
    User.find_by(email: `git config user.email`.strip)
  end
end
Pry.config.pager = false
