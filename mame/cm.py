import re

class StopNested(Exception):
    pass

class CMParser:

    def parse_tokens(self, content):
        pattern = re.compile(r'[\w.-]+|"[^"]*"|\(|\)')
        unquote = lambda x:x[1:-1] if x.startswith('"') else x
        return (unquote(m.group(0)) for m in re.finditer(pattern, content))

    def get_next_keyvalue_pair(self, tokens):
        key = next(tokens)
        if key == '(':
            raise ValueError('Invalid format')

        if key == ')':
            raise StopNested()
        
        value = next(tokens)

        if value == '(':
            pairs = []
            while True:
                try:
                    pairs.append(self.get_next_keyvalue_pair(tokens))
                except StopNested:
                    break
            return (key, pairs)

        else:
            return (key, value)


    def parse(self, content):
        """Parse a clrmamepro format dat file."""
        tokens = self.parse_tokens(content)

        entries = []
        while True:
            try:
                entries.append(self.get_next_keyvalue_pair(tokens))
            except StopIteration:
                break

        return entries

