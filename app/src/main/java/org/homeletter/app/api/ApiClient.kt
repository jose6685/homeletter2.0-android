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

data class GenerateResult(val raw: String)

data class MailItem(
    val id: String,
    val title: String,
    val content: String,
    val createdAt: Long
)

class ApiClient(
    private val baseUrl: String = DEFAULT_BASE_URL,
) {
    private val client = OkHttpClient()

    suspend fun generate(theme: String): GenerateResult = withContext(Dispatchers.IO) {
        val json = JSONObject().put("theme", theme)
        val body = json.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
        val request = Request.Builder()
            .url("$baseUrl/api/generate")
            .post(body)
            .build()
        client.newCall(request).execute().use { resp ->
            val text = resp.body?.string() ?: ""
            GenerateResult(text)
        }
    }

    suspend fun getMailbox(): List<MailItem> = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("$baseUrl/api/mailbox")
            .get()
            .build()
        client.newCall(request).execute().use { resp ->
            val text = resp.body?.string() ?: "[]"
            val arr = JSONArray(text)
            (0 until arr.length()).map { i ->
                val o = arr.getJSONObject(i)
                MailItem(
                    id = o.optString("id"),
                    title = o.optString("title"),
                    content = o.optString("content"),
                    createdAt = o.optLong("createdAt", System.currentTimeMillis())
                )
            }
        }
    }

    suspend fun createMail(title: String, content: String): MailItem = withContext(Dispatchers.IO) {
        val json = JSONObject().put("title", title).put("content", content)
        val body = json.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
        val request = Request.Builder()
            .url("$baseUrl/api/mailbox")
            .post(body)
            .build()
        client.newCall(request).execute().use { resp ->
            val o = JSONObject(resp.body?.string() ?: "{}")
            MailItem(
                id = o.optString("id"),
                title = o.optString("title"),
                content = o.optString("content"),
                createdAt = o.optLong("createdAt", System.currentTimeMillis())
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