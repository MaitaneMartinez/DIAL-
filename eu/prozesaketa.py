import csv

def preprocesing(esaldia):
  try:
    lista = list(esaldia)
    if lista[0] == "-":
      lista.pop(0)

      if lista[-1] == ".":
        lista.pop(-1)
  except:
    print(esaldia)
  return ''.join(lista)

def main():

  f = open("data/eu.txt", "r")
  lines = f.readlines()
  f.close()

  with open('data/eu_train.tsv', 'w') as tsvfile:
      writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
      l = 0
      while l+2<len(lines):
          esaldi1 = preprocesing(lines[l].split('\n')[0])
          esaldi2 =  preprocesing(lines[l+1].split('\n')[0])
          writer.writerow([esaldi1,esaldi2])
          l += 2

if __name__ == '__main__':
    main()
