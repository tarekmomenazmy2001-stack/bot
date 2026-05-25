from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

import routeros_api
import random

# ================== بيانات البوت ==================
TOKEN = "8790966490:AAFcjbv8_yemhjFuzNHvm29Doc7UHZCPNXg"
ADMIN_ID = 5960386794

# ================== بيانات الدفع ==================
VODAFONE_CASH = "01024694898"
INSTAPAY_LINK = "https://ipn.eg/S/tarek.moamen.azmy/instapay/1ZurXa"

# ================== بيانات الميكروتك ==================
MIKROTIK_IP = "25.0.0.1"
MIKROTIK_USER = "admin"
MIKROTIK_PASS = "#39610"

# ================== الباقات ==================
plans = {
    "1": {
        "name": "500 ميجابيت",
        "price": "5 جنيه",
        "prefix": "a",
        "profile": "2.Mega / 2.User",
        "limit": 500
    },

    "2": {
        "name": "1.5 جيجابيت",
        "price": "10 جنيه",
        "prefix": "b",
        "profile": "2.Mega / 2.User",
        "limit": 1536
    },

    "3": {
        "name": "4 جيجابيت",
        "price": "20 جنيه",
        "prefix": "c",
        "profile": "4.Mega / 2.User",
        "limit": 4096
    },

    "4": {
        "name": "10 جيجابيت",
        "price": "45 جنيه",
        "prefix": "d",
        "profile": "4.Mega / 2.User",
        "limit": 10240
    },

    "5": {
        "name": "15 جيجابيت",
        "price": "60 جنيه",
        "prefix": "e",
        "profile": "4.Mega / 2.User",
        "limit": 15360
    },

    "6": {
        "name": "20 جيجابيت",
        "price": "80 جنيه",
        "prefix": "f",
        "profile": "6.Mega / 2.User",
        "limit": 20480
    },

    "7": {
        "name": "30 جيجابيت",
        "price": "100 جنيه",
        "prefix": "g",
        "profile": "6.Mega / 2.User",
        "limit": 30720
    },

    "8": {
        "name": "50 جيجابيت",
        "price": "160 جنيه",
        "prefix": "h",
        "profile": "8.Mega / 2.User",
        "limit": 51200
    },
}

# ================== الطلبات المعلقة ==================
pending = {}

# ================== الاتصال بالميكروتك ==================
def connect_mikrotik():

    connection = routeros_api.RouterOsApiPool(
        host=MIKROTIK_IP,
        username=MIKROTIK_USER,
        password=MIKROTIK_PASS,
        plaintext_login=True
    )

    return connection.get_api()

# ================== إنشاء يوزر ==================
def create_hotspot_user(username, password, profile, limit_mb):

    api = connect_mikrotik()

    hotspot = api.get_resource('/ip/hotspot/user')

    # تحويل MB إلى Bytes
    limit_bytes = limit_mb * 1024 * 1024

    hotspot.add(
        name=username,
        password=password,
        profile=profile,
        **{
            "limit-bytes-total": str(limit_bytes)
        }
    )

# ================== رسالة البداية ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "🌐 شبكة الإمبراطورية للإنترنت 🌐\n\n"

        "{الشبكة رقم واحد فى دماريس}\n\n"

        "🔥 أقوى العروض بأفضل الأسعار 🔥\n\n"

        "1- باقة 500 ميجابيت {5 جنيه}\n"
        "2- باقة 1.5 جيجابيت {10 جنيه}\n"
        "3- باقة 4 جيجابيت {20 جنيه}\n"
        "4- باقة 10 جيجابيت {45 جنيه}\n"
        "5- باقة 15 جيجابيت {60 جنيه}\n"
        "6- باقة 20 جيجابيت {80 جنيه}\n"
        "7- باقة 30 جيجابيت {100 جنيه}\n"
        "8- باقة 50 جيجابيت {160 جنيه}\n\n"

        "📩 أرسل رقم الباقة فقط :"
    )

    await update.message.reply_text(text)

# ================== التعامل مع المستخدم ==================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    # ================== اختيار الباقة ==================
    if update.message.text and update.message.text in plans:

        plan_id = update.message.text

        pending[user_id] = plan_id

        plan = plans[plan_id]

        # ================== أزرار الدفع ==================
        keyboard = [

            [
                InlineKeyboardButton(
                    "📱 فودافون كاش",
                    callback_data="vodafone"
                )
            ],

            [
                InlineKeyboardButton(
                    "🏦 انستا باي",
                    url=INSTAPAY_LINK
                )
            ]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"تم إختيار الباقة التي تناسبك ✅\n\n"

            f"📦 الباقة: {plan['name']}\n\n"

            f"💰 السعر: {plan['price']}\n\n"

            f"💳 اختر طريقة الدفع المناسبة\n\n"

            f"📸 بعد التحويل ابعت صورة العملية",

            reply_markup=reply_markup
        )

    # ================== استقبال صورة التحويل ==================
    elif update.message.photo:

        if user_id not in pending:

            await update.message.reply_text(
                "اختر باقة أولاً ❌"
            )

            return

        await update.message.reply_text(
            "جاري مراجعة التحويل ⏳"
        )

        plan_id = pending[user_id]

        plan = plans[plan_id]

        # ================== بيانات المستخدم ==================
        full_name = update.message.from_user.full_name

        username = update.message.from_user.username

        if username:
            username_text = f"@{username}"
        else:
            username_text = "لا يوجد"

        # ================== أزرار الأدمن ==================
        keyboard = [

            [
                InlineKeyboardButton(
                    "موافقة ✅",
                    callback_data=f"ok_{user_id}"
                ),

                InlineKeyboardButton(
                    "رفض ❌",
                    callback_data=f"no_{user_id}"
                )
            ]

        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        # ================== إرسال صورة للأدمن ==================
        await context.bot.send_photo(
            chat_id=ADMIN_ID,

            photo=update.message.photo[-1].file_id,

            caption=(
                f"💸 طلب جديد\n\n"

                f"👤 الاسم: {full_name}\n"

                f"📱 يوزر تيليجرام: {username_text}\n"

                f"🆔 USER ID: {user_id}\n\n"

                f"📦 الباقة: {plan['name']}\n"

                f"💰 السعر: {plan['price']}"
            ),

            reply_markup=reply_markup
        )

# ================== أزرار البوت ==================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    # ================== زر فودافون كاش ==================
    if data == "vodafone":

        await query.message.reply_text(
            f"📱 رقم فودافون كاش:\n\n{VODAFONE_CASH}"
        )

        return

    # ================== طلب جديد ==================
    if data == "new_order":

        if query.from_user.id in pending:
            del pending[query.from_user.id]

        text = (
            "🌐 شبكة الإمبراطورية للإنترنت 🌐\n\n"

            "🔥 اختر الباقة المناسبة 🔥\n\n"

            "1- باقة 500 ميجابيت {5 جنيه}\n"
            "2- باقة 1.5 جيجابيت {10 جنيه}\n"
            "3- باقة 4 جيجابيت {20 جنيه}\n"
            "4- باقة 10 جيجابيت {45 جنيه}\n"
            "5- باقة 15 جيجابيت {60 جنيه}\n"
            "6- باقة 20 جيجابيت {80 جنيه}\n"
            "7- باقة 30 جيجابيت {100 جنيه}\n"
            "8- باقة 50 جيجابيت {160 جنيه}\n\n"

            "📩 أرسل رقم الباقة فقط :"
        )

        await query.message.reply_text(text)

        return

    # ================== أزرار الأدمن ==================
    if data.startswith("ok_") or data.startswith("no_"):

        action, user_id = data.split("_")

        user_id = int(user_id)

        # التأكد من وجود الطلب
        if user_id not in pending:

            await query.edit_message_caption(
                "❌ الطلب منتهي"
            )

            return

        plan_id = pending[user_id]

        plan = plans[plan_id]

        # ================== موافقة ==================
        if action == "ok":

            try:

                # إنشاء بيانات اليوزر
                username = plan["prefix"] + str(
                    random.randint(000000, 999999)
                )

                password = str(
                    random.randint(0000, 9999)
                )

                profile = plan["profile"]

                limit_mb = plan["limit"]

                # إنشاء يوزر ميكروتك
                create_hotspot_user(
                    username,
                    password,
                    profile,
                    limit_mb
                )

                # ================== زر طلب جديد ==================
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "🔄 طلب جديد",
                            callback_data="new_order"
                        )
                    ]
                ]

                reply_markup = InlineKeyboardMarkup(keyboard)

                # إرسال البيانات للمستخدم
                await context.bot.send_message(
                    chat_id=user_id,

                    text=(
                        "✅ تم التفعيل بنجاح\n\n"

                        f"👤 اليوزر:\n{username}\n\n"

                        f"🔑 الباسورد:\n{password}\n\n"

                        f"📦 الباقة:\n{plan['name']}"
                    ),

                    reply_markup=reply_markup
                )

                await query.edit_message_caption(
                    "✅ تم قبول الطلب وإنشاء اليوزر"
                )

            except Exception as e:

                await query.edit_message_caption(
                    f"❌ حدث خطأ:\n{e}"
                )

        # ================== رفض ==================
        elif action == "no":

            # ================== زر طلب جديد ==================
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔄 طلب جديد",
                        callback_data="new_order"
                    )
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=user_id,

                text="❌ تم رفض عملية الدفع",

                reply_markup=reply_markup
            )

            await query.edit_message_caption(
                "❌ تم رفض الطلب"
            )

        # حذف الطلب
        del pending[user_id]

# ================== تشغيل البوت ==================
app = Application.builder().token(TOKEN).build()

# start
app.add_handler(
    CommandHandler("start", start)
)

# الرسائل والصور
app.add_handler(
    MessageHandler(
        filters.TEXT | filters.PHOTO,
        handle
    )
)

# الأزرار
app.add_handler(
    CallbackQueryHandler(buttons)
)

# تشغيل البوت
print("🚀 Bot running...")

app.run_polling()