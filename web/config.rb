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
  proxy "/lectures/Lecture_#{CGI::escape(lec.name.tr(":", ""))}.html", "/lectures/lecture_template.html", :locals => { :all => data.lectures, :lec => lec, :subtitle => lec.name.to_s}, :subtitle => lec.name.to_s
end

data.interactive.each do |info|
  proxy "/interactive/#{info.url}.html", "/interactive/template.html", :locals => {:info => data.interactive, :sec => info, :subtitle => info.name.to_s}, :subtitle => info.name.to_s
end

# Note that the below is a huge hack. Using a function like get_tags() below
# seems to return an empty tags array every time. I blame Middleman.
tags = []

data.faq.each do |faq_item|
  faq_item.tags.each do |this_tag|
    if !(tags.include? this_tag)
      tags.push(this_tag)
      proxy "/faq/#{CGI::escape(this_tag.to_s)}.html", "/faq/template.html", :locals => {:tagname=> this_tag}, :subtitle => this_tag.to_s
    end
  end
end


ignore '/interactive/template.html.haml'
ignore '/notes/template.html.haml'
ignore '/lectures/lecture_template.html.haml'
ignore '/faq/template.html.haml'
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

  def get_tags()
    # Gets the tags for the FAQ sections
    tags = []

    data.faq.each do |faq_item|
      faq_item.tags.each do |this_tag|
        if !(tags.include? this_tag)
          tags.push(this_tag)
        end
      end
    end

    return tags.sort()
  end
end

activate :search do |search|
  search.resources = ['notes/', 'extra/','faq/']

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
