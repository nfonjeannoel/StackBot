"""

pages = response.css("div.s-pagination a").getall()
for page in pages:
    print(page.css(a::attr(href)).get())
"""