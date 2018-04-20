import csv
import os
import sys


class Joiner:
    def __init__(self):
        self.search = {}
        self.result = {}

    def read_input(self):
        if os.path.isfile("vstup.csv"):
            try:
                with open("vstup.csv", "r") as file:
                    reader = csv.reader(file, delimiter=";")
                    # for row in reader:
                    #     try:
                    #         self.search[row[0]] = row[1:]  # prvni index (0) je karta rishady, zbytek rytire
                    #     except KeyError as ke:
                    #         print("Error at search pairing {}".format(ke))

                    headers = next(reader)
                    columns = {}
                    for h in headers:
                        columns[h] = []
                    for row in reader:
                        for h, v in zip(headers, row):
                            columns[h].append(v)
                        try:
                            self.search[columns["id rishada"][0]] = columns["rytir_id"]
                            for k in columns:
                                columns[k] = []
                        except KeyError as ke:
                            print("Error at search pairing {}".format(ke))

            except Exception as e:
                print("Error at input read {}".format(e))
        else:
            raise KeyboardInterrupt("Missing file ridici-soubor.csv")
#, errors="ignore"

    def read_r(self) -> dict:
        if os.path.isfile("rishada.csv"):
            with open("rishada.csv", "r", errors="ignore") as file:
                reader = csv.reader(file, delimiter=";")
                next(reader)
                data = {}
                for row in reader:
                    try:
                        if row[0] in self.search.keys():  # na prvnim indexu je id karty
                            row[-1] = row[-1].split(",,")[0]
                            data[row[0]] = [row[0], row[1], row[3], row[2], row[6], row[9], row[8], row[10]]
                            # posloupnost indexu odpovida tomuto poradi polozek
                            # id nazev EdID Edice Rarita prodejka nakupka sklad
                    except Exception as e:
                        print("Error at Rishada read {} at row {}".format(e, row))
            return data
        else:
            raise KeyboardInterrupt("Missing file rishada.csv")

    def read_b(self) -> dict:
        # id,name,set,price,stock
        print(self.search)
        if os.path.isfile("rytir2.csv"):
            searched_cards = []
            self.max_items = 0
            for lists in self.search.values():
                if len(lists) > self.max_items:
                    self.max_items = len(lists)
                for card in lists:
                    searched_cards.append(card)
            with open("rytir2.csv", "r", errors="ignore") as file:
                reader = csv.reader(file, delimiter=";")
                next(reader)
                data = {}
                for row in reader:
                    try:
                        if row[0] in searched_cards:
                            row[-1] = row[-1].split(",,")[0]
                            data[row[0]] = [row[3], row[4],
                                            row[2]]  # prvni index je id karty, treti je cena ctvrty je sklad a druha je edice
                    except Exception as e:
                        print("Error at Rytir read {} at row {}".format(e, row))
            return data
        else:
            raise KeyboardInterrupt("Missing file rytir.csv")

    def write_result(self):
        try:
            rishada_data = self.read_r()
        except Exception as e:
            print("rishada file read failed", e)
        else:
            print("First file searched")

        try:
            rytir_data = self.read_b()
        except Exception as e:
            print("rytir file read failed", e)
        else:
            print("Second file searched")

        header = ['id', 'nazev', 'EdID', 'Edice', 'Rarita', 'prodejka', 'nakupka', 'sklad', 'min cena', 'max cena',
                  'soucet skladu rytire']
        header.extend(self.max_items * ["cena rytire", "sklad rytire", "edice rytir"])

        if os.path.isfile("result.csv"):
            print("Previous result will be overwritten")
        try:
            with open("result.csv", "w") as file:
                file.write("{}\n".format(";".join(header)))
                for key, value in self.search.items():
                    prices, stock, data = [], [], []
                    try:
                        for item in value:
                            prices.append(int(rytir_data[item][0]))  # prvni index je cena
                            stock.append(int(rytir_data[item][1]))  # druhy index je sklad
                            data.append(";".join(rytir_data[item]))
                        file.write(
                            "{};{};{};{};{}\n".format(";".join(rishada_data[key]), max(prices), min(prices), sum(stock),
                                                      ";".join(data)))
                    except Exception as e:
                        print("Error at data paring, reason: {}".format(e))
        except Exception as e:
            print("Error at data pairing {}".format(e))

    def main(self):
        try:
            try:
                self.read_input()
            except Exception as e:
                print("input read failed", e)
            else:
                print("Input collected")
            try:
                self.write_result()
            except Exception as e:
                print("write output file failed", e)
            else:
                print("Result written")
        except KeyboardInterrupt as ki:
            print("{} stopping code".format(ki))
            sys.exit(0)

if __name__ == '__main__':
    joiner = Joiner()
    joiner.main()
