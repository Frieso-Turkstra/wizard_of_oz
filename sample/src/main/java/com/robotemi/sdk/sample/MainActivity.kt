package com.robotemi.sdk.sample

import android.Manifest
import android.annotation.SuppressLint
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.View
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.robotemi.sdk.*
import com.robotemi.sdk.Robot.*
import com.robotemi.sdk.Robot.Companion.getInstance
import com.robotemi.sdk.TtsRequest.Companion.create
import com.robotemi.sdk.constants.*
import com.robotemi.sdk.listeners.*
import com.robotemi.sdk.navigation.model.SpeedLevel
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.android.synthetic.main.group_app_and_permission.*
import kotlinx.android.synthetic.main.group_buttons.*
import kotlinx.android.synthetic.main.group_map_and_movement.*
import kotlinx.android.synthetic.main.group_resources.*
import kotlinx.android.synthetic.main.group_settings_and_status.*
import java.io.IOException
import java.util.*
import java.util.concurrent.Executors

// Camera
import androidx.camera.core.CameraSelector
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import java.util.concurrent.ExecutorService

// Server
import okhttp3.*
import org.json.JSONObject
import kotlinx.coroutines.*


class MainActivity : AppCompatActivity() {

    private lateinit var robot: Robot

    // Camera
    private lateinit var viewFinder: PreviewView
    private lateinit var cameraExecutor: ExecutorService

    // Server poller
    private var serverUrl: String = "[enter your serverUrl here]"
    private lateinit var stateMonitor: Job // Job for managing the coroutine lifecycle for state updates

    // Display icon
    private lateinit var textOverlay: TextView

    //-----PREVIEW----------------------------------------------------------------------------------

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            // CameraProvider
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()

            // Preview
            val preview = Preview.Builder()
                .build()
                .also {
                    it.setSurfaceProvider(viewFinder.surfaceProvider)
                }

            // Select front camera as a default
            val cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA

            try {
                // Unbind use cases before rebinding
                cameraProvider.unbindAll()

                // Bind use cases to camera
                cameraProvider.bindToLifecycle(
                    this, cameraSelector, preview)
            } catch (exc: Exception) {
                // Handle any errors (e.g., CameraAccessException)
                println("Use case binding failed ${exc.message}")
            }
        }, ContextCompat.getMainExecutor(this))
    }

    //-----PERMISSIONS------------------------------------------------------------------------------
    companion object {
        private const val REQUEST_CODE_CAMERA = 10
        private val REQUIRED_PERMISSIONS = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO,
            Manifest.permission.WRITE_EXTERNAL_STORAGE,
            Manifest.permission.READ_EXTERNAL_STORAGE
        )
    }

    private fun requestPermissions() {
        if (!hasPermissions()) {
            requestPermissions(REQUIRED_PERMISSIONS, REQUEST_CODE_CAMERA)
        } else {
            startCamera()
        }
    }

    private fun hasPermissions() = REQUIRED_PERMISSIONS.all {
        checkSelfPermission(it) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == REQUEST_CODE_CAMERA) {
            if (grantResults.isNotEmpty() && grantResults.all { it == PackageManager.PERMISSION_GRANTED }) {
                // All permissions have been granted
                startCamera()
            } else {
                // Permissions were denied. Handle the failure to obtain permission.
                Toast.makeText(this, "Permissions not granted by the user.", Toast.LENGTH_SHORT).show()
            }
        }
    }

    //-----EVENT HANDLERS---------------------------------------------------------------------------
    private fun fetchCurrentState() {
        val client = OkHttpClient()
        val url = "$serverUrl/get-current-state"

        val request = Request.Builder()
            .url(url)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                // Handle the error
                e.printStackTrace()
            }

            override fun onResponse(call: Call, response: Response) {
                response.use {
                    if (!response.isSuccessful) {
                        throw IOException("Unexpected code $response")
                    }

                    // Assuming the server response is JSON
                    val jsonString = response.body?.string()

                    // Make sure to check if the jsonString is not null
                    jsonString?.let {
                        JSONObject(it).apply {
                            handleSpeech(getString("wizard_speech"))
                            handleLocation(getString("location"))
                            handleIcon(getBoolean("listening"), getBoolean("thinking"))
                            handleVolume(getString("volume"))
                            handleKeys(getJSONObject("keys"))
                        }
                    }
                }
            }
        })
    }

    private fun handleKeys(keyStates: JSONObject) {
        val keyCtrl = keyStates.getBoolean("Key.ctrl_l") || keyStates.getBoolean("Key.ctrl_r")
        val keyAlt = keyStates.getBoolean("Key.alt_l") || keyStates.getBoolean("Key.alt_r")
        var x = 0f
        var y = 0f
        var degrees = 0
        if (keyStates.getBoolean("Key.left")) {
            y = -0.8f // switched around because camera view for wizard flips the movement
        }
        if (keyStates.getBoolean("Key.right")) {
            y = 0.8f // switched around because camera view for wizard flips the movement
        }
        if (keyStates.getBoolean("Key.up") && !keyCtrl) {
            x = 0.3f
        }
        if (keyStates.getBoolean("Key.down") && !keyCtrl) {
            x = -0.3f
        }
        if (keyStates.getBoolean("Key.up") && keyCtrl) {
            degrees = 7
        }
        if (keyStates.getBoolean("Key.down") && keyCtrl) {
            degrees = -7
        }
        if (keyAlt) {
            robot.stopMovement()
        }
        else {
            if (x != 0f || y != 0f) {
                robot.skidJoy(x, y)
            }
            if (degrees != 0) {
                robot.tiltBy(degrees, 1f)
            }
        }
    }

    private fun handleVolume(value: String) {
        val volume = value.toIntOrNull() ?: -1
        if (volume >= 0) {
            robot.volume = volume
        }
    }
    private fun handleIcon(listening: Boolean, thinking: Boolean) {
        if (listening) {
            runOnUiThread {
                textOverlay.text = "I am listening..."
                textOverlay.visibility = View.VISIBLE
            }
        }
        else if (thinking) {
            runOnUiThread {
                textOverlay.text = "I am thinking..."
                textOverlay.visibility = View.VISIBLE
            }
        }
        else {
            runOnUiThread {
                textOverlay.visibility = View.INVISIBLE
            }
        }
    }

    private fun handleSpeech(message: String) {
        if (message.isNotEmpty()) {
            robot.speak(create(message, false))
        }
    }

    private fun handleLocation(location: String) {
        for (loc in robot.locations) {
            if (loc == location.lowercase().trim { it <= ' ' }) {
                robot.goTo(
                    location.lowercase().trim { it <= ' ' },
                    backwards = false,
                    noBypass = false,
                    speedLevel = SpeedLevel.SLOW
                )
            }
        }
    }

    @SuppressLint("SetTextI18n")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        textOverlay = findViewById(R.id.textOverlay)
        robot = getInstance()

        // Camera
        viewFinder = findViewById(R.id.viewFinder)
        cameraExecutor = Executors.newSingleThreadExecutor()
        requestPermissions()

        // Server
        stateMonitor = CoroutineScope(Dispatchers.IO).launch {
            while (isActive) {  // Runs as long as this coroutine is active
                fetchCurrentState()
                delay(50)  // Wait for X milliseconds before sending the next request
            }
        }
    }

    override fun onStop() {
        robot.stopMovement()
        super.onStop()
    }

    override fun onDestroy() {
        cameraExecutor.shutdown()
        stateMonitor.cancel()
        super.onDestroy()
    }
}
