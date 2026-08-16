import unittest
from backend.parser import analyze_listing, extract_phone, is_rental_listing, matches_block_b1, parse_bedrooms_and_bathrooms
from backend.database import Database

class TestRentalParser(unittest.TestCase):

    def test_rental_versus_sale(self):
        self.assertTrue(is_rental_listing("Cho thuê căn hộ Bông Sao Q8 giá rẻ"))
        self.assertTrue(is_rental_listing("Cho thue chung cu Bong Sao 2PN"))
        self.assertFalse(is_rental_listing("Bán căn hộ Bông Sao 2PN 2WC chính chủ"))
        self.assertFalse(is_rental_listing("Cần bán gấp lô B1 Bông Sao Q8 70m2"))

    def test_block_aliases(self):
        self.assertEqual(matches_block_b1("Chung cư Bông sao Block B1 tầng 5"), "Block B1")
        self.assertEqual(matches_block_b1("Cho thuê Bông sao lô B1 2pn"), "Block B1")
        self.assertEqual(matches_block_b1("Bông Sao lô B 2 phòng ngủ"), "Block B (Lô B)")

    def test_bedroom_and_bathroom_parsing(self):
        bed, bath = parse_bedrooms_and_bathrooms("Căn hộ 2PN 2WC full nội thất")
        self.assertEqual((bed, bath), (2, 2))

        bed2, bath2 = parse_bedrooms_and_bathrooms("Cho thuê 2 phòng ngủ 2 vệ sinh sạch sẻ")
        self.assertEqual((bed2, bath2), (2, 2))

        bed3, bath3 = parse_bedrooms_and_bathrooms("Căn hộ 1PN 1WC tầng cao")
        self.assertEqual((bed3, bath3), (1, 1))

    def test_phone_extraction(self):
        self.assertEqual(extract_phone("Liên hệ 0909123456 xem nhà"), "0909123456")
        self.assertEqual(extract_phone("Zalo: 038 999 8888"), "0389998888")

    def test_full_analysis_valid_match(self):
        res = analyze_listing(
            title="Cho thuê chung cư Bông Sao Block B1 2PN 2WC lầu trung giá 7.5 triệu",
            description="Liên hệ 0987654321 xem nhà ngay. Căn góc view đẹp."
        )
        self.assertTrue(res["is_rental"])
        self.assertTrue(res["is_bong_sao"])
        self.assertIsNotNone(res["block_matched"])
        self.assertEqual(res["bedrooms"], 2)
        self.assertEqual(res["bathrooms"], 2)
        self.assertEqual(res["phone"], "0987654321")
        self.assertTrue(res["is_match"])

    def test_full_analysis_invalid_match_sale(self):
        res = analyze_listing(
            title="Bán gấp căn hộ Bông Sao lô B1 2PN 2WC giá 2.1 tỷ",
            description="Cần tiền bán gấp lô B1 2 phòng ngủ 2 toilet"
        )
        self.assertFalse(res["is_rental"])
        self.assertFalse(res["is_match"])

    def test_database_hash_deduplication(self):
        h1 = Database.generate_hash("Chotot", "https://nhatot.com/123.htm", "0909123456")
        h2 = Database.generate_hash("Chotot", "https://nhatot.com/123.htm?utm_source=test", "0909123456")
        self.assertEqual(h1, h2, "Canonical URL hash should ignore query parameters")

    def test_freshness_and_relative_time_parsing(self):
        from backend.parser import parse_relative_time, is_fresh_listing
        from datetime import datetime, timedelta

        t1 = parse_relative_time("Đăng 15 phút trước")
        self.assertIsNotNone(t1)
        self.assertTrue(is_fresh_listing(t1, max_hours=48))

        t2 = parse_relative_time("Hôm qua 10:30")
        self.assertIsNotNone(t2)
        self.assertTrue(is_fresh_listing(t2, max_hours=48))

        # Stale listing (5 days ago)
        t_old = datetime.now() - timedelta(days=5)
        self.assertFalse(is_fresh_listing(t_old, max_hours=48))

if __name__ == "__main__":
    unittest.main()
