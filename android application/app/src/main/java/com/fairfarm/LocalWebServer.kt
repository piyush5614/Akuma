package com.fairfarm

import android.content.Context
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.InetAddress
import java.net.ServerSocket
import java.net.Socket
import java.net.URLDecoder
import java.util.concurrent.atomic.AtomicBoolean
import kotlin.concurrent.thread

class LocalWebServer(
    private val context: Context,
    private val apiUrl: String,
    private val port: Int = 4173
) {
    private var server: ServerSocket? = null
    private val running = AtomicBoolean(false)
    private var worker: Thread? = null

    fun start(): Boolean {
        if (running.get()) return true
        return try {
            server = ServerSocket(port, 50, InetAddress.getLoopbackAddress())
            running.set(true)
            worker = thread(name = "FairFarmLocalWebServer", start = true, isDaemon = true) {
                while (running.get()) {
                    try {
                        val socket = server?.accept() ?: break
                        thread(name = "FairFarmWebRequest", start = true, isDaemon = true) {
                            handle(socket)
                        }
                    } catch (_: Exception) {
                        if (running.get()) continue
                    }
                }
            }
            true
        } catch (_: Exception) {
            false
        }
    }

    fun url(): String = "http://127.0.0.1:$port/"

    fun stop() {
        running.set(false)
        try {
            server?.close()
        } catch (_: Exception) {
        }
    }

    private fun handle(socket: Socket) {
        socket.use {
            val input = BufferedReader(InputStreamReader(socket.getInputStream()))
            val requestLine = input.readLine() ?: return
            val parts = requestLine.split(" ")
            if (parts.size < 2 || parts[0] != "GET") {
                writeResponse(socket, 405, "text/plain", "Method not allowed".toByteArray())
                return
            }

            val rawPath = parts[1].substringBefore("?")
            val decodedPath = URLDecoder.decode(rawPath, Charsets.UTF_8.name()).trimStart('/')
            if (decodedPath == "config.js") {
                val escapedApiUrl = apiUrl.replace("\\", "\\\\").replace("\"", "\\\"")
                val body =
                    "window.__FAIRFARM_CONFIG__ = { API_URL: \"$escapedApiUrl\" };"
                writeResponse(socket, 200, "application/javascript; charset=utf-8", body.toByteArray())
                return
            }

            val assetPath = decodedPath.ifBlank { "index.html" }
            val bytes = readAsset(assetPath)
            if (bytes != null) {
                writeResponse(socket, 200, contentType(assetPath), bytes)
                return
            }

            val indexBytes = readAsset("index.html")
            if (indexBytes != null) {
                writeResponse(socket, 200, "text/html; charset=utf-8", indexBytes)
            } else {
                writeResponse(
                    socket,
                    404,
                    "text/html; charset=utf-8",
                    "<h1>FairFarm assets missing</h1><p>Rebuild the Android application project.</p>".toByteArray()
                )
            }
        }
    }

    private fun readAsset(path: String): ByteArray? {
        val safePath = path.replace("..", "")
        return try {
            context.assets.open("fairfarm/$safePath").use { it.readBytes() }
        } catch (_: Exception) {
            null
        }
    }

    private fun writeResponse(
        socket: Socket,
        status: Int,
        contentType: String,
        body: ByteArray
    ) {
        val statusText = if (status == 200) "OK" else if (status == 405) "Method Not Allowed" else "Not Found"
        val headers =
            "HTTP/1.1 $status $statusText\r\n" +
                "Content-Type: $contentType\r\n" +
                "Content-Length: ${body.size}\r\n" +
                "Cache-Control: no-cache\r\n" +
                "X-Content-Type-Options: nosniff\r\n" +
                "Connection: close\r\n\r\n"
        socket.getOutputStream().write(headers.toByteArray())
        socket.getOutputStream().write(body)
        socket.getOutputStream().flush()
    }

    private fun contentType(path: String): String =
        when (path.substringAfterLast('.', "").lowercase()) {
            "html" -> "text/html; charset=utf-8"
            "js" -> "application/javascript; charset=utf-8"
            "css" -> "text/css; charset=utf-8"
            "json" -> "application/json; charset=utf-8"
            "svg" -> "image/svg+xml"
            "png" -> "image/png"
            "jpg", "jpeg" -> "image/jpeg"
            "ico" -> "image/x-icon"
            "woff" -> "font/woff"
            "woff2" -> "font/woff2"
            "ttf" -> "font/ttf"
            else -> "application/octet-stream"
        }
}
