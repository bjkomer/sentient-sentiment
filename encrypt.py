def decode( key, password=None ):

  if password is None:
    f = open( 'password.txt', 'r' )
    password = f.readline().strip()
  
  key_chain = [ ord(k) for k in key ]
  pass_chain = [ ord(p) for p in password ]

  new_key_chain = []
  pos = 0
  for k in key_chain:
    new_key_chain.append( ( k - pass_chain[ pos ] + 45 ) % 256 )
    pos = k % len( pass_chain )

  new_key = "".join( chr(k) for k in new_key_chain )
  
  return new_key

def encode( key, password ):

  key_chain = [ ord(k) for k in key ]
  pass_chain = [ ord(p) for p in password ]

  new_key_chain = []
  pos = 0
  for k in key_chain:
    new_key_chain.append( ( k + pass_chain[ pos ] - 45 ) % 256 )
    pos = ( k + pass_chain[ pos ] ) % len( pass_chain )

  new_key = "".join( chr(k) for k in new_key_chain )

  return new_key
