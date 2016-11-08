###
# Page options, layouts, aliases and proxies
###

require 'cgi'

# Per-page layout changes:
#
# With no layout
page '/*.xml', layout: false
page '/*.json', layout: false
page '/*.txt', layout: false

# With alternative layout
# page "/path/to/file.html", layout: :otherlayout


# Proxy pages (http://middlemanapp.com/basics/dynamic-pages/)
# proxy "/this-page-has-no-template.html", "/template-file.html", locals: {
#  which_fake_page: "Rendering a fake page with a local variable" }

data.information.each do |info|
  info.sections.each do |sec|
    proxy "/notes/#{CGI::escape(sec.name.tr(":", ""))}.html", "/notes/template.html", :locals => {:info => info, :sec => sec, :subtitle => sec.name.to_s}, :subtitle => sec.name.to_s
  end
end

data.lectures.each do |lec|
  proxy "/notes/Lecture_#{CGI::escape(lec.name.tr(":", ""))}.html", "/notes/lecture_template.html", :locals => { :all => data.lectures, :lec => lec, :subtitle => lec.name.to_s}, :subtitle => lec.name.to_s
end

data.extra.each do |info|
  proxy "/extra/#{CGI::escape(info.name.tr(":", ""))}.html", "/extra/template.html", :locals => {:info => data.extra, :sec => info, :subtitle => info.name.to_s}, :subtitle => info.name.to_s
end

ignore '/extra/template.html.haml'
ignore '/notes/template.html.haml'
# General configuration

###
# Helpers
###

# Methods defined in the helpers block are available in templates
# helpers do
#   def some_helper
#     "Helping"
#   end
# end

helpers do
  def web_title()
    return "Nuclear & Particle Physics"
  end

  def nav_link(link_text, url, options = {})
    if url == current_page.path
      clss = "active"
    else
      clss = "inactive"
    end
    return "<li class='#{clss}'>" + link_to(link_text, url, options) + "</li>"
  end
end

activate :search do |search|
  search.resources = ['notes/', 'extra/']

  search.fields = {
	title: {boost: 100, store: true, required: true},
	subtitle: {boost: 90, store:true},
    content: {boost: 50},
    url: {index: false, store: true},
    author: {boost: 30}
  }
end

# Build-specific configuration
configure :build do
  # Minify CSS on build
  # activate :minify_css
  set :relative_links, true
  activate :relative_assets
  activate :minify_css
  # Minify Javascript on build
  # activate :minify_javascript
end
