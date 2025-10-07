package org.homeletter.app.api

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import org.homeletter.app.BuildConfig

data class GenerateResult(
    val raw: String,
    val directions: String? = null,
    val verses: String? = null,
    val actions: String? = null,
)

data class MailItem(
    val id: String,
    val title: String,
    val content: String,
    val directions: String? = null,
    val verses: String? = null,
    val actions: String? = null,
    val createdAt: Long
)

class ApiClient(
    private val baseUrl: String = DEFAULT_BASE_URL,
) {
    private val client = OkHttpClient()

    suspend fun generate(theme: String): GenerateResult = withContext(Dispatchers.IO) {
        val json = JSONObject().put("topic", theme)
        val body = json.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
        val request = Request.Builder()
            .url("$baseUrl/api/generate")
            .post(body)
            .build()
        client.newCall(request).execute().use { resp ->
            val text = resp.body?.string() ?: "{}"
            val root = runCatching { JSONObject(text) }.getOrNull()
            val data = root?.optJSONObject("data")
            // 以後端 JSON 的「完整信件」為主要文字，若無則退回 letter/raw
            val letter = data?.optString("完整信件")
                ?: data?.optString("letter")
                ?: text
            val directions = data?.optString("三方向")
            val verses = data?.optString("兩經文")
            val actions = data?.optString("兩個行動呼籱")
            GenerateResult(
                raw = letter,
                directions = directions,
                verses = verses,
                actions = actions,
            )
        }
    }

    suspend fun getMailbox(): List<MailItem> = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("$baseUrl/api/mailbox")
            .get()
            .build()
        client.newCall(request).execute().use { resp ->
            val text = resp.body?.string() ?: "{}"
            val root = runCatching { JSONObject(text) }.getOrNull()
            val arr = root?.optJSONArray("list") ?: JSONArray()
            (0 until arr.length()).map { i ->
                val o = arr.getJSONObject(i)
                MailItem(
                    id = o.optString("id"),
                    title = o.optString("topic"),
                    content = o.optString("text"),
                    directions = o.optString("directions", null),
                    verses = o.optString("verses", null),
                    actions = o.optString("actions", null),
                    createdAt = o.optLong("createdAt", System.currentTimeMillis())
                )
            }
        }
    }

    suspend fun createMail(
        title: String,
        content: String,
        directions: String? = null,
        verses: String? = null,
        actions: String? = null,
    ): MailItem = withContext(Dispatchers.IO) {
        // 後端需要 topic/text 欄位，並可選帶入 directions/verses/actions
        val json = JSONObject()
            .put("topic", title)
            .put("text", content)
        if (directions != null) json.put("directions", directions)
        if (verses != null) json.put("verses", verses)
        if (actions != null) json.put("actions", actions)
        val body = json.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
        val request = Request.Builder()
            .url("$baseUrl/api/mailbox")
            .post(body)
            .build()
        client.newCall(request).execute().use { resp ->
            val o = runCatching { JSONObject(resp.body?.string() ?: "{}") }.getOrNull()
            val id = o?.optString("id") ?: ""
            MailItem(
                id = id,
                title = title,
                content = content,
                directions = directions,
                verses = verses,
                actions = actions,
                createdAt = System.currentTimeMillis()
            )
        }
    }

    suspend fun deleteMail(id: String): Boolean = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("$baseUrl/api/mailbox/$id")
            .delete()
            .build()
        client.newCall(request).execute().use { resp ->
            resp.isSuccessful
        }
    }

    companion object {
        val DEFAULT_BASE_URL: String = BuildConfig.API_BASE_URL
    }
}