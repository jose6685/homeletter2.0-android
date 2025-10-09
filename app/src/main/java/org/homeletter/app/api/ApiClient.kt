package org.homeletter.app.api

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.Response
import java.io.IOException
import java.util.concurrent.TimeUnit
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
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .callTimeout(90, TimeUnit.SECONDS)
        .build()

    private fun executeWithRetry(request: Request, attempts: Int = 2, initialDelayMs: Long = 1500): Response? {
        var lastError: Exception? = null
        var delay = initialDelayMs
        repeat(attempts) { idx ->
            try {
                return client.newCall(request).execute()
            } catch (e: IOException) {
                lastError = e
                if (idx < attempts - 1) {
                    try { Thread.sleep(delay) } catch (_: InterruptedException) {}
                    delay = (delay * 2).coerceAtMost(8000)
                }
            }
        }
        return null
    }

    suspend fun generate(theme: String): GenerateResult = withContext(Dispatchers.IO) {
        val json = JSONObject().put("theme", theme)
        val body = json.toString().toRequestBody("application/json; charset=utf-8".toMediaType())
        val request = Request.Builder()
            .url("$baseUrl/api/generate")
            .post(body)
            .build()
        val resp = executeWithRetry(request, attempts = 2)
        if (resp == null) {
            return@withContext GenerateResult("錯誤：連線逾時或伺服器無回應，請稍後重試。")
        }
        resp.use {
            val text = it.body?.string() ?: ""
            GenerateResult(text)
        }
    }

    suspend fun getMailbox(): List<MailItem> = withContext(Dispatchers.IO) {
        val request = Request.Builder()
            .url("$baseUrl/api/mailbox")
            .get()
            .build()
        val resp = executeWithRetry(request, attempts = 2)
        if (resp == null) return@withContext emptyList()
        resp.use {
            val raw = it.body?.string()?.trim() ?: "[]"
            // 後端可能回傳非陣列（例如錯誤頁面或物件），這裡做防禦性解析避免崩潰
            val arr = runCatching {
                when {
                    raw.startsWith("[") -> JSONArray(raw)
                    raw.startsWith("{") -> {
                        val obj = JSONObject(raw)
                        // 嘗試常見鍵名
                        obj.optJSONArray("mailbox")
                            ?: obj.optJSONArray("data")
                            ?: JSONArray()
                    }
                    else -> JSONArray()
                }
            }.getOrElse { JSONArray() }

            (0 until arr.length()).map { i ->
                val o = arr.optJSONObject(i) ?: JSONObject()
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
        val resp = executeWithRetry(request, attempts = 2)
        if (resp == null) {
            val now = System.currentTimeMillis()
            return@withContext MailItem(
                id = "",
                title = title,
                content = "$content\n（未送出，請稍後重試）",
                createdAt = now
            )
        }
        resp.use {
            val o = JSONObject(it.body?.string() ?: "{}")
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
        val resp = executeWithRetry(request, attempts = 2)
        resp?.use { it.isSuccessful } ?: false
    }

    companion object {
        val DEFAULT_BASE_URL: String = BuildConfig.API_BASE_URL
    }
}