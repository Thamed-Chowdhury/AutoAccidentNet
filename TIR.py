import re

def pagination_url_collector(div_string, n):
    """
    Extracts pagination URLs from a given HTML string.

    Args:
        div_string: The HTML string containing pagination links.
        n: The number of page URLs to retrieve.

    Returns:
        A list of URLs for the first n pages, or None if no pattern is found.
    """

    #Find all divs with pagination
    divs = re.findall(r'<div class="d-flex justify-content-center">(.*?)</div>', div_string, re.DOTALL)

    urls = []
    for div in divs:
        # Find all <a> tags with href attributes within the div
        matches = re.findall(r'<a\s+class="page-link"\s+href="([^"]*)"', div)
        
        #If there are any matches from this div, use them and break out of the loop.
        if matches:
            base_url = matches[0].split("?page=")[0]
            for i in range(1, min(n + 1, len(matches)+1)):  # Iterate up to n or the number of found links
                url = f"{base_url}?page={i}"
                urls.append(url)
            break # Only use the first set of pagination links found


    if not urls:
        return None  # No pattern found
    return urls


# Example usage:
div_string = """
<div class="d-flex justify-content-center">
 <nav>
  <ul class="pagination">
   <li aria-disabled="true" aria-label="« Previous" class="page-item disabled">
    <span aria-hidden="true" class="page-link">
     ‹
    </span>
   </li>
   <li aria-current="page" class="page-item active">
    <span class="page-link">
     1
    </span>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=2">
     2
    </a>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=3">
     3
    </a>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=4">
     4
    </a>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=5">
     5
    </a>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=6">
     6
    </a>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=7">
     7
    </a>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=8">
     8
    </a>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=9">
     9
    </a>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=10">
     10
    </a>
   </li>
   <li aria-disabled="true" class="page-item disabled">
    <span class="page-link">
     ...
    </span>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=1206">
     1206
    </a>
   </li>
   <li class="page-item">
    <a class="page-link" href="https://www.bd-pratidin.com/country?page=1207">
     1207
    </a>
   </li>
   <li class="page-item">
    <a aria-label="Next »" class="page-link" href="https://www.bd-pratidin.com/country?page=2" rel="next">
     ›
    </a>
   </li>
  </ul>
 </nav>
</div>
<div class="d-flex justify-content-center">
  <nav>
   <ul class="pagination">
    <li aria-disabled="true" aria-label="« Previous" class="page-item disabled">
     <span aria-hidden="true" class="page-link">
      ‹
     </span>
    </li>
    <li aria-current="page" class="page-item active">
     <span class="page-link">
      1
     </span>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=2">
      2
     </a>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=3">
      3
     </a>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=4">
      4
     </a>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=5">
      5
     </a>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=6">
      6
     </a>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=7">
      7
     </a>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=8">
      8
     </a>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=9">
      9
     </a>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=10">
      10
     </a>
    </li>
    <li aria-disabled="true" class="page-item disabled">
     <span class="page-link">
      ...
     </span>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=1206">
      1206
     </a>
    </li>
    <li class="page-item">
     <a class="page-link" href="https://www.bd-pratidin.com/country?page=1207">
      1207
     </a>
    </li>
    <li class="page-item">
     <a aria-label="Next »" class="page-link" href="https://www.bd-pratidin.com/country?page=2" rel="next">
      ›
     </a>
    </li>
   </ul>
  </nav>
 </div>
"""

n = 5
urls = pagination_url_collector(div_string, n)
print(urls)
