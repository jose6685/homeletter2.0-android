package org.homeletter.app

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
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
import kotlinx.coroutines.launch
import org.homeletter.app.api.ApiClient
import org.homeletter.app.api.MailItem

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
                runCatching { api.getMailbox() }
                    .onSuccess { mailbox = it }
                    .onFailure { error = it.message }
            }

            MaterialTheme {
                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    topBar = { TopAppBar(title = { Text(text = "天父的信") }) }
                ) { innerPadding ->
                    Column(Modifier.padding(innerPadding).fillMaxSize()) {
                        Text(
                            text = "Android 原生版（抽卡生成 + 入信箱）",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        OutlinedTextField(
                            value = theme,
                            onValueChange = { theme = it },
                            label = { Text("主題/關鍵字") },
                            modifier = Modifier.padding(top = 12.dp)
                        )
                        Button(
                            onClick = {
                                if (!generating) {
                                    scope.launch {
                                        generating = true
                                        runCatching {
                                            val result = api.generate(theme)
                                            api.createMail(title = theme.ifBlank { "主題信" }, content = result.raw)
                                        }.onSuccess { created ->
                                            mailbox = listOf(created) + mailbox
                                        }.onFailure { e ->
                                            error = e.message
                                        }
                                        generating = false
                                    }
                                }
                            },
                            modifier = Modifier.padding(top = 12.dp)
                        ) {
                            Text(text = if (generating) "生成中…" else "抽卡生成並入信箱")
                        }
                        LazyColumn(modifier = Modifier.padding(top = 12.dp)) {
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
                }
            }
        }
    }
}