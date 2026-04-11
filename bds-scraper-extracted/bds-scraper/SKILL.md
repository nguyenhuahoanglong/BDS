---
name: bds-scraper
description: "Real estate listing research tool for Vietnamese property market (batdongsan.com.vn). Searches, extracts, and visualizes property listings with Excel datasource and interactive Leaflet.js map with district boundary polygons. Use this skill whenever the user asks about real estate in Vietnam, property listings, apartment/house hunting, 'tìm nhà', 'tìm chung cư', 'bất động sản', 'mua nhà', 'thuê nhà', 'listing BĐS', or wants to compare properties on a map. Also trigger for 'batdongsan', 'BDS', 'dự án chung cư', 'đất nền', 'nhà phố', 'biệt thự', price range queries like '3-5 tỷ', district-specific searches like 'Quận 8', 'Quận 2', 'Thủ Đức'. Even casual questions like 'có dự án nào tốt ở Q8 không', 'nhà quận mấy rẻ', or 'so sánh giá chung cư' should trigger this skill."
---

# BDS Scraper — Vietnam Real Estate Listing Tool

Skill tìm kiếm, trích xuất và trực quan hóa thông tin bất động sản từ batdongsan.com.vn. Tạo file Excel làm datasource và bản đồ HTML tương tác với Leaflet.js.

## Workflow Overview

```
User yêu cầu → Thu thập tiêu chí → Search BĐS trên Chrome → Extract listings
    → Lấy tọa độ Google Maps → Tạo Excel → Tạo HTML Map → Verify & Deliver
```

## Bước 0: Thu thập tiêu chí từ user

Trước khi bắt đầu, cần xác nhận các thông tin sau. Nếu user đã cung cấp trong câu hỏi, không cần hỏi lại:

| Tiêu chí | Ví dụ | Mặc định |
|-----------|-------|----------|
| Loại BĐS | Chung cư, Nhà phố, Đất nền, Biệt thự | Chung cư |
| Khu vực | Quận/Huyện cụ thể trong TPHCM | Không có |
| Khoảng giá | 3-5 tỷ, dưới 2 tỷ, trên 10 tỷ | Không giới hạn |
| Diện tích | 50-80m2, trên 100m2 | Không giới hạn |
| Phòng ngủ | 2PN, 3PN | Không giới hạn |
| Mục đích | Mua, Thuê | Mua |
| Output folder | Nơi lưu file | Hỏi user hoặc dùng Downloads |

## Bước 1: Search trên batdongsan.com.vn

### URL Pattern

batdongsan.com.vn sử dụng URL structure dạng path-based. Đọc file `references/bds_url_guide.md` để biết cách xây dựng URL search chính xác cho từng loại BĐS và bộ lọc.

### Quy trình search

1. **Mở Chrome** tab mới, navigate tới URL đã xây dựng
2. **Đọc kết quả search** bằng `read_page` hoặc `get_page_text`
3. **Extract thông tin** từ mỗi listing card:
   - Tên dự án / tiêu đề tin
   - Giá (tỷ hoặc triệu/m2)
   - Diện tích
   - Số phòng ngủ, WC
   - Địa chỉ (đường, phường, quận)
   - Link chi tiết
4. **Paginate** nếu cần: click nút trang tiếp hoặc thay đổi URL param `page=2`
5. **Mục tiêu**: thu thập 15-30 listings phù hợp tiêu chí

### Xử lý trường hợp đặc biệt

- **Listing trùng lặp**: Cùng dự án nhưng nhiều tin đăng → Gom thành 1 entry, lấy khoảng giá min-max
- **Giá không rõ**: "Thỏa thuận" → ghi "Thỏa thuận" trong cột giá
- **Dự án mới**: Chưa có nhiều tin → vẫn include, ghi chú "Mới mở bán"

## Bước 2: Lấy tọa độ từ Google Maps

Với mỗi dự án/listing đã extract:

1. Navigate Chrome tới `https://www.google.com/maps/search/{tên dự án + quận}`
2. Đợi map load, đọc URL → extract lat/lng từ URL parameter `@{lat},{lng},{zoom}z`
3. Nếu Google Maps không tìm thấy chính xác → thử search với địa chỉ đầy đủ
4. Lưu tọa độ vào data array

**Tối ưu**: Có thể batch search nhiều dự án bằng cách mở từng tab hoặc search tuần tự.

**Fallback**: Nếu không lấy được tọa độ từ Google Maps, sử dụng tọa độ trung tâm của quận/phường tương ứng.

## Bước 3: Tạo file Excel

Sử dụng Python openpyxl để tạo Excel file. Đọc và chạy script `scripts/generate_excel.py` với data đã thu thập.

### Cấu trúc Excel

**Sheet 1 — "Danh Sách BĐS"**:
| STT | Dự Án | Loại | Khoảng Giá | Diện Tích | Phòng Ngủ | WC | Địa Chỉ | Quận | Ghi Chú | Link BĐS |

**Sheet 2 — "Tọa Độ (Map)"** (cho Google My Maps import):
| Dự Án | Quận | Lat | Lng | Giá | Địa Chỉ |

### Formatting rules:
- Header row: bold, dark blue background (#1F4E79), white text, freeze panes
- Auto-filter trên tất cả cột
- Color-code theo quận (mỗi quận 1 màu nền nhạt khác nhau)
- Cột "Link BĐS": hyperlink clickable
- Column width: auto-fit dựa trên content
- Number format: giá tiền dùng format text (vì "3.2-4.8 tỷ" là text)

## Bước 4: Tạo HTML Map tương tác

Tạo file HTML sử dụng Leaflet.js + OpenStreetMap tiles. Đọc template từ `assets/map_template.html` và customize với data thực tế.

### Thành phần bản đồ:

1. **District boundary polygons** — Đọc data từ `references/tphcm_districts.json` cho ranh giới 22 quận/huyện TPHCM. Mỗi quận có màu riêng, đường viền dashed, fill opacity thấp (0.08), label tên quận ở center.

2. **Property markers** — Numbered circles với popup chứa:
   - Tên dự án
   - Giá
   - Diện tích + phòng ngủ
   - Địa chỉ
   - Link tới batdongsan.com.vn

3. **Side panel** (bên phải, 320px):
   - Header với title + thống kê
   - Filter buttons theo quận
   - Danh sách dự án (click → zoom tới marker)

4. **Filter functionality**:
   - Nút "Tất cả" hiện toàn bộ
   - Nút mỗi quận → filter markers + list, zoom vào quận đó
   - Responsive: trên mobile panel xuống dưới

### Lưu ý kỹ thuật quan trọng:

- **File phải là single self-contained HTML** — tất cả CSS/JS inline, chỉ CDN external là Leaflet
- **Dùng Write tool** để tạo file HTML — KHÔNG dùng bash heredoc vì sẽ bị lỗi escape ký tự `!` trong `<!DOCTYPE html>`
- **Leaflet CDN**: `https://unpkg.com/leaflet@1.9.4/dist/leaflet.css` và `.js`
- **Encoding**: UTF-8, không BOM

## Bước 5: Verify & Deliver

1. **Verify HTML**: Đọc lại file HTML bằng Read tool, kiểm tra dòng đầu là `<!DOCTYPE html>` (không phải `<\!DOCTYPE html>`)
2. **Verify Excel**: Kiểm tra file size > 0 bytes
3. **Delivery**: Cung cấp computer:// link cho cả 2 file

### Chrome Remote Verification (tùy chọn)

Nếu user yêu cầu verify trên Chrome:
- Chrome remote KHÔNG mở được local `file:///` URLs
- **Workaround**: Navigate tới `example.com`, dùng `document.open()` + `document.write()` để inject HTML content, rồi inject JS data và logic qua `javascript_tool` từng phần
- Take screenshot để verify map render đúng

## Troubleshooting

| Vấn đề | Giải pháp |
|---------|-----------|
| `<\!DOCTYPE html>` trong file | File bị tạo bằng bash heredoc → tạo lại bằng Write tool |
| Chrome không mở file local | Dùng workaround: inject HTML vào blank page |
| batdongsan.com.vn block bot | Dùng Chrome browser tool, không dùng curl/fetch |
| Google Maps không tìm thấy | Search bằng địa chỉ thay vì tên dự án |
| Network blocked trong sandbox | Dùng Chrome JS fetch trên github.com page cho raw.githubusercontent.com |
| Leaflet tiles không load | Kiểm tra HTTPS, dùng `{s}.tile.openstreetmap.org` |

## File References

- `references/bds_url_guide.md` — Hướng dẫn xây dựng URL search trên batdongsan.com.vn
- `references/tphcm_districts.json` — Boundary polygon data cho 22 quận/huyện TPHCM (simplified)
- `scripts/generate_excel.py` — Python script tạo Excel file với openpyxl
- `assets/map_template.html` — Template HTML map với Leaflet.js
