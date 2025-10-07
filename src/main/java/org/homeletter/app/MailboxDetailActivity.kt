package org.homeletter.app

import android.content.Intent
import android.os.Bundle
import android.speech.tts.TextToSpeech
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
class MailboxDetailActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val title = intent.getStringExtra("title") ?: ""
        val content = intent.getStringExtra("content") ?: ""

        setContent {
            MaterialTheme {
                Scaffold(
                    topBar = { TopAppBar(title = { Text(text = "詳情") }) }
                ) { padding ->
                    DetailContent(
                        title = title,
                        content = content,
                        modifier = Modifier.padding(padding)
                    )
                }
            }
        }
    }
}

@Composable
private fun DetailContent(title: String, content: String, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    var tts: TextToSpeech? = null
    var paused by remember { mutableStateOf(false) }

    DisposableEffect(Unit) {
        tts = TextToSpeech(context) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.TAIWAN
            }
        }
        onDispose {
            tts?.shutdown()
            tts = null
        }
    }

    Column(modifier = modifier.fillMaxSize().padding(16.dp)) {
        Text(text = title, style = MaterialTheme.typography.titleLarge)
        Spacer(modifier = Modifier.height(12.dp))
        Text(text = content, style = MaterialTheme.typography.bodyLarge)

        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = {
            // 切換播放/暫停（TextToSpeech 無原生暫停，這裡以 stop 模擬暫停，播放時重新從頭朗讀）
            if (paused) {
                tts?.speak(content, TextToSpeech.QUEUE_FLUSH, null, "mail_read")
                paused = false
            } else {
                tts?.stop()
                paused = true
            }
        }) { Text(if (paused) "播放" else "暫停") }

        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = {
            val share = Intent(Intent.ACTION_SEND).apply {
                type = "text/plain"
                putExtra(Intent.EXTRA_SUBJECT, title)
                putExtra(Intent.EXTRA_TEXT, "$title\n\n$content")
            }
            context.startActivity(Intent.createChooser(share, "分享信件"))
        }) { Text("分享") }
    }
}