package org.homeletter.app

import android.content.Intent
import android.os.Bundle
import android.speech.tts.TextToSpeech
import androidx.activity.ComponentActivity

import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
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
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.background
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

    Column(modifier = modifier.fillMaxSize().padding(16.dp).background(Color.White.copy(alpha = 0.1f))) {
        Text(text = title, style = MaterialTheme.typography.titleLarge.copy(fontWeight = FontWeight.Bold))
        Spacer(modifier = Modifier.height(12.dp))
        Text(
            text = content,
            style = MaterialTheme.typography.bodyLarge.copy(fontWeight = FontWeight.Bold),
            modifier = Modifier.padding(8.dp)
        )

        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = {
            tts?.speak(content, TextToSpeech.QUEUE_FLUSH, null, "mail_read")
        }) { Text("\u25B6") }

        // 移除分享功能以與 Web 版一致（不提供 Facebook / LINE 分享）
    }
}