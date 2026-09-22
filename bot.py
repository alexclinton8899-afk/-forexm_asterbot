import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import textstat

# Enable logging so you can see errors in Railway logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Read bot token from environment variable (set this on Railway)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hello, {user.first_name}! 👋\n\n"
        "I analyze text and calculate its readability score.\n\n"
        "📖 **How to use:**\n"
        "Just send me any text (a paragraph, an article, or a few sentences), "
        "and I'll calculate its Flesch-Kincaid Grade Level based on sentence length.\n\n"
        "The score tells you what grade level the text is suited for. "
        "For example, a score of 8.0 means an 8th grader can read it easily.\n\n"
        "Send /help to see this again."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when /help is issued."""
    await update.message.reply_text(
        "📖 **Readability Bot Help**\n\n"
        "**What I do:**\n"
        "I calculate the Flesch-Kincaid Grade Level of any text you send me. "
        "This score is based on average sentence length and word complexity.\n\n"
        "**How to use:**\n"
        "Simply send or paste any English text. I'll reply with the grade level score.\n\n"
        "**Understanding the score:**\n"
        "• 1.0 – 6.0: Very easy (elementary school)\n"
        "• 7.0 – 9.0: Easy (middle school)\n"
        "• 10.0 – 12.0: Moderate (high school)\n"
        "• 13.0+: Difficult (college level)\n\n"
        "**Commands:**\n"
        "/start – Welcome message\n"
        "/help – This help message"
    )


async def analyze_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages and calculate readability score."""
    user_text = update.message.text

    # Basic validation: require at least some text
    if not user_text or len(user_text.strip()) < 10:
        await update.message.reply_text(
            "Please send me a longer text to analyze. "
            "At least a sentence or two is needed for an accurate score."
        )
        return

    try:
        # Calculate Flesch-Kincaid Grade Level [citation:3][citation:8]
        grade_score = textstat.flesch_kincaid_grade(user_text)

        # Get a human-readable label
        if grade_score < 6:
            label = "Very Easy"
        elif grade_score < 9:
            label = "Easy"
        elif grade_score < 12:
            label = "Moderate"
        else:
            label = "Difficult"

        # Get word count for context
        word_count = len(user_text.split())

        await update.message.reply_text(
            f"📊 **Readability Analysis**\n\n"
            f"**Flesch-Kincaid Grade Level:** {grade_score:.1f}\n"
            f"**Reading Level:** {label}\n"
            f"**Word Count:** {word_count}\n\n"
            f"This means the text is suited for a student in grade {grade_score:.0f} "
            f"or above."
        )

    except Exception as e:
        logger.error(f"Error calculating readability: {e}")
        await update.message.reply_text(
            "Sorry, something went wrong while analyzing your text. "
            "Please try again with different text."
        )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "I don't recognize that command. Send /help to see what I can do, "
        "or just paste some text for analysis."
    )


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register handlers [citation:1]
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_text)
    )
    application.add_handler(
        MessageHandler(filters.COMMAND, unknown_command)
    )

    logger.info("Readability Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()
