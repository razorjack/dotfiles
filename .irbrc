begin
  # load wirble
  require 'rubygems'
  require 'wirble'

  # start wirble (with color)
  Wirble.init
  Wirble.colorize
rescue LoadError => err
end

class Object

  def local_methods(obj = self)
    (obj.methods - obj.class.superclass.instance_methods).sort
  end
  
  def ri(method = nil)
    unless method && method =~ /^[A-Z]/ # if class isn't specified
      klass = self.kind_of?(Class) ? name : self.class.name
      method = [klass, method].compact.join('#')
    end
    puts `ri '#{method}'`
  end
end



begin
  require 'ap' # gem "awesome_print"
rescue LoadError
end
begin
  require 'hirb' # sudo gem install cldwalker-hirb --source http://gems.github.com
  Hirb.enable
rescue LoadError
end
