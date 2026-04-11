# batdongsan.com.vn URL Guide

## Base URL Structure

```
https://batdongsan.com.vn/{action}-{property_type}-{location}
```

## Action (Mua/Thuê)

| Mục đích | Path prefix |
|----------|-------------|
| Mua | `ban-` |
| Thuê | `cho-thue-` |

## Property Types

| Loại BĐS | Path segment |
|-----------|-------------|
| Chung cư / Căn hộ | `can-ho-chung-cu` |
| Nhà riêng | `nha-rieng` |
| Nhà biệt thự, liền kề | `biet-thu-lien-ke` |
| Nhà mặt phố | `nha-mat-pho` |
| Shophouse, nhà phố thương mại | `shophouse-nha-pho-thuong-mai` |
| Đất nền dự án | `dat-nen-du-an` |
| Đất | `dat` |
| Trang trại, khu nghỉ dưỡng | `trang-trai-khu-nghi-duong` |
| Condotel | `condotel` |
| Kho, nhà xưởng | `kho-nha-xuong` |

## Location Codes — TPHCM

### Base
```
https://batdongsan.com.vn/ban-can-ho-chung-cu-tp-hcm
```

### Quận/Huyện

| Quận | Path |
|------|------|
| Quận 1 | `quan-1` |
| Quận 3 | `quan-3` |
| Quận 4 | `quan-4` |
| Quận 5 | `quan-5` |
| Quận 6 | `quan-6` |
| Quận 7 | `quan-7` |
| Quận 8 | `quan-8` |
| Quận 10 | `quan-10` |
| Quận 11 | `quan-11` |
| Quận 12 | `quan-12` |
| Gò Vấp | `go-vap` |
| Bình Thạnh | `binh-thanh` |
| Tân Bình | `tan-binh` |
| Tân Phú | `tan-phu` |
| Phú Nhuận | `phu-nhuan` |
| Bình Tân | `binh-tan` |
| TP. Thủ Đức | `thu-duc` |
| Củ Chi | `cu-chi` |
| Hóc Môn | `hoc-mon` |
| Bình Chánh | `binh-chanh` |
| Nhà Bè | `nha-be` |
| Cần Giờ | `can-gio` |

## Price Filter (Query Parameters)

Giá được filter bằng query params:

```
?gia_tu={min}&gia_den={max}
```

Đơn vị: triệu đồng

| Khoảng giá | Params |
|------------|--------|
| Dưới 1 tỷ | `gia_den=1000` |
| 1-2 tỷ | `gia_tu=1000&gia_den=2000` |
| 2-3 tỷ | `gia_tu=2000&gia_den=3000` |
| 3-5 tỷ | `gia_tu=3000&gia_den=5000` |
| 5-7 tỷ | `gia_tu=5000&gia_den=7000` |
| 7-10 tỷ | `gia_tu=7000&gia_den=10000` |
| Trên 10 tỷ | `gia_tu=10000` |

## Area Filter

```
?dt_tu={min}&dt_den={max}
```

Đơn vị: m2

## Complete URL Examples

```
# Mua chung cư Quận 8, 3-5 tỷ
https://batdongsan.com.vn/ban-can-ho-chung-cu-quan-8?gia_tu=3000&gia_den=5000

# Mua nhà phố Gò Vấp, 5-7 tỷ
https://batdongsan.com.vn/ban-nha-rieng-go-vap?gia_tu=5000&gia_den=7000

# Thuê chung cư Quận 7, diện tích 50-80m2
https://batdongsan.com.vn/cho-thue-can-ho-chung-cu-quan-7?dt_tu=50&dt_den=80

# Mua đất nền Bình Chánh
https://batdongsan.com.vn/ban-dat-nen-du-an-binh-chanh

# Mua chung cư toàn TPHCM, 3-5 tỷ
https://batdongsan.com.vn/ban-can-ho-chung-cu-tp-hcm?gia_tu=3000&gia_den=5000

# Pagination - trang 2
https://batdongsan.com.vn/ban-can-ho-chung-cu-quan-8/p2?gia_tu=3000&gia_den=5000
```

## Data Extraction Selectors

Khi dùng Chrome browser tools để đọc trang kết quả:

- **Listing container**: Mỗi listing là 1 card/div trong danh sách
- **Title**: Thường là tag `<a>` hoặc `<h3>` trong card
- **Price**: Element chứa giá (tỷ, triệu, triệu/m2)
- **Area**: Element chứa diện tích (m2)
- **Location**: Element chứa địa chỉ (phường, quận)
- **Link**: `href` attribute của title link

Sử dụng `read_page` hoặc `get_page_text` để extract, sau đó parse bằng JavaScript nếu cần.

## Notes

- batdongsan.com.vn thay đổi layout/URL structure theo thời gian — nếu URL pattern không hoạt động, navigate trực tiếp tới trang chủ và dùng bộ lọc trên UI
- Website có anti-bot measures — luôn dùng Chrome browser tools, KHÔNG dùng curl/wget/requests
- Một số listing có thể là tin VIP/quảng cáo — ưu tiên tin thường và dự án thực tế
