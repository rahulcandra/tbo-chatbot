import re


class NLPEngine:
    def __init__(self):
        # Database Menu
        self.menu_data = {
            "kopi": {
                "price": 15000,
                "emoji": "☕",
                "desc": "Kopi hitam klasik"
            },
            "latte": {
                "price": 20000,
                "emoji": "🥛",
                "desc": "Espresso dengan susu steamed"
            },
            "teh": {
                "price": 10000,
                "emoji": "🍵",
                "desc": "Teh melati hangat"
            },
            "espresso": {
                "price": 18000,
                "emoji": "⚡",
                "desc": "Shot kopi murni pekat"
            },
        }

        # Regex Patterns
        self.re_number = r"\b(\d+)\b"

        # Regex menu dinamis
        menu_keys = "|".join(self.menu_data.keys())
        self.re_menu = rf"\b({menu_keys})\b"

        # Pemisah kalimat
        self.re_split = r"[,.]\s*|\bdan\b|\b&\b"

        # Regex intent
        self.re_cancel_all = r"\b(batalkan semua|hapus semua|reset keranjang|kosongkan)\b"
        self.re_reduce = r"\b(batalkan|kurangi|tidak jadi|hapus|cancel)\b"

    def _parse_single_segment(self, text):
        """
        Memproses satu potongan kalimat
        Contoh:
        '2 teh'
        'latte 3'
        """

        text = text.lower().strip()

        # Cari item menu
        item_match = re.search(self.re_menu, text)

        if not item_match:
            return None

        item_key = item_match.group(1)

        # Cari jumlah
        qty_match = re.search(self.re_number, text)

        qty = int(qty_match.group(1)) if qty_match else 1

        return {
            "item": item_key,
            "qty": qty,
            "price": self.menu_data[item_key]["price"],
            "emoji": self.menu_data[item_key]["emoji"],
            "desc": self.menu_data[item_key]["desc"],
        }

    def parse_orders(self, full_text):
        """
        Memecah kalimat majemuk

        Contoh:
        'pesan teh 2, espresso 2'
        """

        full_text = full_text.lower()

        # Pisahkan kalimat
        segments = re.split(self.re_split, full_text)

        found_orders = []

        for segment in segments:
            segment = segment.strip()

            if not segment:
                continue

            order = self._parse_single_segment(segment)

            if order:
                found_orders.append(order)

        return found_orders

    def detect_intent(self, text):
        """
        Mendeteksi intent user
        """

        text = text.lower()

        if re.search(r"\b(reset|ulang|batal semua)\b", text):
            return "RESET_SYSTEM"

        if re.search(self.re_cancel_all, text):
            return "CANCEL_ALL"

        if re.search(self.re_reduce, text):
            return "REDUCE_ITEM"

        if re.search(r"\b(menu|daftar|apa saja|jual apa|list)\b", text):
            return "ASK_MENU"

        if re.search(r"\b(selesai|bayar|checkout|cukup)\b", text):
            return "CHECKOUT"

        if re.search(r"\b(ya|yes|oke|betul|siap|baik)\b", text):
            return "YES"

        if re.search(r"\b(tidak|enggak|batal|no|salah)\b", text):
            return "NO"

        return "UNKNOWN"

    def print_menu(self):
        """
        Menampilkan menu ke terminal
        """

        for name, data in self.menu_data.items():
            print(
                f"{data['emoji']} "
                f"{name.title()} - "
                f"Rp{data['price']} "
                f"({data['desc']})"
            )