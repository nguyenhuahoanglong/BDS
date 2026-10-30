# data/scenarios.json

Dữ liệu của `loan-calculator.html` (trạng thái hiện tại + các preset). Trang tự nạp file này khi mở.

```json
{
  "format": "bds-loancalc-scenarios",
  "version": 1,
  "updated": "<ISO time>",
  "current": { ...state } | null,
  "presets": { "<tên>": { ...state } }
}
```

- `state` có cùng các trường như `DEFAULT_STATE` trong `loan-calculator.html`
  (`loanBase`, `loan`, `termYears`, `promoRate`, `promoMonths`, `floatRate`, `salary`, `bonus`,
  `otherDebt`, `prepayTiers`, `prepayments`, `monthlyBudget`, `autoPrepayEnabled`, `skipPromoPeriod`, `version: 1`).
- Khi sửa file bằng tay hoặc bằng Claude: **luôn đổi `updated`** sang thời điểm mới. Trang chỉ tự nạp
  khi `updated` khác bản nó đã thấy; trạng thái cũ trên máy được giữ lại thành preset "Máy này trước khi nạp repo ...".
- `current: null` nghĩa là không đổi trạng thái đang mở, chỉ thêm/ghi đè preset.
- Repo đang public nên ai cũng đọc được file này.
