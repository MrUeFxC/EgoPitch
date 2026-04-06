import os
import urllib.request

stars_data = [
    {   "id": "messi", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Lionel-Messi-Argentina-2022-FIFA-World-Cup_%28cropped%29.jpg/220px-Lionel-Messi-Argentina-2022-FIFA-World-Cup_%28cropped%29.jpg" },
    {   "id": "mbappe", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Kylian_Mbapp%C3%A9_2022_%28cropped%29.jpg/220px-Kylian_Mbapp%C3%A9_2022_%28cropped%29.jpg" },
    {   "id": "haaland", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Erling_Haaland_2023_%28cropped%29.jpg/220px-Erling_Haaland_2023_%28cropped%29.jpg" },
    {   "id": "neymar", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Neymar_Jr_Team_Brasil_2018_%28cropped%29.jpg/220px-Neymar_Jr_Team_Brasil_2018_%28cropped%29.jpg" },
    {   "id": "kdb", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Kevin_De_Bruyne_2018_%28cropped%29.jpg/220px-Kevin_De_Bruyne_2018_%28cropped%29.jpg" },
    {   "id": "vini", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Vinicius_Junior_2022.jpg/220px-Vinicius_Junior_2022.jpg" },
    {   "id": "bellingham", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Jude_Bellingham_2022_%28cropped%29.jpg/220px-Jude_Bellingham_2022_%28cropped%29.jpg" },
    {   "id": "kane", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Harry_Kane_2021.jpg/220px-Harry_Kane_2021.jpg" },
    {   "id": "lewa", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Robert_Lewandowski_2022_%28cropped%29.jpg/220px-Robert_Lewandowski_2022_%28cropped%29.jpg" },
    {   "id": "salah", "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Mohamed_Salah_2018.jpg/220px-Mohamed_Salah_2018.jpg" }
]

static_dir = r"d:\Users\REX\VscodeProjects\EgoPitch\static\avatars"
os.makedirs(static_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for star in stars_data:
    url = star.get("image_url")
    save_path = os.path.join(static_dir, f"{star['id']}.jpg")
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            with open(save_path, 'wb') as out_file:
                out_file.write(response.read())
        print(f"Downloaded {star['id']}.jpg")
    except Exception as e:
        print(f"Failed to download {star['id']}: {e}")
