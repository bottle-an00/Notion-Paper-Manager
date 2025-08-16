<div align="center">
  <div style="
    width: 180px; height: 180px;
    border: 4px solid #e5e7eb;      
    border-radius: 50%;              
    overflow: hidden;                 
    display: inline-block;">
    <img src="image/avatar.png" alt="Notion Paper Manager avatar"
         style="width:100%; height:100%; object-fit:cover;">
  </div>
</div>

# 📘 Notion Paper Manager

A tool for efficiently organizing research papers.  
It extracts metadata (title, authors, year, figures, tables, etc.) from **Arxiv** or **PDF files** and automatically uploads them to a Notion database. 

---

## <br>🌟 Features
- Extract metadata (title, authors, year) from **Arxiv ID** or **PDF file**  
- Use **[Docling](https://github.com/docling-project/docling)** to automatically extract figures and tables  
- Integrates with **Notion Database API** → creates paper entries and image blocks automatically  
- Helps researchers skim and organize papers more effectively  

---

## 

<br>

## <i class="fa-brands fa-notion"></i> Notion Database Setting

### 1. Create `Database`

![make Database](../bottle-an00.github.io/assets/images/README/create_Database_Fullpage.png)

Create block with `Database - Full page` 

![Database made](../bottle-an00.github.io/assets/images/README/Database made.png)

<BR>

### 2. Set `Database Properties`

``` yaml
properties:
    title: "Title"
    year: "Year"
    url: "URL"
    rich_text: "Authors"
    checkbox: "Inbox"
    file: "PDF"
    select: "Status"
```

<BR>

### 3. Create an integration and connect it to your database.

[Create a Notion Integration](https://developers.notion.com/docs/create-a-notion-integration) 

![createIntegration](../bottle-an00.github.io/assets/images/README/create Integration.png)



![IntegrationSetting](../bottle-an00.github.io/assets/images/README/Integrationsetting.png)

- Connect `Integration` to your `Database`

![connectIntegration](../bottle-an00.github.io/assets/images/README/connectIntegration.png)

<BR>

### 4. Get Notion Token and Database ID 

- get notion token

![getnotiontoken](../bottle-an00.github.io/assets/images/README/Integration_secret.png)

- get Database ID

![getdatabaseID](../bottle-an00.github.io/assets/images/README/getDatabaseID.png)

The copied link looks like `https://www.notion.so/{your_database_id}?v=...`

<br>

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/<USERNAME>/Notion-Paper-Manager.git
cd Notion-Paper-Manager
```

### <br>2. Install dependencies
```bash
pip install -r requirements.txt
```

### <br>

### 3. Set enviornment variables 

Create a `.env` file in the project root directory

```env
NOTION_TOKEN=your_notion_api_key
NOTION_DATABASE_ID=your_database_id

WORKDIR_DATA=data
WORKDIR_OUTPUT=output
```

### <br>4. Run

- Register paper by Arxiv ID.

```bash
python main.py --arxiv-id <arxiv_id> --extract-figures --add-to-notion --device cuda
```

- Register paper by PDF file.

```bash
python main.py --pdf <your pdf dir> --extract-figures --add-to-notion --device cuda
```

- Running on CPU is possible, but it may take a long time.

```bash
pthon main.py --arxiv-id <arxiv_id> --extract-figures --add-to-notion --device cpu
```



## <br>😚 Result

![](../bottle-an00.github.io/assets/images/README/RESULT.png)

<br>

## ✔️ TODO

- [ ] Extract mathematical formulas from PDFs
- [ ] Provide a simple GUI interface
- [ ] Uploading files > 5MB with Google Drive API