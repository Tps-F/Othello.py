import argparse
import tkinter as tk
from tkthread import Thread


class Othello(tk.Tk):
    def __init__(self, cpu, sec):
        super(Othello, self).__init__()
        self.cpu = cpu
        self.title("オセロ")
        self.geometry("{}x{}+{}+{}".format(350, 450, 450, 100))
        self.color = ["", "white", "black"]
        # {tag: position}
        self.tag2pos = {}
        # 座標からtagの変換
        self.z2tag = {}
        # 符号
        self.numstr = '12345679'
        self.alpstr = "abcdefgh"
        # Set up some variables
        self.set_variables()
        # Set up game board
        self.set_board()
        # Set up some buttons
        self.set_button()
        self.thread = Thread(sec)
        self.thread.set_parent(self)
        if self.cpu:
            self.thread.keylock = 1
            self.thread()

    def set_variables(self):
        self.sentinel = [2] * 10 + [[0, 2][i in [0, 9]] for i in range(10)] * 8 + [2] * 10
        self.board2info = [0] * 64
        self.playerTurn = 1
        self.gorilla = 0
        self.is_end = 0

    def set_board(self):
        # オセロ盤
        self.board = tk.Canvas(self, bg="lime green", width=350, height=350)
        self.board.place(x=0, y=0)
        # オセロ盤を作成
        for i, y in zip(self.numstr, range(15, 336, 40)):
            for j, x in zip(self.alpstr, range(15, 336, 40)):
                pos = x, y, x+40, y+40
                tag = i + j
                self.tag2pos[tag] = pos
                self.board.create_rectangle(*pos, fill="lime green", tags=tag)
                self.z2tag[self.z_coordinate(tag)] = tag
                self.board.tag_bind(tag, "<ButtonPress-1>", self.pressed)
        # 初期設定
        for z, turn in [(44, 1), (45, -1), (54, -1), (55, 1)]:
            tag = self.z2tag[z]
            self.sentinel[z] = turn
            self.board.create_oval(*self.tag2pos[tag], fill=self.color[turn], tags=tag)
        self.sent2board()
        #self.get_board_info()
        self.get_candidates()
        self.switch_board()

    def set_button(self):
        self.reset = tk.Button(self, text="reset", relief="groove", command=self.clear)
        self.reset.place(x=170, y=380)
        self.quit_program = tk.Button(self, text="quit", relief="groove", command=self.close)
        self.quit_program.place(x=280, y=380)

    def get_sentinel_info(self):
        # self.sentinelを表示
        print("{:-^31s}".format("self.sentinel"))
        print(*[str(" {:2d} " * 8).format(*self.sentinel[i:i+8]) \
            for i in range(11, 89, 10)], sep="\n")
        print('-'*31)

    def get_board_info(self):
        # self.board2infoを表示
        print("{:-^31s}".format("self.board2info"))
        print(*[str(" {:2d} " * 8).format(*self.board2info[i:i+8]) \
            for i in range(0, 64, 8)], sep="\n")
        print('-'*31)

    def sent2board(self):
        # self.sentinelをself.board2infoに変換
        self.board2info = [self.sentinel[j] for i in range(11, 89, 10) for j in range(i, i+8)]

    def z_coordinate(self, tag):
        x = self.alpstr.index(tag[1])+1
        y = self.numstr.index(tag[0])+1
        return y*10 + x

    def get_candidates(self):
        # 置ける場所を探す
        self.candidates = {}
        for y in self.numstr:
            for x in self.alpstr:
                tag = y + x
                if self.sentinel[self.z_coordinate(tag)] != 0:
                    continue
                self.search(tag)

        if len(self.candidates) == 0:
            # 候補手がない
            print("パスしまーす（{}）".format(['', '白', '黒'][self.playerTurn]))
            # ターンを変えて候補手を探す。
            self.gorilla += 1
            if self.gorilla == 2:
                self.is_end = 1
                self.print_result()
            else:
                self.playerTurn = -self.playerTurn
                self.get_candidates()
                self.switch_board()
        else:
            # 候補手がある。
            self.print_turn()
            self.gorilla = 0

    def pressed(self, event):
        if self.thread.keylock:
            return
        item_id = self.board.find_closest(event.x, event.y)
        tag = self.board.gettags(item_id[0])[0]
        if tag not in self.candidates:
            return
        self.update_board(tag)

    def update_board(self, tag):
        """ 色々更新する。
            1. 盤面の更新。
            2. 盤情報の更新。
            3. ターンの更新。
        """
        ### 1. 盤面の更新。###
        self.switch_board(0)
        # 反転処理
        for z in self.candidates[tag]:
            ctag = self.z2tag[z]
            self.board.create_oval(*self.tag2pos[ctag], fill=self.color[self.playerTurn])
            self.sentinel[z] = self.playerTurn
        # 新しく石を置く
        self.board.create_oval(*self.tag2pos[tag], fill=self.color[self.playerTurn])

        ### 2. 盤情報の更新。###
        self.sentinel[self.z_coordinate(tag)] = self.playerTurn
        self.sent2board()
        # 盤情報を出力
        self.get_board_info()
        ### 3. ターンの更新。###
        self.playerTurn = -self.playerTurn
        # 候補手を探す。
        self.get_candidates()
        self.switch_board()
        if self.playerTurn == -1 or self.cpu:
            self.thread()

    def search(self, tag):
        z = self.z_coordinate(tag)
        for num in [-10, 10, 1, -1, -11, 11, -9, 9]:
            self.flag = False
            self.tmp = []
            result = self._search(z+num, num)
            if result == -1:
                continue
            if tag in self.candidates:
                self.candidates[tag] += self.tmp
            else:
                self.candidates[tag] = self.tmp

    def _search(self, z, num):
        v = self.sentinel[z]
        if v in [0, 2]:
            return -1
        if v == self.playerTurn:
            return z if self.flag else -1
        self.flag = True
        self.tmp.append(z)
        return self._search(z+num, num)

    def switch_board(self, color=1):
        # 候補手のところの色を変える
        for tag in self.candidates.keys():
            self.board.itemconfig(tag, fill=["lime green", "lawn green"][color])

    def print_turn(self):
        print("{}のターンです。".format(['', '白', '黒'][self.playerTurn]))

    def print_result(self):
        # 結果の表示
        total_black = sum([0, 1][x == -1] for x in self.board2info)
        total_white = sum([0, 1][x == 1] for x in self.board2info)
        print("{:-^29s}".format("結果"))
        if total_black == total_white:
            print(f"{'引き分け':^29s}")
        else:
            result = ["黒", "白"][total_black < total_white]
            print(f"{result+'の勝ち':^29s}")
        print("黒：{}".format(total_black))
        print("白：{}".format(total_white))

    def clear(self):
        # 初期化
        print("\n"*30)
        self.board.delete("all")
        self.set_variables()
        self.set_board()
        self.thread.keylock = 0
        if self.cpu:
            self.thread.keylock = 1
            self.thread()

    def close(self):
        # 終了処理
        self.thread.is_running = 0
        self.quit()

    def run(self):
        self.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--cpu',
        type=bool,
        default=False,
        help="TrueならCPU同士、Falseなら人vsCPUの対戦"
    )

    parser.add_argument(
        '-s',
        '--sec',
        type=float,
        default=0.1,
        help="AIが思考状態に入るまでの時間を指定"
    )
    args = parser.parse_args()
    app = Othello(args.cpu, args.sec)
    app.run()