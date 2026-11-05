# checkout-uz

[CHECKOUT.UZ](https://checkout.uz) merchant API'si uchun rasmiy Python kutubxonasi — bitta paket orqali **v1** va **v2** versiyalarining ikkalasiga ham kirish imkoni.

```python
from checkout_uz import CheckoutClient

client = CheckoutClient(api_key="kassangizning_api_kaliti")
payment = client.v2.create_payment(amount=50000, description="Buyurtma #1")
print(payment["payment"]["_url"])  # shu havolani mijozga yuboring
```

## O'rnatish

Hozircha PyPI'da emas — to'g'ridan-to'g'ri GitHub'dan o'rnating:

```bash
pip install git+https://github.com/otabek-hasanov/checkout.uz-python.git
```

Yoki klonlab, mahalliy o'rnating:

```bash
git clone https://github.com/otabek-hasanov/checkout.uz-python.git
cd checkout.uz-python
pip install -e .
```

## API kalitini qayerdan olish mumkin

1. [checkout.uz](https://checkout.uz)ga kiring → **Kassalar** → kerakli kassani oching → **Sozlamalar**.
2. U yerda ko'rsatilgan **API KEY**ni nusxalang.
3. Bu kalitni hech kimga bermang — u orqali kassangiz nomidan barcha so'rovlar yuboriladi. Uni hech qachon frontend/client-side (brauzer, mobil ilova) kodiga yozmang — faqat server tomonida ishlating.

## Tezkor boshlash

```python
from checkout_uz import CheckoutClient, CheckoutAPIError

client = CheckoutClient(api_key="kassangizning_api_kaliti")

try:
    payment = client.v2.create_payment(
        amount=50000,              # so'mda, 1000 - 10 000 000 oralig'ida
        description="Buyurtma #1",
        expire_time=3600,          # ixtiyoriy, soniyada, standart 1 soat
    )
    print(payment["payment"]["_url"])     # mijozni shu to'lov sahifasiga yo'naltiring
    print(payment["payment"]["_uuid"])    # buni saqlab qo'ying - to'lovning doimiy ID'si
except CheckoutAPIError as e:
    print(f"Xatolik ({e.status_code}): {e.message}")
```

Mijoz to'lov qilgandan keyin, checkout.uz sizning `webhook_url`'ingizga xabar yuboradi (agar sozlagan bo'lsangiz) — yoki `status_payment` orqali o'zingiz tekshirishingiz mumkin:

```python
status = client.v2.status_payment(uuid=payment["payment"]["_uuid"])
print(status["data"]["status"])  # "pending" / "paid" / "canceled" / "reversed"
```

## v1 va v2 farqi

Ikkalasi ham bitta client'da mavjud — xohlasangiz ikkalasini aralashtirib ishlatavering, xohlasangiz o'z vaqtingizda v2'ga o'ting:

```python
client.v1.create_payment(amount=50000)
client.v2.create_payment(amount=50000, expire_time=7200, idempotency_key="order-42")
```

v2 v1'ning hamma imkoniyatlari ustiga quyidagilarni qo'shadi:

- `idempotency_key` (`create_payment`da) — xavfsiz qayta urinish uchun: shu kalit bilan 24 soat ichida qayta so'ralsa, yangi invoys ochilmaydi, eskisi qaytariladi (takroriy to'lov havolasi yaratilib ketishining oldini oladi)
- `expire_time` — invoys qancha vaqt ochiq turishini (avtomatik bekor bo'lishidan oldin) belgilash
- `get_history(..., offset=, status=, date_from=, date_to=)` — sahifalash va filtrlash
- `get_stats(...)` — endi `by_provider` (to'lov tizimi bo'yicha) taqsimot bilan
- `cancel_payment(order_id)` — hali "kutilmoqda" holatidagi invoysni bekor qilish
- `refund_payment(order_id)` — muvaffaqiyatli to'lovni qaytarish (to'lovdan keyingi ma'lum vaqt oralig'ida)
- `get_fiscal(order_id)` — Payme/Click/Plum to'lovlari uchun fiskal (soliq) chekni olish

`pay_via_card` va `confirm_card_payment` (SMS tasdiqlash bilan to'g'ridan-to'g'ri karta to'lovi) `client.v1`'da ham, `client.v2`'da ham bir xil ishlaydi.

## Metodlar ro'yxati

Boshqacha ko'rsatilmagan bo'lsa, barcha metodlar ham `client.v1`, ham `client.v2`'da mavjud. Har bir metod `POST` so'rovi yuboradi va javobni Python `dict` sifatida qaytaradi.

| Metod | Majburiy argumentlar | Nima qiladi |
|---|---|---|
| `create_payment` | `amount` | Yangi to'lov havolasi (invoys) yaratadi |
| `status_payment` | `id` yoki `uuid` | Bitta invoysning joriy holatini ko'rsatadi |
| `get_balance` | — | Kassaning joriy balansi (valyuta bo'yicha) |
| `get_history` | — | So'nggi invoyslar ro'yxati, yangisidan eskisiga |
| `get_stats` | — | Buyurtmalar soni / umumiy tushum |
| `get_payment_methods` | — | Kassada yoqilgan to'lov usullari |
| `pay_via_card` | `order_id`, `card_number`, `card_expiry` | To'g'ridan-to'g'ri Uzcard/Humo to'lovini boshlaydi |
| `confirm_card_payment` | `payment_token`, `sms_code` | Karta to'lovini SMS kod bilan tasdiqlaydi |
| `cancel_payment` *(faqat v2)* | `order_id` | Kutilayotgan invoysni bekor qiladi |
| `refund_payment` *(faqat v2)* | `order_id` | Muvaffaqiyatli to'lovni qaytaradi |
| `get_fiscal` *(faqat v2)* | `order_id` | Fiskal (soliq) chekni oladi |

Har bir metodning barcha ixtiyoriy argumentlari uchun — `help(client.v2.create_payment)` orqali to'liq tavsifni ko'rishingiz mumkin.

## Hisob darajasidagi metodlar (`ProfileClient`)

v2'dagi 3 ta metod — `get_profile`, `get_shops`, `get_profile_stats` — **bitta kassaga emas, butun hisobingizga** tegishli. Ular alohida *profil API kaliti* bilan ishlaydi (biror kassaning emas, hisob sozlamalaridagi kalit) va sizga tegishli barcha kassalar bo'yicha ma'lumot ko'rsatadi. Kredensial boshqacha bo'lgani uchun, bu metodlar `CheckoutClient`da emas, alohida client'da joylashgan:

```python
from checkout_uz import ProfileClient

profile = ProfileClient(profile_api_key="profil_api_kalitingiz")
shops = profile.get_shops()
stats = profile.get_profile_stats(date_from="2026-01-01")
```

## Xatoliklarni qayta ishlash

Har bir metod muvaffaqiyatsizlikda (2xx bo'lmagan HTTP holat yoki tarmoq xatosi) `checkout_uz.CheckoutAPIError` xatoligini chiqaradi. Qaytgan dict'ni "muvaffaqiyatlimi yoki yo'qmi" deb tekshirib o'tirishingiz shart emas:

```python
from checkout_uz import CheckoutAPIError

try:
    client.v2.refund_payment(order_id=123)
except CheckoutAPIError as e:
    print(e.status_code, e.message)   # masalan: 409 "More than 22 hours have passed..."
```

## To'liq API hujjatlari

- v1: https://checkout.uz/api-docs/v1
- v2: https://checkout.uz/api-docs/v2

## Ishlab chiqish (development)

```bash
pip install -e ".[test]"
pytest
```

Barcha testlar HTTP so'rovlarini soxtalashtiradi (mock) — hech biri haqiqiy checkout.uz API'siga murojaat qilmaydi, shuning uchun istalgan joyda xavfsiz ishga tushirish mumkin.

## Litsenziya

MIT
