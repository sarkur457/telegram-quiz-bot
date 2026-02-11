import json
import time
import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# JSON fayllarını yükləmək
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_scores():
    if os.path.exists("scores.json"):
        with open("scores.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False)

questions = load_questions()
scores = load_scores()

current_q_index = 0
question_active = False
answers_received = {}

# Başlama komandası
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Quiz başladı!")
    ask_question(update, context)

# Sual sor
def ask_question(update: Update, context: CallbackContext):
    global current_q_index, question_active, answers_received
    if current_q_index < len(questions):
        q_text = questions[current_q_index]["q"]
        update.message.reply_text(f"Sual: {q_text} (1 dəqiqə)")
        question_active = True
        answers_received = {}
        # 60 saniyə sonra avtomatik cavabı göstər
        context.job_queue.run_once(reveal_answer, 60, context=update.message.chat_id)
    else:
        show_scores(update)

# Cavabları yoxla
def answer_handler(update: Update, context: CallbackContext):
    global current_q_index, question_active, answers_received, scores
    if not question_active:
        return
    user = update.message.from_user.username or update.message.from_user.first_name
    text = update.message.text.strip()
    correct = questions[current_q_index]["a"]
    if text.lower() == correct.lower() and user not in answers_received:
        answers_received[user] = time.time()
        # Puan əlavə et
        scores[user] = scores.get(user, 0) + 1
        save_scores(scores)
        update.message.reply_text(f"Doğru! {user} 1 puan qazandı. Cavab: {correct}")
        question_active = False
        current_q_index += 1
        ask_question(update, context)

# Süre bitdiğinde cavabı göstər
def reveal_answer(context: CallbackContext):
    global question_active, current_q_index
    if question_active:
        chat_id = context.job.context
        correct = questions[current_q_index]["a"]
        context.bot.send_message(chat_id=chat_id, text=f"Vaxt bitdi! Doğru cavab: {correct}")
        question_active = False
        current_q_index += 1
        context.bot.send_message(chat_id=chat_id, text="Sonrakı sual gəlir...")

# Nəticələri göstər
def show_scores(update: Update):
    if scores:
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        msg = "Puanlar:\n" + "\n".join([f"{user}: {score}" for user, score in sorted_scores])
    else:
        msg = "Hələ heç kim puan qazanmamışdır."
    update.message.reply_text(msg)

def main():
    updater = Updater(os.environ[8570643844:AAFMhpfKtP5wlqZUjCHaILhPYjgFUJeNSW4])
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, answer_handler))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()