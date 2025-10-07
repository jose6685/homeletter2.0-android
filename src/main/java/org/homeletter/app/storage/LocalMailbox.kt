package org.homeletter.app.storage

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import org.homeletter.app.api.MailItem

object LocalMailbox {
    private const val PREFS_NAME = "mailbox_prefs"
    private const val KEY_MAILBOX = "mailbox_json"

    fun load(context: Context): List<MailItem> {
        return try {
            val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            val json = prefs.getString(KEY_MAILBOX, "[]") ?: "[]"
            val arr = JSONArray(json)
            (0 until arr.length()).map { i ->
                val o = arr.getJSONObject(i)
                MailItem(
                    id = o.optString("id"),
                    title = o.optString("title"),
                    content = o.optString("content"),
                    directions = o.optString("directions", null),
                    verses = o.optString("verses", null),
                    actions = o.optString("actions", null),
                    createdAt = o.optLong("createdAt", System.currentTimeMillis())
                )
            }
        } catch (_: Throwable) {
            emptyList()
        }
    }

    fun save(context: Context, items: List<MailItem>) {
        val arr = JSONArray()
        for (item in items) {
            arr.put(
                JSONObject()
                    .put("id", item.id)
                    .put("title", item.title)
                    .put("content", item.content)
                    .put("directions", item.directions)
                    .put("verses", item.verses)
                    .put("actions", item.actions)
                    .put("createdAt", item.createdAt)
            )
        }
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(KEY_MAILBOX, arr.toString()).apply()
    }

    fun append(context: Context, item: MailItem) {
        val current = load(context)
        save(context, listOf(item) + current)
    }

    fun clear(context: Context) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        prefs.edit().putString(KEY_MAILBOX, "[]").apply()
    }
}