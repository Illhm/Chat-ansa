import os
import requests
from flask import Flask, render_template_string, jsonify, request

app = Flask(__name__)

BASE_API_URL = "https://animeku.my.id/nontonanime-x/phalcon/api"
V77_API_URL = "https://animeku.my.id/nontonanime-v77/phalcon/api"

DEFAULT_PARAMS = {
    "isAPKvalid": "true",
    "device_id": "610da07cf6e863e4",
    "device_token": "610da07cf6e863e4"
}
HEADERS = {
    "User-Agent": "okhttp/4.9.2"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AnsaStream Proxy</title>
    <style>
        body { background-color: #121212; color: #fff; font-family: sans-serif; margin: 0; padding: 0; }
        header { background-color: #1f1f1f; padding: 20px; text-align: center; border-bottom: 3px solid #e50914; }
        h1 { margin: 0; color: #e50914; cursor: pointer; }
        .container { display: flex; flex-direction: row; margin: 20px auto; max-width: 1200px; gap: 20px; padding: 0 20px; }
        @media (max-width: 800px) { .container { flex-direction: column; } }

        .player-section { flex: 3; display: none; }
        .video-container { background: #000; border-radius: 10px; overflow: hidden; width: 100%; aspect-ratio: 16/9; margin-bottom: 20px;}
        video { width: 100%; height: 100%; }
        .video-info { background: #1f1f1f; padding: 20px; border-radius: 10px; margin-bottom: 20px; }

        .anime-grid { flex: 3; display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; }
        .anime-card { background: #1f1f1f; border-radius: 8px; overflow: hidden; cursor: pointer; transition: transform 0.2s; }
        .anime-card:hover { transform: scale(1.05); border: 1px solid #e50914; }
        .anime-card img { width: 100%; height: 280px; object-fit: cover; }
        .anime-card .title { padding: 10px; font-size: 0.9em; text-align: center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

        .sidebar { flex: 1; background: #1f1f1f; border-radius: 10px; padding: 15px; max-height: 800px; overflow-y: auto; }
        .ep-list { list-style: none; padding: 0; margin: 0; }
        .ep-item { background: #2a2a2a; margin-bottom: 8px; padding: 10px; border-radius: 5px; cursor: pointer; font-size: 0.9em;}
        .ep-item:hover { background: #e50914; }
        .ep-item.active { background: #e50914; font-weight: bold; }

        .loader { text-align: center; padding: 20px; display: none; color: #e50914; }

        #back-btn { background: #333; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; margin-bottom: 15px; display: none; }
        #back-btn:hover { background: #555; }

        .resolutions { display: flex; gap: 10px; margin-top: 10px; }
        .res-btn { background: #333; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer; }
        .res-btn.active { background: #e50914; }
    </style>
</head>
<body>

    <header>
        <h1 onclick="loadHome()">AnsaStream</h1>
    </header>

    <div class="container">
        <div style="flex: 3; display: flex; flex-direction: column;">
            <button id="back-btn" onclick="loadHome()">← Kembali ke Beranda</button>

            <div id="loader" class="loader">Loading bro... tunggu bentar...</div>

            <!-- Fake Data untuk grid biar web ga kosong kalo server aslinya lagi nge-block page -->
            <div id="anime-grid" class="anime-grid"></div>

            <div id="player-section" class="player-section">
                <div class="video-container">
                    <video id="video-player" controls controlsList="nodownload">
                        <source id="video-source" src="" type="video/mp4">
                        Browser lu gak support HTML5 video bro.
                    </video>
                </div>
                <div class="video-info">
                    <h2 id="video-title">Pilih episode dulu</h2>
                    <div id="video-desc" style="font-size: 0.9em; color: #ccc; margin-top: 10px; max-height: 150px; overflow-y: auto;"></div>
                    <div class="resolutions" id="res-container"></div>
                </div>
            </div>
        </div>

        <div class="sidebar" id="sidebar">
            <h3 id="sidebar-title">Anime Terbaru</h3>
            <ul class="ep-list" id="sidebar-list">
            </ul>
        </div>
    </div>

    <script>
        const API_BASE = '/api';

        // Data backup yang kita tau dari HAR file.
        // Biar app nya ga kosong melompong gara-gara API animeku ngubah param nya pas kita live run.
        const backupPosts = [
            { category_id: 2482, category_name: "Jujutsu Kaisen Season 3 Part 1", img_url: "https://cdn.myanimelist.net/images/anime/1180/153379l.jpg", channel_name: "Jujutsu Kaisen S3 Part 1" },
            { category_id: 2480, category_name: "Omae Gotoki ga Maou ni Kateru to Omouna", img_url: "https://cdn.myanimelist.net/images/anime/1360/153435l.jpg", channel_name: "Omae Gotoki ga Maou ni" },
            { category_id: 2464, category_name: "Yuusha-kei ni Shosu Choubatsu Yuusha", img_url: "https://cdn.myanimelist.net/images/anime/1062/151911l.jpg", channel_name: "Yuusha-kei ni Shosu" },
            { category_id: 2479, category_name: "Mato Seihei no Slave 2", img_url: "https://cdn.myanimelist.net/images/anime/1668/148737l.jpg", channel_name: "Mato Seihei no Slave 2" },
            { category_id: 2493, category_name: "Oshi no Ko Season 3", img_url: "https://cdn.myanimelist.net/images/anime/1979/153329l.jpg", channel_name: "Oshi no Ko Season 3" }
        ];

        async function fetchAPI(endpoint, data = {}) {
            document.getElementById('loader').style.display = 'block';
            try {
                const fd = new URLSearchParams();
                for (const key in data) { fd.append(key, data[key]); }

                const res = await fetch(`${API_BASE}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: fd
                });
                return await res.json();
            } catch (err) {
                console.error(err);
                return { status: 'error' };
            } finally {
                document.getElementById('loader').style.display = 'none';
            }
        }

        async function loadHome() {
            document.getElementById('anime-grid').style.display = 'grid';
            document.getElementById('player-section').style.display = 'none';
            document.getElementById('back-btn').style.display = 'none';
            document.getElementById('sidebar-title').innerText = 'Anime Terbaru';
            document.getElementById('sidebar-list').innerHTML = '';

            const data = await fetchAPI('/get_posts', { page: 1, count: 24 });
            let posts = backupPosts;

            // Pake live API kalo ada, kalo ngga pake backup aja dari file HAR
            if(data && data.posts && data.posts.length > 0) {
                posts = data.posts;
            }

            renderAnimeGrid(posts);
            renderSidebarHome(posts);
        }

        function renderAnimeGrid(posts) {
            const grid = document.getElementById('anime-grid');
            grid.innerHTML = '';
            const uniquePosts = new Map();
            posts.forEach(p => {
                if(!uniquePosts.has(p.category_id)) {
                    uniquePosts.set(p.category_id, p);
                }
            });

            uniquePosts.forEach(post => {
                const card = document.createElement('div');
                card.className = 'anime-card';
                card.onclick = () => loadAnime(post.category_id, post.category_name);

                let imgUrl = post.img_url;
                if(imgUrl && imgUrl.includes('\\/')) imgUrl = imgUrl.replace(/\\\//g, '/');

                card.innerHTML = `
                    <img src="${imgUrl}" alt="${post.category_name}" onerror="this.src='https://via.placeholder.com/200x280?text=No+Image'">
                    <div class="title">${post.category_name}</div>
                `;
                grid.appendChild(card);
            });
        }

        function renderSidebarHome(posts) {
            const list = document.getElementById('sidebar-list');
            posts.slice(0, 15).forEach(post => {
                const li = document.createElement('li');
                li.className = 'ep-item';
                li.innerText = post.channel_name || post.category_name;
                li.onclick = () => loadAnime(post.category_id, post.category_name);
                list.appendChild(li);
            });
        }

        async function loadAnime(categoryId, categoryName) {
            document.getElementById('anime-grid').style.display = 'none';
            document.getElementById('player-section').style.display = 'block';
            document.getElementById('back-btn').style.display = 'block';
            document.getElementById('sidebar-title').innerText = categoryName;

            const list = document.getElementById('sidebar-list');
            list.innerHTML = '<li style="padding:10px;">Loading episodes...</li>';

            const data = await fetchAPI('/get_category_posts', { id: categoryId });
            if(data && data.posts && data.posts.length > 0) {
                list.innerHTML = '';
                const sortedPosts = data.posts.sort((a,b) => a.channel_name.localeCompare(b.channel_name));

                sortedPosts.forEach((ep, index) => {
                    const li = document.createElement('li');
                    li.className = 'ep-item';
                    li.innerText = ep.channel_name;
                    li.onclick = (e) => loadEpisode(ep.channel_id, e.target);
                    list.appendChild(li);

                    if(index === 0) li.click();
                });
            } else {
                 list.innerHTML = '<li style="padding:10px;">Gak ada episode / Server di block.</li>';
            }
        }

        async function loadEpisode(channelId, element) {
            document.querySelectorAll('.ep-item').forEach(el => el.classList.remove('active'));
            if(element) element.classList.add('active');

            document.getElementById('video-title').innerText = "Loading data stream...";

            const data = await fetchAPI('/get_post_description', { channel_id: channelId });
            if(data && data.status === 'ok') {
                document.getElementById('video-title').innerText = data.channel_name;
                document.getElementById('video-desc').innerHTML = data.channel_description || 'Tidak ada deskripsi.';
                renderResolutions(data);
            } else {
                document.getElementById('video-title').innerText = "Gagal load data stream.";
            }
        }

        function renderResolutions(data) {
            const container = document.getElementById('res-container');
            container.innerHTML = '<span>Resolusi: </span>';

            const qualities = [
                { id: 'fhd', name: '1080p (FHD)', url: data.channel_url_fhd },
                { id: 'hd', name: '720p (HD)', url: data.channel_url_hd },
                { id: 'sd', name: '480p (SD)', url: data.channel_url }
            ];

            let firstAvail = null;

            qualities.forEach(q => {
                if(q.url && q.url.trim() !== '' && q.url !== '#') {
                    const btn = document.createElement('button');
                    btn.className = 'res-btn';
                    btn.innerText = q.name;
                    btn.onclick = (e) => {
                        document.querySelectorAll('.res-btn').forEach(b => b.classList.remove('active'));
                        e.target.classList.add('active');
                        playStream(q.url);
                    };
                    container.appendChild(btn);

                    if(!firstAvail) firstAvail = btn;
                }
            });

            if(firstAvail) {
                firstAvail.click();
            } else {
                 document.getElementById('video-title').innerText += " (Video ga tersedia)";
            }
        }

        function playStream(url) {
            if(url.includes('\\/')) url = url.replace(/\\\//g, '/');

            const player = document.getElementById('video-player');
            const source = document.getElementById('video-source');

            source.src = `/proxy_video?url=${encodeURIComponent(url)}`;
            player.load();
            player.play().catch(e => console.log("Autoplay dicegah browser", e));
        }

        window.onload = loadHome;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/get_posts', methods=['POST'])
def api_get_posts():
    data = DEFAULT_PARAMS.copy()
    data['page'] = request.form.get('page', '1')
    data['count'] = request.form.get('count', '24')
    try:
        r = requests.post(f"{BASE_API_URL}/get_posts/", data=data, headers=HEADERS)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/get_category_posts', methods=['POST'])
def api_get_category_posts():
    data = DEFAULT_PARAMS.copy()
    data['id'] = request.form.get('id')
    try:
        r = requests.post(f"{V77_API_URL}/get_category_posts_secure/v9_1/", data=data, headers=HEADERS)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/api/get_post_description', methods=['POST'])
def api_get_post_description():
    data = DEFAULT_PARAMS.copy()
    data['channel_id'] = request.form.get('channel_id')
    try:
        r = requests.post(f"{BASE_API_URL}/get_post_description/", data=data, headers=HEADERS)
        return jsonify(r.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/proxy_video')
def proxy_video():
    video_url = request.args.get('url')
    if not video_url:
        return "No URL", 400

    req_headers = {"User-Agent": HEADERS["User-Agent"]}
    range_header = request.headers.get('Range', None)
    if range_header:
        req_headers['Range'] = range_header

    try:
        r = requests.get(video_url, headers=req_headers, stream=True)
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in r.raw.headers.items()
                   if name.lower() not in excluded_headers]

        if 'content-length' in r.headers:
            headers.append(('Content-Length', r.headers['content-length']))

        return app.response_class(r.iter_content(chunk_size=1024*1024), status=r.status_code, headers=headers)
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
