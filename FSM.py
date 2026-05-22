from enum import Enum, auto
from engine import NLPEngine


class State(Enum):
    IDLE = auto()
    ORDERING = auto()
    CONFIRMATION = auto()
    PAYMENT = auto()


class CoffeeFSM:
    def __init__(self):
        self.state = State.IDLE
        self.nlp = NLPEngine()
        self.cart = []
        self.response = ""

    def get_response(self):
        return self.response

    def calculate_total(self):
        return sum(item['price'] * item['qty'] for item in self.cart)

    def get_menu_text(self):
        teks_menu = "* Daftar Menu Logic Coffee:*\n\n"

        for key, data in self.nlp.menu_data.items():
            teks_menu += (
                f"- {data['emoji']} "
                f"*{key.capitalize()}* "
                f"(Rp {data['price']:,}): "
                f"{data['desc']}\n"
            )

        teks_menu += (
            "\nSilakan ketik pesanan Anda "
            "(contoh: 'Pesan 2 teh, 1 espresso')."
        )

        return teks_menu

    def reduce_cart(self, item_to_reduce, qty_to_remove):
        found = False
        message = ""

        for item in self.cart:
            if item['item'] == item_to_reduce:
                item['qty'] -= qty_to_remove
                found = True

                if item['qty'] <= 0:
                    self.cart.remove(item)
                    message = (
                        f"❌ *{item_to_reduce}* "
                        f"telah dihapus dari keranjang."
                    )
                else:
                    message = (
                        f"📝 *{item_to_reduce}* "
                        f"dikurangi {qty_to_remove}. "
                        f"Sisa: {item['qty']}."
                    )
                break

        if not found:
            message = (
                f"Gagal: *{item_to_reduce}* "
                f"tidak ditemukan di keranjang Anda."
            )

        return message

    def step(self, user_input=""):
        user_input = user_input.strip()

        # Jika input kosong saat pertama kali
        if user_input == "" and self.state == State.IDLE:
            self.state = State.ORDERING
            self.response = (
                "Halo! Mau pesan apa hari ini?\n"
                "Ketik 'menu' untuk melihat pilihan."
            )
            return

        intent = self.nlp.detect_intent(user_input)

        # RESET SYSTEM
        if intent == "RESET_SYSTEM":
            self.__init__()
            self.response = (
                "Sistem berhasil di-reset.\n"
                "Halo! Mau pesan apa?"
            )
            return

        # =========================
        # STATE: ORDERING
        # =========================
        if self.state == State.ORDERING:

            # LIHAT MENU
            if intent == "ASK_MENU":
                self.response = self.get_menu_text()

            # HAPUS SEMUA
            elif intent == "CANCEL_ALL":
                self.cart = []
                self.response = (
                    "🗑️ Keranjang berhasil dikosongkan.\n"
                    "Mau pesan yang lain?"
                )

            # HAPUS ITEM
            elif intent == "REDUCE_ITEM":
                items_to_remove = self.nlp.parse_orders(user_input)

                if items_to_remove:
                    results = []

                    for itm in items_to_remove:
                        result = self.reduce_cart(
                            itm['item'],
                            itm['qty']
                        )
                        results.append(result)

                    self.response = "\n".join(results)

                else:
                    self.response = (
                        "Item apa yang ingin dibatalkan?\n"
                        "Contoh: 'batalkan 1 kopi'"
                    )

            # CHECKOUT
            elif intent == "CHECKOUT":

                if not self.cart:
                    self.response = (
                        "🛒 Keranjang masih kosong."
                    )

                else:
                    self.state = State.CONFIRMATION

                    self.response = (
                        f"Total belanja Anda: "
                        f"*Rp {self.calculate_total():,}*\n"
                        f"Lanjut bayar? (Ya/Tidak)"
                    )

            # TAMBAH PESANAN
            else:
                new_orders = self.nlp.parse_orders(user_input)

                if new_orders:

                    for order in new_orders:

                        existing = next(
                            (
                                i for i in self.cart
                                if i['item'] == order['item']
                            ),
                            None
                        )

                        if existing:
                            existing['qty'] += order['qty']

                        else:
                            menu_info = self.nlp.menu_data[
                                order['item']
                            ]

                            order.update({
                                "price": menu_info['price'],
                                "emoji": menu_info['emoji']
                            })

                            self.cart.append(order)

                    self.response = (
                        "✅ Pesanan berhasil ditambahkan.\n"
                        "Ada lagi? "
                        "(ketik 'bayar' untuk checkout)"
                    )

                else:
                    self.response = (
                        "❌ Maaf, saya tidak mengerti.\n"
                        "Contoh:\n"
                        "- pesan 2 kopi\n"
                        "- hapus 1 teh\n"
                        "- menu"
                    )

        # =========================
        # STATE: CONFIRMATION
        # =========================
        elif self.state == State.CONFIRMATION:

            if intent == "YES":
                self.state = State.PAYMENT
                self.step()

            elif intent == "NO":
                self.state = State.ORDERING
                self.response = (
                    "Oke, silakan tambah pesanan lagi."
                )

            else:
                self.response = (
                    "Jawab dengan 'Ya' atau 'Tidak'."
                )

        # =========================
        # STATE: PAYMENT
        # =========================
        elif self.state == State.PAYMENT:

            total = self.calculate_total()

            self.response = (
                f"🎉 Terima kasih!\n"
                f"Pembayaran sebesar "
                f"*Rp {total:,}* berhasil.\n"
                f"Pesanan sedang diproses."
            )

            # reset keranjang
            self.cart = []

            # kembali ke awal
            self.state = State.IDLE