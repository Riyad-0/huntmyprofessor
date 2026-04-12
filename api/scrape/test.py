from bs4 import BeautifulSoup

def main():
  with open("a.html") as f:
    soup = BeautifulSoup(f.read(), 'html.parser')
    el = soup.find(name="td", string="A")
    print(soup.find(name="td"))
    print(el)
    print(el.find_next_sibling())
main()