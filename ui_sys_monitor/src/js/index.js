let intervalId = null; // để lưu interval

async function loadSystemInfo() {
  try {
    // const apiUrl = document.getElementById("api_input").value;
    const apiUrl = "http://127.0.0.1:5050/"
    if (!apiUrl) return; // nếu chưa nhập thì bỏ qua

    const res = await fetch(apiUrl);
    const data = await res.json();
    console.log(data)

    document.getElementById("os_name").textContent = `${data["system"]["os_name"]}`;
    document.getElementById("api_out").textContent = apiUrl;
    document.getElementById("os_version").textContent = `${data["system"]["os_version"]}`;
    document.getElementById("uptime").textContent = `${data["system"]["uptime_seconds"]}`;
    document.getElementById("api_status").textContent = "Connected";
    document.getElementById("api_status").classList.remove("text-red-500");
    document.getElementById("api_status").classList.add("text-green-500");
    document.getElementById("remote").textContent = "on";

    // fake data system monitor
    document.getElementById("cpu").textContent = `${data["cpu"]["cpu_used"]}%`;
    document.getElementById("memory").textContent = `${data["memory"]["ram_percent"]}%`;
    document.getElementById("disk").textContent = `${data["disk"]["disk_sum"]["disk_sum_percent"]}%`;
    document.getElementById("network").textContent = "120 KB/s";

  } catch (err) {
    console.error(err);
    document.getElementById("api_status").textContent = "Error";
    document.getElementById("api_status").classList.remove("text-green-500");
    document.getElementById("api_status").classList.add("text-red-500");
  }
}

// clear interval cũ nếu có
if (intervalId) clearInterval(intervalId);

// gọi ngay lần đầu
loadSystemInfo();

// gọi lại mỗi 1 giây
intervalId = setInterval(loadSystemInfo, 2500);

console.log(intervalId)