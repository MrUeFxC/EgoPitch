import subprocess
import time

stars = [
    ("messi", "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/Lionel-Messi-Argentina-2022-FIFA-World-Cup_%28cropped%29.jpg/220px-Lionel-Messi-Argentina-2022-FIFA-World-Cup_%28cropped%29.jpg"),
    ("mbappe", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Kylian_Mbapp%C3%A9_2022_%28cropped%29.jpg/220px-Kylian_Mbapp%C3%A9_2022_%28cropped%29.jpg"),
    ("haaland", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Erling_Haaland_2023_%28cropped%29.jpg/220px-Erling_Haaland_2023_%28cropped%29.jpg"),
    ("neymar", "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/Neymar_Jr_Team_Brasil_2018_%28cropped%29.jpg/220px-Neymar_Jr_Team_Brasil_2018_%28cropped%29.jpg"),
    ("kdb", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Kevin_De_Bruyne_2018_%28cropped%29.jpg/220px-Kevin_De_Bruyne_2018_%28cropped%29.jpg"),
    ("vini", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Vinicius_Junior_2022.jpg/220px-Vinicius_Junior_2022.jpg"),
    ("bellingham", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cd/Jude_Bellingham_2022_%28cropped%29.jpg/220px-Jude_Bellingham_2022_%28cropped%29.jpg"),
    ("kane", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Harry_Kane_2021.jpg/220px-Harry_Kane_2021.jpg"),
    ("lewa", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ca/Robert_Lewandowski_2022_%28cropped%29.jpg/220px-Robert_Lewandowski_2022_%28cropped%29.jpg"),
    ("salah", "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Mohamed_Salah_2018.jpg/220px-Mohamed_Salah_2018.jpg")
]

for star_id, url in stars:
    filepath = rf"d:\Users\REX\VscodeProjects\EgoPitch\static\avatars\{star_id}.jpg"
    cmd = [
        "curl", "-s", "-L",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "-o", filepath,
        url
    ]
    subprocess.run(cmd)
    print(f"Downloaded {star_id}")
    time.sleep(1)
