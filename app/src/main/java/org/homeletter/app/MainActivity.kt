import androidx.compose.foundation.layout.widthIn
package org.homeletter.app

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.wrapContentHeight
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.ui.Alignment
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import kotlinx.coroutines.launch
import org.homeletter.app.api.ApiClient
import org.homeletter.app.api.MailItem
import org.homeletter.app.storage.LocalMailbox
import com.google.android.gms.ads.AdRequest
import com.google.android.gms.ads.AdSize
import com.google.android.gms.ads.AdView
import androidx.compose.ui.viewinterop.AndroidView
import androidx.compose.runtime.Composable

@OptIn(ExperimentalMaterial3Api::class)
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            var mailbox by remember { mutableStateOf<List<MailItem>>(emptyList()) }
            var error by remember { mutableStateOf<String?>(null) }
            var theme by remember { mutableStateOf("") }
            var generating by remember { mutableStateOf(false) }
            val api = remember { ApiClient() }
            val scope = rememberCoroutineScope()
            val context = LocalContext.current

            LaunchedEffect(Unit) {
                val local = LocalMailbox.load(context)
                if (local.isNotEmpty()) {
                    mailbox = local
                }
                runCatching { api.getMailbox() }
                    .onSuccess { mailbox = it; LocalMailbox.save(context, it) }
                    .onFailure { error = it.message }
            }

            MaterialTheme {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(16.dp) // 調整內邊距以適應不同螢幕
                ) {

                    Text(
                        text = "天父的家書",
                        color = Color(0xFFFFD700),
                        style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold),
                        modifier = Modifier.align(Alignment.TopStart).padding(16.dp)
                    )

                    Column(
                        modifier = Modifier
                            .fillMaxSize()
                            .imePadding()
                            .padding(horizontal = 16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        OutlinedTextField(
                            value = theme,
                            onValueChange = { theme = it },
                            label = { Text("主題/關鍵字") },
                            modifier = Modifier
                                .fillMaxWidth()
                                .widthIn(max = 700.dp) // 調整最大寬度以適應不同螢幕
                                .wrapContentHeight()
                        )
                        Button(
                            onClick = {
                                if (!generating) {
                                    scope.launch {
                                        generating = true
                                        try {
                                            val result = api.generate(theme)
                                            val title = theme.ifBlank { "主題信" }
                                            val created = runCatching {
                                                api.createMail(title = title, content = result.raw)
                                            }.getOrElse { e ->
                                                error = e.message
                                                MailItem(
                                                    id = "",
                                                    title = title,
                                                    content = result.raw,
                                                    createdAt = System.currentTimeMillis()
                                                )
                                            }
                                            mailbox = listOf(created) + mailbox
                                            LocalMailbox.append(context, created)
                                        } catch (e: Throwable) {
                                            error = e.message
                                        }
                                        generating = false
                                    }
                                }
                            },
                            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF6A5ACD)),
                            modifier = Modifier
                                .padding(top = 12.dp)
                        ) {
                            Text(text = if (generating) "生成中…" else "抽卡生成並入信箱")
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        LazyColumn(
                            modifier = Modifier
                                .fillMaxWidth()
                                .widthIn(max = 600.dp) // 調整最大寬度以適應不同螢幕
                                .weight(1f, fill = false)
                        ) {
                            items(mailbox) { item ->
                                Text(
                                    text = item.title,
                                    style = MaterialTheme.typography.titleMedium,
                                    modifier = Modifier
                                        .padding(bottom = 4.dp)
                                        .clickable {
                                            val intent = Intent(context, MailboxDetailActivity::class.java).apply {
                                                putExtra("title", item.title)
                                                putExtra("content", item.content)
                                            }
                                            context.startActivity(intent)
                                        }
                                )
                                Text(
                                    text = item.content,
                                    style = MaterialTheme.typography.bodyMedium
                                )
                            }
                        }

                        if (error != null) {
                            Text(text = "錯誤：$error", color = MaterialTheme.colorScheme.error)
                        }
                    }

                    BannerAd(modifier = Modifier.align(Alignment.BottomCenter))
                }
            }
        }
    }
}

@Composable
private fun BannerAd(modifier: Modifier = Modifier) {
    AndroidView(modifier = modifier, factory = { ctx ->
        AdView(ctx).apply {
            setAdSize(AdSize.BANNER)
            adUnitId = "ca-app-pub-3940256099942544/6300978111" // 測試版位 ID，請替換成正式 ID
            loadAd(AdRequest.Builder().build())
        }
    })
}
@Preview(showBackground = true, name = "Light Theme")
@Composable
fun LightPreview() {
    MaterialTheme {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            Text(text = "主題顏色示例", color = MaterialTheme.colorScheme.primary)
            Text(text = "錯誤顏色示例", color = MaterialTheme.colorScheme.error)
        }
    }
}

@Preview(showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES, name = "Dark Theme")
@Composable
fun DarkPreview() {
    MaterialTheme {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            Text(text = "主題顏色示例", color = MaterialTheme.colorScheme.primary)
            Text(text = "錯誤顏色示例", color = MaterialTheme.colorScheme.error)
        }
    }
}
</insert_content>