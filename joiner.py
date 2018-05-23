import csv
import os
import sys
import uuid
import traceback
import re
import json


class Joiner:
    def __init__(self):
        self.search = {}
        self.result = {}
        self.ids = []
        self.id_mapping = {}

    def generate_id(self):
        while True:
            uid = str(uuid.uuid4())[:6]
            if uid not in self.ids:
                self.ids.append(uid)
                return uid

    def write_ids(self):
        try:
            with open("rytir.csv", "r") as input_file:
                reader = csv.reader(input_file, delimiter=";")
                next(reader)
                print("File load done")
                print("Starting to generate ids")
                with open("rytir_with_ids.csv", "w") as output_file:
                    for row in reader:
                        uid = self.generate_id()
                        self.id_mapping["{};{}".format(row[0], row[1])] = uid
                        output_file.write("{};{}\n".format(uid, ";".join(row)))
                print("Done creating id card mapping and id generation")
                self.ids = None
                with open("cache.json", "w") as cache:
                    json.dump(self.id_mapping, cache)
        except Exception as e:
            raise KeyboardInterrupt(e)

    def load_cache(self):
        with open("cache.json", "r") as cache:
            self.id_mapping = json.load(cache)

#self.id_mapping["{};{}".format(list(filter(None, columns["nazev rytir"]))[i],list(filter(None, columns["id edice rytir"]))[i])]
#                           for i in range(len(list(filter(None,columns["nazev rytir"]))))

    def read_input(self):
        if os.path.isfile("vstup.csv"):
            try:
                with open("vstup.csv", "r", errors="ignore") as file:
                    reader = csv.reader(file, delimiter=";")
                    headers = next(reader)
                    columns = {}
                    for h in headers:
                        columns[h] = []
                    for row in reader:
                        row = list(filter(None, row))
                        for h, v in zip(headers, row):
                            columns[h].append(v)
                        try:
                            self.search[columns["id rishada"][0]] = []
                        except Exception as e:
                            print(
                                "Failed to add rishada card {}, this exception is critical and needs to be fixed to proceed".format(
                                    e))
                        else:
                            for i in range(len(columns["nazev rytir"])):
                                try:
                                    self.search[columns["id rishada"][0]].append(self.id_mapping["{};{}".format(
                                        columns["nazev rytir"][i], columns["id edice rytir"][i])])
                                except Exception as e:
                                    self.search[columns["id rishada"][0]].append("fail")
                                    print("Failed to add item to {} error: {}".format(columns["id rishada"][0], e))
                            # try:
                            #     # row = list(filter(None, row))
                            #     self.search[columns["id rishada"][0]] = [
                            #         self.id_mapping["{};{}".format(columns["nazev rytir"][i], columns["id edice rytir"][i])]
                            #         for i in range(len(columns["nazev rytir"]))]
                            # except KeyError as ke:
                            #     self.search[columns["id rishada"][0]] = []
                            #     print("Error at search pairing {}".format(ke))
                            for k in columns:
                                columns[k] = []
            except Exception as e:
                # traceback.print_exc()
                print("Error at input read {} at row {}".format(e, row))
        else:
            raise KeyboardInterrupt("Missing file vstup.csv")

    def read_r(self) -> dict:
        if os.path.isfile("rishada.csv"):
            with open("rishada.csv", "r", errors="ignore") as file:
                reader = csv.reader(file, delimiter=";")
                next(reader)
                data = {}
                for row in reader:
                    try:
                        if row[0] in self.search.keys():  # na prvnim indexu je id karty
                            # if ",," in row[-1] or "," in row[-1]:
                            #     row[-1] = re.split(",,|,", row[-1])[0]
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
        if os.path.isfile("rytir_with_ids.csv"):
            searched_cards = []
            self.max_items = 0
            for lists in self.search.values():
                if len(lists) > self.max_items:
                    self.max_items = len(lists)
                for card in lists:
                    searched_cards.append(card)
            with open("rytir_with_ids.csv", "r") as file:
                reader = csv.reader(file, delimiter=";")
                data = {}
                for row in reader:
                    try:
                        if row[0] in searched_cards:
                            # if ",," in row[-1] or "," in row[-1]:
                            #     row[-1] = re.split(",,|,", row[-1])[0]
                            data[row[0]] = [row[3], row[4],
                                            row[2]]  # prvni index je id karty, treti je cena ctvrty je sklad a druha je edice
                    except Exception as e:
                        print("Error at Rytir read {} at row {}".format(e, row))
            return data
        else:
            raise KeyboardInterrupt("Missing file rytir_with_ids.csv")

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
                            if item == "fail":
                                if len(prices) == 0 and len(stock) == 0:
                                    prices.append(0)
                                    stock.append(0)
                                data.append("FAILED;FAILED;FAILED")
                            else:
                                try:
                                    prices.append(int(rytir_data[item][0]))  # prvni index je cena
                                    stock.append(int(rytir_data[item][1]))  # druhy index je sklad
                                    data.append(";".join(rytir_data[item]))
                                except Exception as e:
                                    if len(prices) == 0 and len(stock) == 0:
                                        prices.append(0)
                                        stock.append(0)
                                    data.append("FAILED;FAILED;FAILED")
                                    print("Failed to add rytir card with id: {} to result, error: {}".format(item, e))
                        if len(data) == 0:
                            file.write("{}\n".format(";".join(rishada_data[key])))
                        else:
                            file.write(
                                "{};{};{};{};{}\n".format(";".join(rishada_data[key]), max(prices), min(prices),
                                                          sum(stock),
                                                          ";".join(data)))
                    except Exception as e:
                        file.write("{};FAILED\n".format(";".join(rishada_data[key])))
                        print("Error at data paring, reason: {} at id {}".format(e, key))
            print("Wrote {} lines to result.csv".format(len(rishada_data)))
        except Exception as e:
            #traceback.print_exc()
            print("General error at data pairing {}".format(e))

    def main(self):
        try:
            if os.path.isfile("cache.json"):
                print("Found cache, loading values from it.")
                self.load_cache()
            else:
                print("Cache not found, Id generation will start.")
                self.write_ids()
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
